// Scripted browser footage: a clean Chrome (temp profile, signed out, kiosk 1920x1080) driven over CDP.
//   node web-rec.mjs <plan.json> <profileDir>
// plan: [{"go": url, "wait": ms} | {"scroll": px, "ms": duration} | {"highlight": cssSelector|text, "ms": hold}
//        | {"zoom": 1.25} | {"wait": ms}]
import { spawn } from 'node:child_process';
import fs from 'node:fs';

const [planFile, profile] = process.argv.slice(2);
const plan = JSON.parse(fs.readFileSync(planFile, 'utf8'));
const CHROME = 'C:/Program Files/Google/Chrome/Application/chrome.exe';
const PORT = 9333;
const sleep = ms => new Promise(r => setTimeout(r, ms));
const chrome = spawn(CHROME, [`--remote-debugging-port=${PORT}`, `--user-data-dir=${profile}`, '--no-first-run',
  '--no-default-browser-check', '--disable-extensions', '--kiosk', '--hide-crash-restore-bubble', 'about:blank'], { stdio: 'ignore', detached: true });

let ws, seq = 0; const pending = new Map();
const send = (method, params = {}) => new Promise(res => { const id = ++seq; pending.set(id, res); ws.send(JSON.stringify({ id, method, params })); });
async function connect() {
  for (let i = 0; i < 40; i++) {
    try {
      const tabs = await (await fetch(`http://127.0.0.1:${PORT}/json`)).json();
      const page = tabs.find(t => t.type === 'page');
      if (page) { ws = new WebSocket(page.webSocketDebuggerUrl); await new Promise(r => ws.addEventListener('open', r)); break; }
    } catch { /* not up yet */ }
    await sleep(500);
  }
  ws.addEventListener('message', e => { const m = JSON.parse(e.data); if (m.id && pending.has(m.id)) { pending.get(m.id)(m.result); pending.delete(m.id); } });
}
const js = expr => send('Runtime.evaluate', { expression: expr, awaitPromise: true });

await connect();
await send('Page.enable');
for (const step of plan) {
  if (step.go) { await send('Page.navigate', { url: step.go }); await sleep(step.wait ?? 3500); await js(`document.body.style.zoom='${step.zoom ?? 1.25}'`); }
  else if (step.scroll != null) {
    const ms = step.ms ?? 2500, n = Math.max(1, Math.round(ms / 16));
    await js(`(async()=>{for(let i=0;i<${n};i++){window.scrollBy(0,${step.scroll / n});await new Promise(r=>setTimeout(r,16));}})()`);
  } else if (step.highlight) {
    const q = JSON.stringify(step.highlight);
    await js(`(()=>{let el=null;try{el=document.querySelector(${q});}catch(e){}
      if(!el){const w=document.createTreeWalker(document.body,NodeFilter.SHOW_TEXT);let n;while((n=w.nextNode())){if(n.textContent.trim()===${q}||n.textContent.includes(${q})){el=n.parentElement;break;}}}
      if(!el)return 'none';el.scrollIntoView({behavior:'smooth',block:'center'});
      setTimeout(()=>{el.style.outline='4px solid #FFD23F';el.style.outlineOffset='4px';el.style.borderRadius='6px';el.style.background='rgba(255,210,63,.18)';},700);return 'ok';})()`);
    await sleep(step.ms ?? 2500);
  }
  if (step.wait && !step.go) await sleep(step.wait);
}
await sleep(500);
try { await send('Browser.close'); } catch { /* closing */ }
setTimeout(() => process.exit(0), 800);
