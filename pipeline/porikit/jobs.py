"""Jobs that run on AWS Batch (GPU) or locally: layout, sync, export, bake, shots, night queue."""
from __future__ import annotations
import glob, json, os, shutil, subprocess, sys, time
from pathlib import Path

HOME = Path(os.environ.get('PORI_HOME', '/home/claude'))     # the layout the existing scripts expect
REPO = Path(os.environ.get('PORI_REPO', '/repo'))              # git checkout of porin-kopterilento
BUCKET = os.environ.get('PORI_BUCKET', '')                     # s3 bucket (AWS)
VOL = Path(os.environ['PORI_VOLUME']) if os.environ.get('PORI_VOLUME') else None   # mounted volume (Modal) instead of S3


# ---------------------------------------------------------------- storage
def s3():
    import boto3
    return boto3.client('s3')


def sync_down(prefix: str, dest: Path):
    """s3://bucket/prefix/** (or <volume>/prefix/**) -> dest (skips files that are already there with the same size)."""
    if VOL is not None:
        src = VOL / prefix; n = 0
        for p in (src.rglob('*') if src.exists() else []):
            if not p.is_file(): continue
            q = dest / p.relative_to(src); q.parent.mkdir(parents=True, exist_ok=True)
            if q.exists() and q.stat().st_size == p.stat().st_size: continue
            shutil.copy(p, q); n += 1
        return n
    if not BUCKET: return 0
    c = s3(); n = 0; pag = c.get_paginator('list_objects_v2')
    for page in pag.paginate(Bucket=BUCKET, Prefix=prefix.rstrip('/') + '/'):
        for o in page.get('Contents', []):
            rel = o['Key'][len(prefix.rstrip('/')) + 1:]
            if not rel or rel.endswith('/'): continue
            p = dest / rel; p.parent.mkdir(parents=True, exist_ok=True)
            if p.exists() and p.stat().st_size == o['Size']: continue
            c.download_file(BUCKET, o['Key'], str(p)); n += 1
    return n


def sync_up(src: Path, prefix: str, pattern: str = '**/*', newer_than: float = 0):
    if VOL is not None:
        n = 0
        for p in src.glob(pattern):
            if p.is_file() and p.stat().st_mtime > newer_than: q = VOL / prefix / p.relative_to(src); q.parent.mkdir(parents=True, exist_ok=True); shutil.copy(p, q); n += 1
        return n
    if not BUCKET: return 0
    c = s3(); n = 0
    for p in src.glob(pattern):
        if p.is_file() and p.stat().st_mtime > newer_than: c.upload_file(str(p), BUCKET, f"{prefix.rstrip('/')}/{p.relative_to(src)}"); n += 1
    return n


# ---------------------------------------------------------------- layout
def layout():
    """Recreate the working layout of the development workspace from the repo + the data bundle in S3."""
    HOME.mkdir(parents=True, exist_ok=True)
    for d in ('out', 'blender/out', 'mmlproc', 'data', 'photos', 'work'): (HOME / d).mkdir(parents=True, exist_ok=True)
    pori = HOME / 'pori'
    if not pori.exists(): pori.symlink_to(REPO)                  # the game files live at the repo root
    game = HOME / 'game'
    if not game.exists(): game.symlink_to(REPO)
    for f in ('gen.py', 'zones.py', 'run.py', 'run2.py', 'zones2.py', 'lib_city.py', 'gpu_hook.py'):
        src = REPO / 'blender' / f
        if src.exists(): shutil.copy(src, HOME / f)
    for f in glob.glob(str(REPO / 'blender' / '*.py')): shutil.copy(f, HOME / 'blender' / os.path.basename(f))
    for f in ('mml_city.py', 'river_build.py', 'dem_build.py', 'parse.py'):
        src = REPO / 'blender' / f
        if src.exists(): shutil.copy(src, HOME / 'mmlproc' / f)
    n = sync_down('data', HOME)                                  # mmlproc/*.pkl, river.pkl, data/*.json ... (not in git: large / licensed)
    print('layout ready, data files fetched:', n)


# ---------------------------------------------------------------- export approved facades to the game
def export(work: Path, game: Path):
    """approved.json (review tool) -> ph_<id>.jpg + phs.json in the game folder."""
    ap = json.loads((work / 'approved.json').read_text())
    phs = json.loads((game / 'phs.json').read_text()) if (game / 'phs.json').exists() else {}
    for bid, a in ap.items():
        name = f'ph_{bid}'; shutil.copy(work / a['strip'], game / f'{name}.jpg')
        phs[bid] = [{'t': name, 'bw': a['bay_m']}]
    (game / 'phs.json').write_text(json.dumps(phs, indent=1))
    print('exported', len(ap), 'facades; phs.json has', len(phs))
    return phs


