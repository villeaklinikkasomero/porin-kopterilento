"""Review UI: four clicks on a photo + one click on the map -> photo facade for the game.

Run: porikit review --photos <folder with district folders> --work <output folder>  (then open http://localhost:8800)
The heavy lifting (rectification, rhythm, occluder rejection) is porikit.facade; this only serves the page and stores decisions.
"""
from __future__ import annotations
import hashlib, io, json, os, threading
from pathlib import Path
import cv2
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, HTMLResponse, Response
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from .. import facade, gamedata

PHOTOS = Path(os.environ.get('PORI_PHOTOS', 'photos'))
WORK = Path(os.environ.get('PORI_WORK', 'work')); (WORK / 'facades').mkdir(parents=True, exist_ok=True)
APPROVED = WORK / 'approved.json'
lock = threading.Lock()
app = FastAPI(title='Porin kopterilento – julkisivut')
app.mount('/files', StaticFiles(directory=str(WORK)), name='files')


def pid(rel: str) -> str: return hashlib.sha1(rel.encode()).hexdigest()[:12]


def photos():
    out = []
    for p in sorted(PHOTOS.rglob('*')):
        if p.suffix.lower() in ('.jpg', '.jpeg', '.png'):
            rel = str(p.relative_to(PHOTOS)); out.append({'id': pid(rel), 'rel': rel, 'district': p.parent.name if p.parent != PHOTOS else '', 'name': p.name})
    return out


def find(photo_id: str):
    for p in photos():
        if p['id'] == photo_id: return p
    raise HTTPException(404, 'photo not found')


def approved():
    return json.loads(APPROVED.read_text()) if APPROVED.exists() else {}


@app.get('/', response_class=HTMLResponse)
def index(): return (Path(__file__).parent / 'index.html').read_text(encoding='utf-8')


@app.get('/api/photos')
def api_photos():
    ap = approved(); done = {v['photo_id'] for v in ap.values()}
    return [{**p, 'street': gamedata.guess_street(p['name']), 'done': p['id'] in done} for p in photos()]


@app.get('/api/photo/{photo_id}')
def api_photo(photo_id: str, max: int = 1600):
    p = find(photo_id); img = cv2.imread(str(PHOTOS / p['rel']))
    h, w = img.shape[:2]; s = min(1.0, max / w); small = cv2.resize(img, (int(w * s), int(h * s)), interpolation=cv2.INTER_AREA)
    ok, buf = cv2.imencode('.jpg', small, [cv2.IMWRITE_JPEG_QUALITY, 85])
    return Response(buf.tobytes(), media_type='image/jpeg', headers={'X-Scale': str(s), 'X-Width': str(w), 'X-Height': str(h), 'Access-Control-Expose-Headers': 'X-Scale, X-Width, X-Height'})


@app.get('/api/streets')
def api_streets(): return gamedata.street_names()


@app.get('/api/buildings')
def api_buildings(street: str):
    ids, segs = gamedata.buildings_near_street(street)
    ap = approved()
    return {'segs': segs, 'buildings': [{'i': i, 'pts': gamedata.footprint(i), 'eave': gamedata.eave(i), 'done': str(i) in ap} for i in ids]}


class FacadeReq(BaseModel):
    photo_id: str
    quad: list                 # four [x, y] in full-resolution photo pixels: TL, TR, BR, BL
    building: int
    eave: float | None = None
    floor_mul: float = 1.0
    bay_mul: float = 1.0


@app.post('/api/facade')
def api_facade(r: FacadeReq):
    p = find(r.photo_id); eave = r.eave or gamedata.eave(r.building) or 15.0
    pref = str(WORK / 'facades' / f'{r.photo_id}_{r.building}')
    try:
        meta = facade.process(str(PHOTOS / p['rel']), pref, eave, quad=r.quad, floor_mul=r.floor_mul, bay_mul=r.bay_mul)
    except ValueError as e:
        raise HTTPException(422, str(e))
    name = os.path.basename(pref)
    return {'strip': f'/files/facades/{name}_strip.jpg', 'tile': f'/files/facades/{name}_tile.png', 'rect': f'/files/facades/{name}_rect.jpg',
            'module': meta['module'], 'strip_info': meta['strip'], 'eave': eave}


class ApproveReq(BaseModel):
    photo_id: str
    building: int
    west: float | None = None  # optional: second facade for walls west of this x (one footprint, two buildings)


@app.post('/api/approve')
def api_approve(r: ApproveReq):
    meta_p = WORK / 'facades' / f'{r.photo_id}_{r.building}.json'
    if not meta_p.exists(): raise HTTPException(400, 'compute the facade first')
    meta = json.loads(meta_p.read_text()); p = find(r.photo_id)
    with lock:
        ap = approved()
        ap[str(r.building)] = {'photo_id': r.photo_id, 'photo': p['rel'], 'strip': f'facades/{r.photo_id}_{r.building}_strip.jpg', 'bay_m': meta['strip']['bay_m'],
                               'floor_m': meta['strip']['floor_m'], 'eave_m': meta['strip']['eave_m']}
        APPROVED.write_text(json.dumps(ap, indent=1, ensure_ascii=False))
    return {'ok': True, 'count': len(ap)}


@app.delete('/api/approve/{building}')
def api_unapprove(building: int):
    with lock:
        ap = approved(); ap.pop(str(building), None); APPROVED.write_text(json.dumps(ap, indent=1, ensure_ascii=False))
    return {'ok': True}


@app.get('/api/approved')
def api_approved(): return approved()
