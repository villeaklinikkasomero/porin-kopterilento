"""porikit on Modal (modal.com): GPU jobs without servers.

  modal deploy pipeline/modal_app.py                                   # once (and after code changes)
  modal run pipeline/modal_app.py --queue bake --body '{"zones": ["tori0"]}'   # queue a task; the GPU worker starts at once
  modal run pipeline/modal_app.py --cmd "bake tori0 tori3"             # one job right now, waiting for it in the terminal
  modal volume put pori-data <local> <remote>   /   modal volume get pori-data results/<date> night/

Storage is the Modal Volume 'pori-data' (replaces S3): data/ (Blender data bundle), photos/, queue/, results/<date>/.\nWork runs continuously: queued tasks start at once on one GPU machine, which stops when the queue is empty.
Jobs run in the EU region (region selection costs more than 'anywhere', but keeps the city's photos in the EU).
"""
from __future__ import annotations
import datetime, json, os, shlex, subprocess, time
from pathlib import Path
import modal

ROOT = Path(__file__).resolve().parent.parent          # repository root (game files + blender/ + pipeline/)
REGION = os.environ.get('PORI_REGION', 'eu')
GPU = os.environ.get('PORI_GPU_TYPE', 'L4')             # 24 GB, RTX-class: Cycles OptiX works

image = (
    modal.Image.debian_slim(python_version='3.13')
    .apt_install('ca-certificates', 'wget', 'gnupg', 'nodejs', 'npm', 'fonts-dejavu-core', 'libgl1', 'libegl1', 'libglib2.0-0', 'libxrender1',
                 'libxi6', 'libxkbcommon0', 'libsm6', 'libxxf86vm1', 'libxfixes3', 'libxext6', 'libx11-6')
    .run_commands('wget -q -O /tmp/chrome.deb https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb'
                  ' && apt-get update && apt-get install -y --no-install-recommends /tmp/chrome.deb && rm /tmp/chrome.deb',
                  'mkdir -p /opt/node && cd /opt/node && npm init -y >/dev/null && npm install --omit=dev puppeteer-core@25 >/dev/null')
    .pip_install_from_requirements(str(ROOT / 'pipeline' / 'requirements.txt'))
    .env({'NVIDIA_DRIVER_CAPABILITIES': 'all', 'PORI_REPO': '/repo', 'PORI_HOME': '/home/claude', 'PORI_GAME': '/repo',
          'PORI_VOLUME': '/vol', 'PORI_GPU': '1', 'PYTHONPATH': '/repo/pipeline', 'PYTHONUNBUFFERED': '1'})
    # the repository is added last so that code changes do not rebuild the heavy layers above
    .add_local_dir(str(ROOT), '/repo', copy=True, ignore=['.git', '**/__pycache__', 'photos', 'work', 'night', '**/*– kopio*', 'pipeline/porikit/node_modules'])
    .run_commands('ln -sfn /opt/node/node_modules /repo/pipeline/porikit/node_modules')
)
vol = modal.Volume.from_name('pori-data', create_if_missing=True)
app = modal.App('porikit', image=image)
common = dict(gpu=GPU, volumes={'/vol': vol}, region=REGION, timeout=8 * 3600, retries=modal.Retries(max_retries=2, initial_delay=30.0))


@app.function(max_containers=1, **common)
def worker():
    """Works through queue/ until it is empty, then the GPU machine stops (billing is per second, so 'now' costs the same as 'at night').
    max_containers=1: one GPU machine at a time; extra calls simply find the queue empty and end within seconds."""
    from porikit import jobs
    while True:
        vol.reload()
        if not jobs.q_keys(): break
        try: jobs.night()
        finally: vol.commit()


@app.function(schedule=modal.Period(hours=1), volumes={'/vol': vol}, region=REGION)
def sweep():
    """Hourly safety net on a CPU container: if anything is waiting in the queue, start the GPU worker."""
    from porikit import jobs
    vol.reload()
    if jobs.q_keys(): worker.spawn()


