// Drive the running PhotoCraft app over its control channel (photocraft --control 7878 --control-token-file F).
//   node pc-live.mjs <tokenFile> script.json   — script: [[method, params, pauseMs?], …]
//   methods: any control method (ui.set, ui.menu.invoke …) or "cmd:<engine command id>" (engine.execute)
import fs from 'node:fs';
import net from 'node:net';

const [tokFile, scriptFile] = process.argv.slice(2);
const token = fs.readFileSync(tokFile, 'utf8').trim();
const steps = JSON.parse(fs.readFileSync(scriptFile, 'utf8'));
const port = +(process.env.PC_PORT || 7878);
const sock = net.connect(port, '127.0.0.1');
let buf = '', waiting = null, n = 0;
sock.on('data', d => {
  buf += d;
  let i;
  while ((i = buf.indexOf('\n')) >= 0) {
    const line = buf.slice(0, i); buf = buf.slice(i + 1);
    let msg; try { msg = JSON.parse(line); } catch { continue; }
    if (waiting && String(msg.id) === String(n)) { const w = waiting; waiting = null; w(msg); }
  }
});
const call = (method, params) => new Promise(res => { waiting = res; sock.write(JSON.stringify({ id: ++n, method, params }) + '\n'); });
const sleep = ms => new Promise(r => setTimeout(r, ms));
sock.on('connect', async () => {
  const a = await call('auth', { token }, 'auth');
  if (!a.ok) { console.error('auth failed', a.error); process.exit(1); }
  for (const [m, p, pause] of steps) {
    const r = m.startsWith('cmd:') ? await call('engine.execute', { command: m.slice(4), params: p || {} }) : await call(m, p || {});
    console.log(m, r.ok ? 'ok' : 'ERR', JSON.stringify(r.ok ? r.result : r.error)?.slice(0, 160));
    await sleep(pause ?? 1200);
  }
  sock.end(); process.exit(0);
});
sock.on('error', e => { console.error(e.message); process.exit(1); });
