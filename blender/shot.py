import asyncio, sys, subprocess, time
from playwright.async_api import async_playwright
shots = [  # x, y, alt, yaw(deg, 0 = north), file
    (215, 60, 38, 0, 'c1.png'), (60, 20, 30, 0, 'c2.png')]
async def main():
    srv = subprocess.Popen(['python3', '-m', 'http.server', '8765', '--directory', '/home/claude/pori'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL); time.sleep(1)
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'])
        pg = await b.new_page(viewport={'width': 1280, 'height': 720})
        errs = []; pg.on('pageerror', lambda e: errs.append(str(e))); pg.on('console', lambda m: errs.append(m.text) if m.type == 'error' else None)
        await pg.goto('http://localhost:8765/index.html')
        await asyncio.sleep(20); print('ERR', errs[:6], await pg.evaluate('[window.__ready, (window.__bl||[]).length]'))
        for _ in range(15):
            n = await pg.evaluate('(window.__bl||[]).filter(k=>k.startsWith("tori")&&k!=="tori").length')
            if n >= 6: break
            await asyncio.sleep(1)
        print('cars', await pg.evaluate('window.__cars')); print('loaded', await pg.evaluate('(window.__bl||[]).join(",")'))
        await pg.evaluate('window.__game.begin()'); await asyncio.sleep(1)
        for x, y, alt, yaw, f in shots:
            await pg.evaluate(f'(()=>{{const G=window.__game,S=G.S;S.x={x};S.y={y};S.alt={alt};S.yaw={yaw}*Math.PI/180;S.vx=S.vy=S.vz=0;S.landed=false;G.snap();}})()')
            await asyncio.sleep(0.6)
            await pg.evaluate(f'(()=>{{const G=window.__game,S=G.S;S.x={x};S.y={y};S.alt={alt};S.yaw={yaw}*Math.PI/180;S.vx=S.vy=S.vz=0;G.snap();}})()')
            await asyncio.sleep(0.4)
            await pg.screenshot(path='/home/claude/out/' + f)
        print('errors', errs[:5]); await b.close()
    srv.kill()
asyncio.run(main())
