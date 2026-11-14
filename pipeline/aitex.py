"""AI textures on Modal (GPU), two modes.

  modal run pipeline/aitex.py                         # tiles: seamless material textures from PROMPTS -> tex/ai/<name>_<n>.png
  modal run pipeline/aitex.py --mode facade           # facade: every tex/ai_in/<x>.png (+ optional <x>.txt prompt) -> tex/ai/<x>_ai<strength%>.png
  modal run pipeline/aitex.py --only keltalaatta      # one tile texture / one facade

Model: Stable Diffusion XL base 1.0 (CreativeML OpenRAIL++-M, commercial use allowed); facade mode adds the SDXL canny ControlNet
(diffusers/controlnet-canny-sdxl-1.0, OpenRAIL++). Inputs are text and our OWN game renders only (orthographic elevations of the
baked buildings) - never Street View or other photos. The ControlNet keeps the edges of the render (windows, balconies, storeys),
so the result still fits the geometry; img2img strength decides how much the AI may repaint.
Seamless tiles: every convolution of the UNet and VAE uses circular padding.
"""
from __future__ import annotations
from pathlib import Path
import modal

ROOT = Path(__file__).resolve().parent.parent
MODEL = 'stabilityai/stable-diffusion-xl-base-1.0'
CNET = 'diffusers/controlnet-canny-sdxl-1.0'
VAE = 'madebyollin/sdxl-vae-fp16-fix'

image = (modal.Image.debian_slim(python_version='3.11')
         .pip_install('torch==2.4.1', 'diffusers==0.30.3', 'transformers==4.44.2', 'accelerate==0.34.2', 'safetensors==0.4.5',
                      'pillow==10.4.0', 'numpy<2', 'opencv-python-headless==4.10.0.84')
         .run_commands(
             "python -c \"import torch; from diffusers import StableDiffusionXLPipeline as P, ControlNetModel as C, AutoencoderKL as A; "
             f"P.from_pretrained('{MODEL}', torch_dtype=torch.float16, variant='fp16', use_safetensors=True); "
             f"C.from_pretrained('{CNET}', torch_dtype=torch.float16); A.from_pretrained('{VAE}', torch_dtype=torch.float16)\""))
app = modal.App('pori-aitex', image=image)

STYLE = ('seamless tileable texture, flat orthographic front view of a wall surface, evenly lit, overcast diffuse light, no shadows, '
         'no perspective, photorealistic, high detail, 4k material scan')
NEG = 'perspective, windows, doors, people, text, logo, watermark, vignette, strong shadows, border, frame, blurry'
PROMPTS = {
    'keltalaatta':  'Finnish 1960s facade cladding of small glossy yellow ceramic tiles, 5 cm square tiles, light grey grout, slightly weathered',
    'pesubetoni':   'exposed aggregate concrete facade panel, washed concrete with small rounded beige and grey pebbles, 1970s Finland',
    'betonielementti': 'light grey precast concrete facade panel surface, fine pores, faint rain streaks and stains',
    'rappaus':      'old light beige lime plaster render wall, fine sand texture, subtle patches and hairline cracks',
    'keltatiili':   'yellow brick wall, Finnish pale yellow bricks in running bond, light mortar joints',
    'peltikatto':   'dark grey standing seam metal roof, vertical seams every 50 cm, slight weathering, seen from above',
    'huopakatto':   'black bitumen roofing felt on a flat roof, granular surface with overlapping strips, seen from above',
}
FACADE_STYLE = ('photograph of a real building facade in Pori, Finland, straight-on orthographic elevation, overcast daylight, '
                'photorealistic, sharp, high detail, realistic window glass with reflections and curtains, slight weathering and rain streaks')
FACADE_NEG = 'perspective, tilted, people, cars, trees, text, logo, watermark, cartoon, painting, 3d render, cgi, blurry, distorted windows'


def _tile(model):
    import torch
    for m in model.modules():
        if isinstance(m, (torch.nn.Conv2d, torch.nn.ConvTranspose2d)): m.padding_mode = 'circular'


def _png(im):
    import io
    b = io.BytesIO(); im.save(b, 'PNG'); return b.getvalue()


@app.function(gpu=['L4', 'A10', 'L40S'], timeout=1800)   # any region: inputs are our own renders, no photos
def tiles(names: list[str], variants: int = 2) -> dict:
    import torch
    from diffusers import StableDiffusionXLPipeline
    pipe = StableDiffusionXLPipeline.from_pretrained(MODEL, torch_dtype=torch.float16, variant='fp16', use_safetensors=True).to('cuda')
    _tile(pipe.unet); _tile(pipe.vae)
    out = {}
    for n in names:
        for v in range(variants):
            g = torch.Generator('cuda').manual_seed(1000 + v)
            im = pipe(prompt=f'{PROMPTS[n]}, {STYLE}', negative_prompt=NEG, width=1024, height=1024, num_inference_steps=30, guidance_scale=6.5, generator=g).images[0]
            out[f'{n}_{v + 1}.png'] = _png(im); print('done', n, v + 1, flush=True)
    return out


