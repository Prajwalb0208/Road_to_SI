// Send one raw control method to the running FilmCraft (filmcraft --control 9876).
//   node fc-raw.mjs <method> '<json params>' [port]
import net from 'node:net';
const [method, params = '{}', port = '9876'] = process.argv.slice(2);
const s = net.connect(+port, '127.0.0.1', () => s.write(JSON.stringify({ id: 1, method, params: JSON.parse(params) }) + '\n'));
let b = '';
s.on('data', d => { b += d; if (b.includes('\n')) { console.log(b.trim().slice(0, 300)); s.end(); process.exit(0); } });
s.on('error', e => { console.error(e.message); process.exit(1); });
setTimeout(() => { console.error('timeout'); process.exit(1); }, 20000);
