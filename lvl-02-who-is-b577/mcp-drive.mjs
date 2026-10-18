// Drive any Craft app's MCP server (stdio) from a JSON step list — used to run live, recorded demos.
//   node mcp-drive.mjs "<cli.exe>" "<args…>" --list                 → print tool names + short descriptions
//   node mcp-drive.mjs "<cli.exe>" "<args…>" --schema tool1,tool2   → input schemas
//   node mcp-drive.mjs "<cli.exe>" "<args…>" steps.json [--log out.json]
//   steps.json: [[toolName, {args}, pauseMs?], …]   e.g. ["command_run", {"id": "cell.set", "params": {…}}, 600]
import { spawn } from 'node:child_process';
import fs from 'node:fs';

const [exe, argStr, third, ...rest] = process.argv.slice(2);
const p = spawn(exe, argStr.split(' ').filter(Boolean), { stdio: ['pipe', 'pipe', 'inherit'] });
let buf = '', id = 0;
const waits = new Map();
p.stdout.on('data', d => {
  buf += d;
  let i;
  while ((i = buf.indexOf('\n')) >= 0) {
    const line = buf.slice(0, i).trim(); buf = buf.slice(i + 1);
    if (!line) continue;
    let m; try { m = JSON.parse(line); } catch { continue; }
    if (m.id != null && waits.has(m.id)) { waits.get(m.id)(m); waits.delete(m.id); }
  }
});
const rpc = (method, params) => new Promise(res => { const n = ++id; waits.set(n, res); p.stdin.write(JSON.stringify({ jsonrpc: '2.0', id: n, method, params }) + '\n'); });
const note = (method, params) => p.stdin.write(JSON.stringify({ jsonrpc: '2.0', method, params }) + '\n');
const sleep = ms => new Promise(r => setTimeout(r, ms));
const short = r => JSON.stringify(r?.result?.content?.map(c => c.text ?? c.type) ?? r?.error ?? r).slice(0, 160);

await rpc('initialize', { protocolVersion: '2025-06-18', capabilities: {}, clientInfo: { name: 'mcp-drive', version: '1' } });
note('notifications/initialized', {});
if (third === '--schema') {
  const r = await rpc('tools/list', {});
  for (const t of r.result?.tools ?? []) if (rest[0].split(',').includes(t.name)) console.log(t.name, JSON.stringify(t.inputSchema));
} else if (third === '--list') {
  const r = await rpc('tools/list', {});
  for (const t of r.result?.tools ?? []) console.log(t.name.padEnd(22), (t.description || '').split('\n')[0].slice(0, 110));
} else {
  const steps = JSON.parse(fs.readFileSync(third, 'utf8'));
  const log = [], t0 = Date.now();
  for (const [name, args = {}, pause = 400] of steps) {
    const t = Date.now() - t0;
    const r = await rpc('tools/call', { name, arguments: args });
    const bad = r.error || r.result?.isError;
    console.log(`${bad ? 'ERR' : 'ok '} ${name} ${short(r)}`);
    log.push({ t, ms: Date.now() - t0 - t, name, args, ok: !bad, result: r.result ?? r.error });
    await sleep(pause);
  }
  const li = rest.indexOf('--log');
  if (li >= 0) fs.writeFileSync(rest[li + 1], JSON.stringify(log, null, 1));
}
p.stdin.end(); setTimeout(() => process.exit(0), 300);