@app.function(**common)
def task(cmd: str):
    """One porikit command right away, e.g. 'bake tori0 tori3 --samples 64'. Changed game files go to results/<date>/game."""
    from porikit import jobs
    vol.reload(); t0 = time.time()
    jobs.layout()
    r = subprocess.run(['python3', '-m', 'porikit.cli', *shlex.split(cmd)], cwd='/repo')
    day = datetime.date.today().isoformat()
    n = jobs.sync_up(jobs.REPO, f'results/{day}/game', 'bl_*.js', newer_than=t0)
    jobs.put_text(f"results/{day}/{time.strftime('%H%M%S')}-task.status.json",
                  json.dumps({'task': {'kind': 'task', 'cmd': cmd}, 'status': 'ok' if r.returncode == 0 else f'failed ({r.returncode})', 'seconds': round(time.time() - t0)}))
    vol.commit(); print('changed game files:', n)
    return r.returncode


@app.function(gpu=GPU, volumes={'/vol': vol}, region=REGION, timeout=3600, max_containers=10, retries=modal.Retries(max_retries=1, initial_delay=10.0))
def city_zone(name: str, samples: int = 64, day: str = ''):
    """Bake one automatically split city block (blender/city.py) on its own GPU; up to 10 run side by side."""
    from porikit import jobs
    t0 = time.time(); jobs.layout()
    env = dict(os.environ, PORI_ATLAS='4096', PORI_PHS='/repo/phs.json')
    r = subprocess.run(['python3', '/home/claude/city.py', name, str(samples)], cwd='/home/claude', env=env, capture_output=True, text=True)
    src = Path('/home/claude/out') / f'bl_{name}.js'; ok = r.returncode == 0 and src.exists()
    if ok:
        dst = Path('/vol/results') / day / 'game' / f'bl_{name}.js'; dst.parent.mkdir(parents=True, exist_ok=True); dst.write_bytes(src.read_bytes())
    else: print(r.stdout[-3000:], r.stderr[-3000:])
    vol.commit()
    return name, ok, round(time.time() - t0)


@app.function(volumes={'/vol': vol}, region=REGION, timeout=6 * 3600, is_generator=True)
def city(samples: int = 64, only: str = ''):
    """Whole-city run: every block in city_zones.json (or only the listed ones, comma separated) on up to 10 GPUs at once."""
    zones = json.loads((Path('/repo') / 'city_zones.json').read_text())['zones']
    names = [n for n in zones if not only or n in only.split(',') or (only in ('c', 'h') and n.startswith(only))]   # 'c' = apartment / commercial blocks, 'h' = houses
    day = datetime.date.today().isoformat(); t0 = time.time(); res = []
    yield f'{len(names)} blocks to bake on up to 10 GPUs'
    for out in city_zone.map(names, [samples] * len(names), [day] * len(names), return_exceptions=True, order_outputs=False):
        res.append(out if isinstance(out, tuple) else ('?', False, 0)); print(res[-1], flush=True); yield res[-1]
    good = sum(1 for r in res if r[1])
    from porikit import jobs
    jobs.put_text(f"results/{day}/{time.strftime('%H%M%S')}-city.status.json",
                  json.dumps({'task': {'kind': 'city', 'zones': len(names)}, 'status': f'{good}/{len(names)} ok', 'seconds': round(time.time() - t0),
                              'failed': [r[0] for r in res if not r[1]]}))
    vol.commit()
    yield f'done: {good}/{len(names)} ok'


@app.function(volumes={'/vol': vol}, region=REGION)
def enqueue(kind: str, body: str):
    """Add a task to the queue and start the GPU worker right away."""
    from porikit import jobs
    k = jobs.enqueue(kind, json.loads(body)); vol.commit(); worker.spawn(); return k


@app.local_entrypoint()
def main(cmd: str = '', queue: str = '', body: str = '{}'):
    print('porikit command:', repr(cmd), repr(queue), flush=True)
    if cmd.strip().lower().split()[:1] == ['city']:     # "city", "city 96" (samples), "city 64 h" (house blocks only) or "city 64 c001,c002"
        a = cmd.split(); samples = int(a[1]) if len(a) > 1 else 64; only = a[2] if len(a) > 2 else ''
        print(f'city run: samples {samples}, blocks {only or "all"}; one line per finished block follows', flush=True)
        n_ok = n_all = 0
        for out in city.remote_gen(samples, only):           # progress streams back to the terminal / GitHub Actions log
            print(out, flush=True)
            if isinstance(out, tuple) and len(out) == 3: n_all += 1; n_ok += bool(out[1])
        print('city blocks ok:', (n_ok, n_all), flush=True)
    elif queue: print('queued, the GPU worker is starting:', enqueue.remote(queue, body))
    elif cmd: print('exit code', task.remote(cmd))
    else: print(__doc__)
