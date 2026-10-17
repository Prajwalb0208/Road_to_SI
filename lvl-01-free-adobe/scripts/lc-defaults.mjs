#!/usr/bin/env node
// Default wildlife edit on the OPEN LightCraft app (start it with D:\Mycraft\tools\LightCraft-fit.ps1).
// Works for any species: the subject is found by SAM 3 from a text prompt or from clicks.
//
//   node lc-defaults.mjs masks  --id N --subject "bird" [--points '[[x,y],..]' --exclude '[[x,y],..]']
//                               [--sky auto|no] [--light tr|tl|br|bl|none] [--eye x,y]... [--base] [--preview DIR]
//   node lc-defaults.mjs export --id N --out DIR --name BASE [--crop x0,y0,x1,y1]
//
// masks:  Subject (+lift, texture, sharpness)            — prompt or object clicks
//         Sky (only if SAM finds sky) = sky − subject      — darker, richer
//         Background = NOT(subject ∪ sky)                 — darker, smoother
//         Sky and Background get the SAME exposure, so their soft, complementary edges cancel (no mottling).
//         --light: diagonal light from that corner (whole frame) + fade from the opposite corner (not subject).
//         --eye:  tiny radial per eye (lift, saturation, clarity, sharpness).
//         --base: global look (contrast, deep blacks, lifted shadows, ISO-based AI denoise, halo-safe sharpening).
//         --preview: mask overlays (subject / sky / background) + an edit preview, to check with vision.
// export: full-res JPG q100 + 16-bit PNG + 1080 JPG for Instagram, straight from the NEF edit.
import { spawnSync } from 'node:child_process';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';

const CLI = process.env.LIGHTCRAFT_CLI || 'C:\\Program Files\\LightCraft\\lightcraft-cli.exe';
const ADDR = process.env.LC_ADDR || '127.0.0.1:7980';
const argv = process.argv.slice(2);
const mode = argv[0];
const opt = (k, d) => { const i = argv.indexOf(k); return i >= 0 ? argv[i + 1] : d; };
const all = k => argv.flatMap((a, i) => (a === k ? [argv[i + 1]] : []));
const has = k => argv.includes(k);
const id = +opt('--id');
if (!['masks', 'export'].includes(mode) || !id) {
  console.error('usage: lc-defaults.mjs masks|export --id N ... (see header)'); process.exit(2);
}
const fwd = p => p.replace(/\\/g, '/');
const C = (command, params = {}) => ({ command, params });

function run(cmds) {
  const f = path.join(os.tmpdir(), `lc-defaults-${process.pid}.jsonl`);
  fs.writeFileSync(f, cmds.map(c => JSON.stringify(c)).join('\n') + '\n');
  const r = spawnSync(CLI, ['run', '--connect', ADDR, '--keep-going', '--script', f], { encoding: 'utf8', maxBuffer: 1 << 28 });
  const out = (r.stdout || '').split('\n').filter(l => l.startsWith('{')).map(l => JSON.parse(l));
  if (!out.length) { console.error((r.stderr || '').trim() || 'LightCraft not reachable — start it with LightCraft-fit.ps1'); process.exit(1); }
  for (const o of out) if (!o.ok) console.error(`  ! ${o.command}: ${JSON.stringify(o.error)}`);
  return out;
}
const sleep = ms => Atomics.wait(new Int32Array(new SharedArrayBuffer(4)), 0, 0, ms);
function waitSam(maxS = 240) {
  for (let t = 0; t < maxS; t += 2) {
    const [s] = run([C('segment.model.status')]);
    if (s.ok && !s.result.busy) return;
    sleep(2000);
  }
  throw new Error('SAM 3 still busy');
}
const masks = () => run([C('develop.get', { id })])[0].result.masks;
const byName = n => masks().find(m => m.name === n);
const hasSeg = m => m && m.components.some(c => c.shape.seg);
// a SAM mask resolves some time after `segment.model.status` already reads idle: poll the mask itself
function waitMask(name, maxS = 90) {
  for (let t = 0; t < maxS; t += 3) {
    const m = byName(name);
    if (hasSeg(m)) return m;
    sleep(3000);
  }
  return byName(name);
}