@app.function(gpu=['L4', 'A10', 'L40S'], timeout=1800)   # any region: inputs are our own renders, no photos
def facades(items: list, strength: float = 0.55, control: float = 0.65) -> dict:
    """items: (name, png bytes of our orthographic render, prompt[, extra negative prompt, ControlNet weight]) -> {name_aiNN.png, name_canny.png}"""
    import io, numpy as np, cv2, torch
    from PIL import Image
    from diffusers import StableDiffusionXLControlNetImg2ImgPipeline, ControlNetModel, AutoencoderKL
    cn = ControlNetModel.from_pretrained(CNET, torch_dtype=torch.float16)
    vae = AutoencoderKL.from_pretrained(VAE, torch_dtype=torch.float16)
    pipe = StableDiffusionXLControlNetImg2ImgPipeline.from_pretrained(MODEL, controlnet=cn, vae=vae, torch_dtype=torch.float16, variant='fp16', use_safetensors=True).to('cuda')
    out = {}
    for it in items:
        name, data, prompt = it[:3]; neg = it[3] if len(it) > 3 and it[3] else ''; ctl = it[4] if len(it) > 4 and it[4] else control
        src = Image.open(io.BytesIO(data)).convert('RGB')
        w, h = (src.width // 8) * 8, (src.height // 8) * 8; src = src.crop((0, 0, w, h))
        e = cv2.Canny(cv2.cvtColor(np.asarray(src), cv2.COLOR_RGB2GRAY), 60, 160)
        canny = Image.fromarray(np.stack([e] * 3, -1))
        g = torch.Generator('cuda').manual_seed(7)
        im = pipe(prompt=f'{prompt}, {FACADE_STYLE}', negative_prompt=FACADE_NEG + (', ' + neg if neg else ''), image=src, control_image=canny, strength=strength,
                  controlnet_conditioning_scale=ctl, width=w, height=h, num_inference_steps=36, guidance_scale=6.0, generator=g).images[0]
        out[f'{name}_ai{int(round(strength * 100))}' + (f'_c{int(round(ctl * 100))}' if ctl != 0.8 else '') + '.png'] = _png(im)   # _cNN: ControlNet weight other than 0.8; out[f'{name}_canny.png'] = _png(canny); print('done', name, flush=True)
    return out


def json_prompt(j: dict) -> tuple[str, str, float | None]:
    """English, machine-readable facade spec (tex/ai_in/<x>.json) -> prompt, negative prompt, ControlNet weight.
    Only the 'words' go to the model (it does not understand hex codes); the hex colours are for the colour lock after the AI step.
    SDXL reads only ~75 tokens, so the materials come first and the generic style words last."""
    m = j.get('materials', {})
    parts = [m[k]['words'] for k in ('wall', 'trim', 'plinth', 'window', 'roof') if m.get(k, {}).get('words')]
    prompt = ', '.join(['photo of a real building facade'] + parts + [j.get('style', ''), j.get('building', '')])
    neg = ', '.join(j.get('avoid', []))
    return prompt, neg, j.get('control')


@app.local_entrypoint()
def main(mode: str = 'tiles', only: str = '', variants: int = 2, strength: str = '0.55', control: float = 0.65):
    """strength: one value or several separated by commas, e.g. '0.8,0.9,0.95' (one image per value)"""
    import json as _json
    d = ROOT / 'tex' / 'ai'; d.mkdir(parents=True, exist_ok=True)
    strengths = [float(x) for x in str(strength).split(',') if x.strip()]
    if mode == 'facade':
        src = ROOT / 'tex' / 'ai_in'; items = []
        for p in sorted(src.glob('*.png')):
            if only and not p.stem.startswith(only): continue      # prefix: 'raati' = all four sides
            jf, t = p.with_suffix('.json'), p.with_suffix('.txt'); neg, ctl = '', None
            if jf.exists(): prompt, neg, ctl = json_prompt(_json.loads(jf.read_text(encoding='utf-8')))
            elif t.exists(): prompt = t.read_text(encoding='utf-8').strip()
            else: prompt = 'apartment block facade'
            items.append((p.stem, p.read_bytes(), prompt, neg, ctl))
        print('facades:', [i[0] for i in items], 'strengths:', strengths, flush=True)
        res = {}
        for st in strengths: res.update(facades.remote(items, st, control))
    else:
        res = tiles.remote([only] if only else list(PROMPTS), variants)
    for k, v in res.items():
        (d / k).write_bytes(v); print('saved', d / k)