# ---------------------------------------------------------------- Blender bakes on the GPU
def bake(zones: list[str], samples: int = 48, parallel: int = 1):
    """Bake block zones with Cycles. On a GPU instance PORI_GPU=1 makes gen.bake_zone use OptiX/CUDA."""
    env = dict(os.environ, PORI_GPU=os.environ.get('PORI_GPU', '1'), PORI_PHS=str(REPO / 'phs.json'))
    if zones == ['all']:
        sys.path.insert(0, str(HOME)); import importlib; zones = list(importlib.import_module('zones').ZONES)
    procs, done = [], []
    for z in zones:
        while len(procs) >= parallel:
            for p in procs[:]:
                if p[0].poll() is not None: procs.remove(p); done.append((p[1], p[0].returncode, round(time.time() - p[2])))
            time.sleep(1)
        log = open(HOME / 'out' / f'{z}.log', 'w')
        procs.append((subprocess.Popen([sys.executable, str(HOME / 'run.py'), z, str(samples)], cwd=HOME, env=env, stdout=log, stderr=subprocess.STDOUT), z, time.time()))
    for p in procs: p[0].wait(); done.append((p[1], p[0].returncode, round(time.time() - p[2])))
    for z, rc, t in done:
        src = HOME / 'out' / f'bl_{z}.js'
        if rc == 0 and src.exists(): shutil.copy(src, REPO / f'bl_{z}.js')
        print(f'{z}: {"ok" if rc == 0 else "FAILED"} {t}s')
    return done


def landmarks(names: list[str]):
    env = dict(os.environ, PORI_GPU=os.environ.get('PORI_GPU', '1'))
    for n in names:
        r = subprocess.run([sys.executable, str(HOME / 'blender' / 'lm.py'), n], cwd=HOME, env=env)
        print(n, 'ok' if r.returncode == 0 else 'FAILED')


# ---------------------------------------------------------------- screenshots of the game (headless Chrome on the GPU)
def shots(views: list, out: Path):
    out.mkdir(parents=True, exist_ok=True)
    js = Path(__file__).parent / 'shots.mjs'
    r = subprocess.run(['node', str(js), str(REPO), str(out), json.dumps(views)], check=False)
    return r.returncode


# ---------------------------------------------------------------- night queue (S3 on AWS, a mounted volume on Modal)
def q_keys():
    if VOL is not None: return sorted(str(p.relative_to(VOL)) for p in (VOL / 'queue').glob('*.json'))
    return sorted(o['Key'] for o in s3().list_objects_v2(Bucket=BUCKET, Prefix='queue/').get('Contents', []) if o['Key'].endswith('.json'))


def q_read(k):
    return json.loads((VOL / k).read_text()) if VOL is not None else json.loads(s3().get_object(Bucket=BUCKET, Key=k)['Body'].read())


def q_delete(k):
    if VOL is not None: (VOL / k).unlink(missing_ok=True)
    else: s3().delete_object(Bucket=BUCKET, Key=k)


def put_text(k, text):
    if VOL is not None: (VOL / k).parent.mkdir(parents=True, exist_ok=True); (VOL / k).write_text(text)
    else: s3().put_object(Bucket=BUCKET, Key=k, Body=text.encode())


def enqueue(kind: str, body: dict):
    k = f"queue/{time.strftime('%Y%m%d-%H%M%S')}-{kind}.json"; put_text(k, json.dumps({'kind': kind, **body})); return k


def night():
    """Run every queued task in name order; results and logs to results/<date>/ (S3 or volume)."""
    import datetime
    if VOL is None and not BUCKET: raise SystemExit('set PORI_VOLUME (Modal) or PORI_BUCKET (AWS)')
    day = datetime.date.today().isoformat(); res = HOME / 'results'; res.mkdir(parents=True, exist_ok=True)
    keys = q_keys(); t_start = time.time()
    if not keys: print('queue empty'); return
    layout()
    for k in keys:
        task = q_read(k); t0 = time.time(); print('task', k, task)
        try:
            kind = task['kind']
            if kind == 'bake': bake(task.get('zones', ['all']), task.get('samples', 48), task.get('parallel', 1))
            elif kind == 'landmarks': landmarks(task['names'])
            elif kind == 'facades': auto_facades(task.get('district'))
            elif kind == 'shots': shots(task['views'], res / 'shots')
            status = 'ok'
        except Exception as e:
            status = f'failed: {e}'
        put_text(f'results/{day}/{Path(k).stem}.status.json', json.dumps({'task': task, 'status': status, 'seconds': round(time.time() - t0)}))
        q_delete(k)
    n = sync_up(REPO, f'results/{day}/game', 'bl_*.js', newer_than=t_start); sync_up(res, f'results/{day}', newer_than=t_start)
    print('changed game files:', n)


def auto_facades(district: str | None):
    """Fully automatic first pass over a district: candidates for the review tool (not applied to the game)."""
    from . import facade
    photos = HOME / 'photos'; sync_down('photos' + (f'/{district}' if district else ''), photos / (district or ''))
    out = HOME / 'work' / 'auto'; out.mkdir(parents=True, exist_ok=True)
    for p in sorted(photos.rglob('*.jpg')):
        try: facade.process(str(p), str(out / p.stem.replace(' ', '_')))
        except Exception as e: print(p.name, 'skip:', e)
    sync_up(out, 'work/auto')
