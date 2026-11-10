"""Rasterise un SVG en PNG RGBA (Chromium via Playwright : rsvg-convert absent de l'environnement de build)."""
import asyncio, base64, io
import numpy as np
from PIL import Image

def render(svg_path, w, h=None):
    svg = open(svg_path).read()
    async def go():
        from playwright.async_api import async_playwright
        async with async_playwright() as p:
            b = await p.chromium.launch()
            # taille demandee ; si h est None, proportions du viewBox
            import re
            vb = re.search(r'viewBox="([^"]+)"', svg)
            vw, vh = [float(v) for v in vb.group(1).split()[2:]] if vb else (w, h or w)
            H_ = h if h else int(round(w * vh / vw))
            pg = await b.new_page(viewport={'width': int(w), 'height': int(H_)}, device_scale_factor=1)
            src = 'data:image/svg+xml;base64,' + base64.b64encode(svg.encode()).decode()
            await pg.set_content(f"<html><body style='margin:0;background:transparent'><img src='{src}' style='width:{w}px;height:{H_}px;display:block'></body></html>")
            await pg.wait_for_timeout(200)
            png = await pg.screenshot(omit_background=True, clip={'x': 0, 'y': 0, 'width': int(w), 'height': int(H_)})
            await b.close()
            return png
    png = asyncio.run(go())
    return np.asarray(Image.open(io.BytesIO(png)).convert('RGBA'))
