// Copie le moteur (Pyodide, fontTools, brotli-wasm, sources Python) dans public/engine,
// servi tel quel par Vite puis embarqué dans l'application : aucun accès réseau à l'exécution.
import { cpSync, mkdirSync, readdirSync, writeFileSync } from 'node:fs';

const root = new URL('../', import.meta.url);
const out = new URL('public/engine/', root);
mkdirSync(out, { recursive: true });
const copy = (from, to = from.split('/').pop()) => cpSync(new URL(from, root), new URL(to, out));

for (const f of ['pyodide.mjs', 'pyodide.asm.mjs', 'pyodide.asm.wasm', 'python_stdlib.zip', 'pyodide-lock.json']) copy('node_modules/pyodide/' + f);
copy('node_modules/brotli-wasm/pkg.web/brotli_wasm.js', 'brotli_wasm.js');
copy('node_modules/brotli-wasm/pkg.web/brotli_wasm_bg.wasm', 'brotli_wasm_bg.wasm');
const wheels = readdirSync(new URL('engine/vendor/', root)).filter((f) => f.endsWith('.whl'));
for (const f of wheels) copy('engine/vendor/' + f);
copy('engine/fontaine_engine.py');
copy('engine/brotli_shim.py');
writeFileSync(new URL('engine.json', out), JSON.stringify({ wheels, modules: ['brotli_shim.py', 'fontaine_engine.py'] }, null, 2));
console.log('moteur copié dans public/engine');
