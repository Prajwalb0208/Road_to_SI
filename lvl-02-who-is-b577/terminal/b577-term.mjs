// B-577 in the terminal: ASCII B-577 runs across the terminal, stops, smiles (eyes turn orange) and asks you a question.
//   node b577-term.mjs            (interactive: answer y/n)
//   node b577-term.mjs --demo     (auto-answers "y" after 2 s, for recordings)
import readline from 'node:readline';

const C = { cy: '\x1b[96m', or: '\x1b[38;5;215m', cr: '\x1b[38;5;230m', dim: '\x1b[38;5;240m', rs: '\x1b[0m' };
const demo = process.argv.includes('--demo');
const sleep = ms => new Promise(r => setTimeout(r, ms));
const W = Math.min(process.stdout.columns || 100, 120);

function bot(eyes, eyeCol, legs, mouth = '\\_/') {
  const o = C.or, c = C.cr, e = eyeCol, r = C.rs;
  return [
    `   ${o}\\${c} ${o}/${r}`,
    ` ${c}.-------.${r}`,
    `${o}[${c}|${r} ${e}${eyes[0]}${r}   ${e}${eyes[1]}${r} ${c}|${o}]${r}`,
    ` ${c}|${r}  ${e}${mouth}${r}  ${c}|${r}`,
    ` ${c}'-------'${r}`,
    `   ${o}[B577]${r}`,
    `   ${c}${legs}${r}`,
  ];
}
const draw = (lines, x) => { process.stdout.write('\x1b[H'); for (const l of lines) process.stdout.write(' '.repeat(x) + l + '\x1b[K\n'); };

process.stdout.write('\x1b[2J\x1b[?25l');
process.stdout.write('\x1b[9;1H' + C.dim + '$ ' + '─'.repeat(W - 4) + C.rs);
const stop = Math.floor(W / 2) - 6;
for (let x = 0; x <= stop; x += 2) {                       // run across the command line
  draw(bot(['o', 'o'], C.cy, x % 4 ? ' / \\ ' : ' | | '), x);
  await sleep(70);
}
draw(bot(['o', 'o'], C.cy, ' | | '), stop); await sleep(500);
draw(bot(['-', '-'], C.cy, ' | | '), stop); await sleep(120);  // blink
draw(bot(['^', '^'], C.or, ' | | ', '\\_/'), stop); await sleep(600);   // happy: eyes turn orange
process.stdout.write('\x1b[11;1H\x1b[?25h' + C.or + 'B-577 › ' + C.rs + 'want me to build the next level live, in front of you? ' + C.cy + '[y/n] ' + C.rs);

const answer = await new Promise(res => {
  if (demo) { setTimeout(() => { process.stdout.write('y\n'); res('y'); }, 2000); return; }
  const rl = readline.createInterface({ input: process.stdin }); rl.once('line', l => { rl.close(); res(l.trim().toLowerCase()); });
});
const yes = answer.startsWith('y');
draw(bot(yes ? ['^', '^'] : ['o', 'o'], yes ? C.or : C.cy, yes ? ' \\ / ' : ' | | ', yes ? '\\_/' : '___'), stop);
process.stdout.write('\x1b[13;1H' + C.or + 'B-577 › ' + C.rs + (yes ? 'deal. comment what I should build — I read them all.' : 'fair. tell me in the comments what you WOULD watch.') + '\n\n');
await sleep(demo ? 2500 : 0);
