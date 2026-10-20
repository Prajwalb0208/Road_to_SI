# Download the owner-approved Poly Haven CC0 assets (2026-10-20) via the public API.
#   python -I get_polyhaven.py
import json, os, urllib.request

OUT = os.environ.get('POLYHAVEN_DIR', os.path.join(os.path.dirname(os.path.abspath(__file__)), 'polyhaven'))
UA = {'User-Agent': 'road-to-si-asset-fetch'}
HDRI = ['kiara_1_dawn']
TEX = ['rock_face_03', 'aerial_grass_rock', 'forrest_ground_01', 'clay_roof_tiles', 'clay_plaster']
MODEL = ['boulder_01', 'rock_moss_set_01', 'fern_02', 'grass_bermuda_01']
ALLOWED = ('.hdr', '.jpg', '.png', '.gltf', '.bin')

def get(url):
    with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=120) as r: return r.read()
def save(url, path):
    assert url.startswith('https://dl.polyhaven.org/'), url
    assert path.lower().endswith(ALLOWED), path
    os.makedirs(os.path.dirname(path), exist_ok=True); data = get(url); open(path, 'wb').write(data); return len(data)

log = []
for k in HDRI:
    f = json.loads(get(f'https://api.polyhaven.com/files/{k}'))['hdri']['2k']['hdr']
    log.append((k, save(f['url'], os.path.join(OUT, k, f'{k}_2k.hdr'))))
for k in TEX:
    f = json.loads(get(f'https://api.polyhaven.com/files/{k}'))
    for m in ('Diffuse', 'nor_gl', 'Rough', 'Displacement'):
        e = f.get(m, {}).get('1k', {}); e = e.get('jpg') or e.get('png')
        if e: log.append((f'{k}/{m}', save(e['url'], os.path.join(OUT, k, os.path.basename(e['url'])))))
for k in MODEL:
    g = json.loads(get(f'https://api.polyhaven.com/files/{k}'))['gltf']['1k']['gltf']
    log.append((k, save(g['url'], os.path.join(OUT, k, os.path.basename(g['url'])))))
    for rel, inc in g.get('include', {}).items():
        log.append((f'{k}/{rel}', save(inc['url'], os.path.join(OUT, k, rel.replace('/', os.sep)))))
info = {k: json.loads(get(f'https://api.polyhaven.com/info/{k}')).get('authors') for k in HDRI + TEX + MODEL}
json.dump({'source': 'https://polyhaven.com (CC0)', 'downloaded': '2026-10-20', 'authors': info}, open(os.path.join(OUT, 'CREDITS.json'), 'w'), indent=1)
print(len(log), 'files', round(sum(s for _, s in log) / 1e6, 1), 'MB')
