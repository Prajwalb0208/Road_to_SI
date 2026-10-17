// Live FilmCraft demo for screen recording: new project → import → 9:16 sequence → frame-exact placement →
// Warp Stabilizer on the videos → cross-dissolves → play → export. Drives the open app over its bridge.
//   node fc-demo.mjs <out.mp4> [--clips clips.json] [--bridge 127.0.0.1:9876]
import { spawnSync } from 'node:child_process';
import fs from 'node:fs';

const CLI = 'C:/Program Files/FilmCraft/filmcraft-cli.exe';
const args = process.argv.slice(2);
const out = args.find(a => !a.startsWith('--'));
const bi = args.indexOf('--bridge');
const bridge = bi >= 0 ? args[bi + 1] : '127.0.0.1:9876';
const sleep = ms => Atomics.wait(new Int32Array(new SharedArrayBuffer(4)), 0, 0, ms);
function x(id, params = {}, pause = 1500) {
  const r = spawnSync(CLI, ['--bridge', bridge, 'exec', id, JSON.stringify(params)], { encoding: 'utf8', maxBuffer: 1 << 26 });
  const txt = (r.stdout || '').trim();
  let res; try { res = JSON.parse(txt); } catch { res = txt; }
  console.log(id, r.status === 0 ? 'ok' : 'ERR', (typeof res === 'string' ? res : JSON.stringify(res)).slice(0, 140), (r.stderr || '').trim().slice(0, 200));
  sleep(pause);
  return res;
}
const raw = (m, p, pause) => { const r = spawnSync(process.execPath, [new URL('./fc-raw.mjs', import.meta.url).pathname.replace(/^\/([A-Za-z]:)/, '$1'), m, JSON.stringify(p), bridge.split(':')[1]], { encoding: 'utf8' }); console.log(m, (r.stdout || r.stderr).trim().slice(0, 120)); sleep(pause); };
const fit = () => raw('ui.set', { timeline: { fit: true } }, 600);
const FPF = 8475667200n; // ticks per frame at 29.97 (254016000000 * 1001 / 30000)
const T = f => Number(BigInt(f) * FPF);

// clips.json: [{"path": "C:/videos/clip1.mp4", "video": true, "inSec": 2, "frames": 120}, {"path": "C:/photos/p1.jpg", "frames": 66}]
const ci = args.indexOf('--clips');
const src = JSON.parse(fs.readFileSync(ci >= 0 ? args[ci + 1] : 'clips.json', 'utf8'));

x('file.newProject', { name: 'wildlife-demo' }, 2500);
const imp = x('file.import', { paths: src.map(s => s.path) }, 3000);
const items = imp.items;
x('file.newSequence', { name: 'wildlife-reel-9x16', width: 1080, height: 1920, fps: 29.97, video: 1, audio: 1 }, 2500);
let frame = 0;
const clips = [];
for (const [i, s] of src.entries()) {
  const p = { item: items[i], track: 'V1', frame, duration: T(s.frames), audio: false };
  if (s.video) p.sourceIn = Math.round(s.inSec * 254016000000);
  const r = x('timeline.place', p, 1800);
  const clip = r?.clip ?? r?.clips?.[0] ?? r?.id;
  clips.push(clip);
  x('clip.fillFrame', { clips: [clip] }, 900);
  fit();
  frame += s.frames;
}
for (const [i, s] of src.entries()) if (s.video) {
  x('effects.apply', { clips: [clips[i]], effect: 'Warp Stabilizer' }, 2000);
  x('effects.setParam', { clip: clips[i], effect: 'warp_stabilizer', param: 'smoothness', value: 30 }, 800);
}
for (const c of clips.slice(1)) x('sequence.applyVideoTransition', { clip: c, effect: 'cross_dissolve', frames: 8, edge: 'in' }, 1200);
x('sequence.applyVideoTransition', { clip: clips.at(-1), effect: 'cross_dissolve', frames: 20, edge: 'out' }, 1500);
fit();
x('playhead.set', { frame: 0 }, 1000);
raw('ui.playback', { action: 'play' }, 15500);
raw('ui.playback', { action: 'stop' }, 1500);
if (out) x('export.quick', { path: out, hardwareEncoding: 'auto', wait: true }, 4000);
