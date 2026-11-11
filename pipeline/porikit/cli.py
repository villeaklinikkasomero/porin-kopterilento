"""porikit – the Porin kopterilento graphics pipeline.

  porikit review  --photos DIR --work DIR [--game DIR]     review UI on http://localhost:8800
  porikit facade  PHOTO OUT_PREFIX [--eave M] [--quad x,y,x,y,x,y,x,y]
  porikit auto    [--district NAME]                        automatic first pass over photos (S3 -> S3)
  porikit export  --work DIR --game DIR                    approved facades -> ph_*.jpg + phs.json
  porikit layout                                            recreate the working layout (container start)
  porikit bake    ZONE [ZONE ...] | all [--samples N] [--parallel N]
  porikit landmarks NAME [NAME ...]
  porikit shots   OUT '[["name",x,y,alt,yaw]]'
  porikit queue   KIND JSON                                add a task to the night queue (S3)
  porikit night                                             run the night queue (AWS Batch entry point)
"""
from __future__ import annotations
import argparse, json, os, sys, time
from pathlib import Path


def main(argv=None):
    ap = argparse.ArgumentParser(prog='porikit', description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sp = ap.add_subparsers(dest='cmd', required=True)
    r = sp.add_parser('review'); r.add_argument('--photos', required=True); r.add_argument('--work', required=True); r.add_argument('--game', default=None); r.add_argument('--port', type=int, default=8800)
    f = sp.add_parser('facade'); f.add_argument('photo'); f.add_argument('out'); f.add_argument('--eave', type=float); f.add_argument('--quad')
    a = sp.add_parser('auto'); a.add_argument('--district')
    e = sp.add_parser('export'); e.add_argument('--work', required=True); e.add_argument('--game', required=True)
    sp.add_parser('layout')
    b = sp.add_parser('bake'); b.add_argument('zones', nargs='+'); b.add_argument('--samples', type=int, default=48); b.add_argument('--parallel', type=int, default=1)
    l = sp.add_parser('landmarks'); l.add_argument('names', nargs='+')
    s = sp.add_parser('shots'); s.add_argument('out'); s.add_argument('views')
    q = sp.add_parser('queue'); q.add_argument('kind', choices=['bake', 'landmarks', 'facades', 'shots']); q.add_argument('json', nargs='?', default='{}')
    sp.add_parser('night')
    o = ap.parse_args(argv)

    if o.cmd == 'review':
        os.environ['PORI_PHOTOS'] = o.photos; os.environ['PORI_WORK'] = o.work
        if o.game: os.environ['PORI_GAME'] = o.game
        import uvicorn
        from .review.app import app
        uvicorn.run(app, host='127.0.0.1', port=o.port)
    elif o.cmd == 'facade':
        from . import facade
        quad = None
        if o.quad: v = [float(x) for x in o.quad.split(',')]; quad = [v[i:i + 2] for i in range(0, 8, 2)]
        print(json.dumps(facade.process(o.photo, o.out, o.eave, quad=quad)['module'], indent=1))
    else:
        from . import jobs
        if o.cmd == 'auto': jobs.auto_facades(o.district)
        elif o.cmd == 'export': jobs.export(Path(o.work), Path(o.game))
        elif o.cmd == 'layout': jobs.layout()
        elif o.cmd == 'bake': jobs.bake(o.zones, o.samples, o.parallel)
        elif o.cmd == 'landmarks': jobs.landmarks(o.names)
        elif o.cmd == 'shots': sys.exit(jobs.shots(json.loads(o.views), Path(o.out)))
        elif o.cmd == 'queue':
            print('queued', jobs.enqueue(o.kind, json.loads(o.json)))
        elif o.cmd == 'night': jobs.night()


if __name__ == '__main__':
    main()
