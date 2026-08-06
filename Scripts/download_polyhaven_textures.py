import urllib.request
from pathlib import Path

dest = Path(r'D:\Skyguard52\Content\Skyguard\Textures\PolyHaven')
dest.mkdir(parents=True, exist_ok=True)
logp = Path(r'D:\Skyguard52\Saved\Logs\texture-download.log')
sets = {
    'coast_sand_01': ['coast_sand_01_diff_2k.jpg','coast_sand_01_nor_gl_2k.jpg','coast_sand_01_rough_2k.jpg'],
    'aerial_rocks_02': ['aerial_rocks_02_diff_2k.jpg','aerial_rocks_02_nor_gl_2k.jpg','aerial_rocks_02_rough_2k.jpg'],
    'metal_plate': ['metal_plate_diff_2k.jpg','metal_plate_nor_gl_2k.jpg','metal_plate_rough_2k.jpg','metal_plate_metal_2k.jpg'],
    'painted_metal_02': ['painted_metal_02_diff_2k.jpg','painted_metal_02_nor_gl_2k.jpg','painted_metal_02_rough_2k.jpg'],
    'concrete_floor_painted': ['concrete_floor_painted_diff_2k.jpg','concrete_floor_painted_nor_gl_2k.jpg','concrete_floor_painted_rough_2k.jpg'],
    'asphalt_02': ['asphalt_02_diff_2k.jpg','asphalt_02_nor_gl_2k.jpg','asphalt_02_rough_2k.jpg'],
    'wood_cabinet_worn_long': ['wood_cabinet_worn_long_diff_2k.jpg','wood_cabinet_worn_long_nor_gl_2k.jpg','wood_cabinet_worn_long_rough_2k.jpg'],
    'roof_07': ['roof_07_diff_2k.jpg','roof_07_nor_gl_2k.jpg','roof_07_rough_2k.jpg'],
}
ok = fail = 0
lines = []
for name, files in sets.items():
    d = dest / name
    d.mkdir(exist_ok=True)
    for f in files:
        out = d / f
        if out.exists() and out.stat().st_size > 10000:
            ok += 1
            lines.append(f'SKIP {f}')
            continue
        url = f'https://dl.polyhaven.org/file/ph-assets/Textures/jpg/2k/{name}/{f}'
        try:
            urllib.request.urlretrieve(url, out)
            sz = out.stat().st_size
            if sz > 10000:
                ok += 1
                lines.append(f'OK {f} {sz}')
            else:
                fail += 1
                lines.append(f'SMALL {f} {sz}')
        except Exception as e:
            fail += 1
            lines.append(f'FAIL {f} {e}')
lines.append(f'DONE ok={ok} fail={fail}')
logp.write_text(chr(10).join(lines), encoding='utf-8')
print(chr(10).join(lines))