if (mode === 'export') {
  const dir = opt('--out'), name = opt('--name');
  if (!dir || !name) { console.error('export needs --out DIR --name BASE'); process.exit(2); }
  fs.mkdirSync(dir, { recursive: true });
  const common = { ids: [id], colorSpace: 'srgb', metadata: 'copyright', removeLocation: true, conflict: 'overwrite' };
  const cmds = [C('library.select', { ids: [id] })];
  if (opt('--crop')) cmds.push(C('crop.set', { rect: opt('--crop').split(',').map(Number) }));
  cmds.push(
    C('app.export', { ...common, path: fwd(path.join(dir, `${name}_full.jpg`)), format: 'jpeg', quality: 100, longEdge: 0, sharpen: 'screen', sharpenAmount: 'low' }),
    C('app.export', { ...common, path: fwd(path.join(dir, `${name}_full.png`)), format: 'png', bitDepth: 16, longEdge: 0 }),
    C('app.export', { ...common, path: fwd(path.join(dir, `${name}_ig_1080.jpg`)), format: 'jpeg', quality: 95, longEdge: 1080, sharpen: 'screen', sharpenAmount: 'standard' }),
  );
  for (const o of run(cmds)) if (o.command === 'app.export' && o.ok) for (const f of o.result.files || []) console.log(`  ${f.path}  ${f.width}×${f.height}`);
  process.exit(0);
}

// ---------- masks ----------
const subjectText = opt('--subject', 'animal');
const points = opt('--points') ? JSON.parse(opt('--points')) : null;
const exclude = opt('--exclude') ? JSON.parse(opt('--exclude')) : [];
// the subject as a mask shape: SAM object clicks when given (tighter), else a SAM text prompt
const subjectShape = points ? { kind: 'object', points, exclude } : { kind: 'prompt', text: subjectText };

run([C('library.select', { ids: [id] }), C('segment.prepare')]);
sleep(4000); // analysis starts a moment after prepare returns
waitSam();

// drop an earlier default set, keep anything else (the user's own masks)
const ours = ['Subject', 'Sky', 'Background', 'Eye', 'Light (diagonal)', 'Fade (diagonal, not subject)'];
for (const m of masks()) if (ours.some(n => m.name === n || m.name.startsWith('Eye'))) run([C('mask.delete', { id: m.id })]);

// LightCraft 0.8 segments an Object shape's stored points only after a click: repeat the first point as one
const click = id => (points ? [C('mask.objectPoint', { x: points[0][0], y: points[0][1], ...(id ? { id } : {}) })] : []);

// Subject
let subject = null;
for (let attempt = 0; attempt < 3 && !hasSeg(subject); attempt++) {
  // a mask added while SAM is still analysing comes back empty — delete and add again
  if (subject) { run([C('mask.delete', { id: subject.id })]); sleep(5000); waitSam(); }
  run([C('mask.add', { ...subjectShape, name: 'Subject' }), ...click()]); sleep(2000); waitSam();
  subject = waitMask('Subject', 60);
}
if (!hasSeg(subject)) { console.error(`SAM found no "${subjectText}" — give --points on the animal`); process.exit(1); }

// Sky (only when SAM finds one)
let sky = null;
if (opt('--sky', 'auto') !== 'no') {
  run([C('mask.add', { kind: 'prompt', text: 'sky', name: 'Sky' })]); waitSam();
  sky = waitMask('Sky', 45);
  if (hasSeg(sky)) {
    run([C('mask.addComponent', { id: sky.id, op: 'subtract', ...subjectShape }), ...click(sky.id)]); waitSam();
    run([C('mask.refine', { id: sky.id, value: 45 })]);
  } else { if (sky) run([C('mask.delete', { id: sky.id })]); sky = null; }
}

// Background = NOT(subject ∪ sky)  (the invert applies after the components)
run([C('mask.add', { ...subjectShape, name: 'Background' }), ...click()]); waitSam();
const bg = waitMask('Background');
if (sky) { run([C('mask.addComponent', { id: bg.id, op: 'add', kind: 'prompt', text: 'sky' })]); waitSam(); }
// refine only smooths the sky/background seam; without sky it spreads a halo around the subject
run([C('mask.invert', { id: bg.id }), ...(sky ? [C('mask.refine', { id: bg.id, value: 45 })] : [])]);

// adjustments — from the user's own DSC_6352 edit: do NOT lift the subject (it gets light from the diagonal),
// darken the background hard, sharpen the subject strongly + local NR; same exposure on sky and background
const adj = [
  C('mask.adjust', { id: subject.id, values: { exposure: -0.4, highlights: -20, shadows: 25, whites: 15, texture: 42, clarity: 10, dehaze: 9, sharpness: sky ? 25 : 60, noise: 25, saturation: 4 } }),
  C('mask.adjust', { id: bg.id, values: { exposure: -0.6, highlights: -20, texture: -15, clarity: -10 } }),
];
if (sky) adj.push(C('mask.adjust', { id: sky.id, values: { exposure: -0.6, highlights: -20, saturation: 8, dehaze: 5 } }));

