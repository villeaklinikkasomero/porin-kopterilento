"""AI-generated seamless (tileable) test textures for the facade bake, on Modal.

  modal run pipeline/aitex.py                       # all textures in PROMPTS, 2 variants each -> tex/ai/*.png
  modal run pipeline/aitex.py --only keltalaatta    # one texture

Model: Stable Diffusion XL base 1.0 (stabilityai, CreativeML OpenRAIL++-M: commercial use allowed). Seamless tiling: every
convolution of the UNet and the VAE uses circular padding, so the left/right and top/bottom edges continue into each other.
Input is text only (no Street View or other photos). Runs on one L4 GPU, ~10 s per image after the model has loaded.
"""
from __future__ import annotations
from pathlib import Path
import modal

ROOT = Path(__file__).resolve().parent.parent
MODEL = 'stabilityai/stable-diffusion-xl-base-1.0'

image = (modal.Image.debian_slim(python_version='3.11')
         .pip_install('torch==2.4.1', 'diffusers==0.30.3', 'transformers==4.44.2', 'accelerate==0.34.2', 'safetensors==0.4.5', 'pillow==10.4.0')
         .run_commands(f"python -c \"from diffusers import StableDiffusionXLPipeline as P; import torch; P.from_pretrained('{MODEL}', torch_dtype=torch.float16, variant='fp16', use_safetensors=True)\""))
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


def _tile(model):
    import torch
    for m in model.modules():
        if isinstance(m, (torch.nn.Conv2d, torch.nn.ConvTranspose2d)): m.padding_mode = 'circular'


@app.function(gpu='L4', timeout=1800, region='eu')
def gen(names: list[str], variants: int = 2) -> dict:
    import io, torch
    from diffusers import StableDiffusionXLPipeline
    pipe = StableDiffusionXLPipeline.from_pretrained(MODEL, torch_dtype=torch.float16, variant='fp16', use_safetensors=True).to('cuda')
    _tile(pipe.unet); _tile(pipe.vae)
    out = {}
    for n in names:
        for v in range(variants):
            g = torch.Generator('cuda').manual_seed(1000 + v)
            im = pipe(prompt=f'{PROMPTS[n]}, {STYLE}', negative_prompt=NEG, width=1024, height=1024, num_inference_steps=30, guidance_scale=6.5, generator=g).images[0]
            b = io.BytesIO(); im.save(b, 'PNG'); out[f'{n}_{v + 1}.png'] = b.getvalue()
            print('done', n, v + 1, flush=True)
    return out


@app.local_entrypoint()
def main(only: str = '', variants: int = 2):
    names = [only] if only else list(PROMPTS)
    res = gen.remote(names, variants)
    d = ROOT / 'tex' / 'ai'; d.mkdir(parents=True, exist_ok=True)
    for k, v in res.items():
        (d / k).write_bytes(v); print('saved', d / k)