// diagonal light + opposite fade
const corners = { tl: [0, 0], tr: [1, 0], bl: [0, 1], br: [1, 1] };
const opposite = { tl: 'br', tr: 'bl', bl: 'tr', br: 'tl' };
const light = opt('--light', 'none');
if (corners[light]) {
  const a = corners[light], b = corners[opposite[light]];
  adj.push(C('mask.add', { kind: 'linear', name: 'Light (diagonal)', start: a, end: [0.5, 0.5] }),
    C('mask.adjust', { values: { exposure: 1.5, temp: 25 } }),
    C('mask.add', { kind: 'linear', name: 'Fade (diagonal, not subject)', start: b, end: [b[0] + 0.62 * (0.5 - b[0]) * 2, b[1] + 0.62 * (0.5 - b[1]) * 2] }));
}
run(adj);
if (corners[light]) {
  const fade = byName('Fade (diagonal, not subject)');
  run([C('mask.addComponent', { id: fade.id, op: 'subtract', ...subjectShape })]); waitSam();
  run([C('mask.adjust', { id: fade.id, values: { exposure: -0.85, saturation: -10 } })]);
}

// eyes
all('--eye').forEach((e, i) => {
  const [x, y] = e.split(',').map(Number);
  run([C('mask.add', { kind: 'radial', name: `Eye ${i + 1}`, center: [x, y], rx: 0.006, ry: 0.009, feather: 50 }),
    C('mask.adjust', { values: { exposure: 0.35, shadows: 20, saturation: 25, clarity: 20, sharpness: 35 } })]);
});

// global look
if (has('--base')) {
  const meta = run([C('photo.allMetadata', { id })])[0].result.exif;
  const iso = parseInt(meta.find(e => e.name === 'ISO Speed')?.value || '400', 10);
  const denoise = iso <= 800 ? 25 : iso <= 1600 ? 40 : iso <= 3200 ? 50 : iso <= 6400 ? 60 : 70;
  run([C('develop.merge', { settings: { enhance: { raw_details: true } }, label: 'Raw Details' }),
    C('develop.set', { ids: [id], values: {
      'light.contrast': 25, 'light.highlights': -30, 'light.shadows': 22, 'light.whites': 10, 'light.blacks': -35,
      'curve.darks': -6, 'curve.lights': 4, 'color.vibrance': 12, 'color.saturation': -3, 'effects.dehaze': 6, 'effects.texture': 8,
      'enhance.denoise': denoise, 'detail.nrLuminance': 0, 'detail.nrColor': 10,
      // halo-safe only when a bright sky meets the subject; otherwise the user's strong detail
      ...(sky ? { 'detail.sharpenAmount': 35, 'detail.sharpenRadius': 0.6, 'detail.sharpenDetail': 25, 'detail.sharpenMasking': 78 }
              : { 'detail.sharpenAmount': 42, 'detail.sharpenRadius': 0.8, 'detail.sharpenDetail': 70, 'detail.sharpenMasking': 75 }) } })]);
  console.log(`  base look applied (ISO ${iso} → AI denoise ${denoise})`);
}

// overlays for a vision check
const dir = opt('--preview');
if (dir) {
  fs.mkdirSync(dir, { recursive: true });
  const ms = masks();
  const vis = Object.fromEntries(ms.map(m => [m.id, m.visible !== false]));
  const cmds = [C('develop.set', { values: { 'light.exposure': -4 } })];
  const cur = run([C('develop.get', { id })])[0].result.light.exposure;
  for (const m of [subject, sky, bg].filter(Boolean)) {
    const e0 = ms.find(x => x.id === m.id).adjust.exposure;
    for (const x of ms) cmds.push(C('mask.visible', { id: x.id, visible: x.id === m.id }));
    cmds.push(C('mask.adjust', { id: m.id, values: { exposure: 4 } }),
      C('app.export', { ids: [id], path: fwd(path.join(dir, `mask_${m.name.toLowerCase()}.jpg`)), longEdge: 1000, quality: 85, conflict: 'overwrite' }),
      C('mask.adjust', { id: m.id, values: { exposure: e0 } }));
  }
  for (const x of ms) cmds.push(C('mask.visible', { id: x.id, visible: vis[x.id] }));
  cmds.push(C('develop.set', { values: { 'light.exposure': cur } }));
  run(cmds);
  // export the edit in a later call: in the same script the render can still be the last overlay's
  sleep(2000);
  run([C('app.export', { ids: [id], path: fwd(path.join(dir, 'edit_preview.jpg')), longEdge: 1600, quality: 90, conflict: 'overwrite' })]);
  console.log(`  previews → ${dir} (mask_subject/sky/background.jpg, edit_preview.jpg)`);
}
console.log(`  masks: Subject${sky ? ', Sky' : ''}, Background${corners[light] ? ', Light, Fade' : ''}${all('--eye').length ? ', Eyes' : ''}`);
