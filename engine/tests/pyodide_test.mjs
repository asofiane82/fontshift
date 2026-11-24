// Test du moteur dans Pyodide (même environnement que l'application) : node engine/tests/pyodide_test.mjs
import { loadPyodide } from 'pyodide';
import { readFileSync, writeFileSync, mkdirSync } from 'node:fs';
import { createRequire } from 'node:module';
const require = createRequire(import.meta.url);
const brotli = require('brotli-wasm');
const here = new URL('.', import.meta.url).pathname;
const root = new URL('../', import.meta.url).pathname;

const t0 = Date.now();
globalThis.fontaineBrotli = {
  compress: (u8, quality) => brotli.compress(u8, { quality }),
  decompress: (u8) => brotli.decompress(u8),
};
const py = await loadPyodide({ indexURL: new URL('../../node_modules/pyodide/', import.meta.url).pathname });
const site = py.runPython('import site; site.getsitepackages()[0]');
py.unpackArchive(new Uint8Array(readFileSync(root + 'vendor/fonttools-4.62.1-py3-none-any.whl')), 'wheel');
py.FS.writeFile(site + '/brotli.py', readFileSync(root + 'brotli_shim.py'));
py.FS.writeFile(site + '/fontaine_engine.py', readFileSync(root + 'fontaine_engine.py'));
const E = py.pyimport('fontaine_engine');
console.log('chargement', Date.now() - t0, 'ms');

const toJs = (proxy) => proxy.toJs({ dict_converter: Object.fromEntries, create_pyproxies: false });
mkdirSync(here + 'out-pyodide', { recursive: true });
let ok = true;
for (const name of ['playfair-display-latin-wght-normal.woff2', 'playfair-display-latin-600-italic.woff2']) {
  const bytes = new Uint8Array(readFileSync(here + name));
  let t = Date.now();
  const info = toJs(E.open_faces(bytes, name));
  const face = info.faces[0];
  console.log(name, face.family, face.style, face.axes.map((a) => a.tag), 'analyse', Date.now() - t, 'ms');
  t = Date.now();
  const res = toJs(E.convert(bytes, name, JSON.stringify({ formats: ['woff2', 'woff', 'ttf', 'otf', 'eot'], variable: 'keep', subset: 'full' })));
  if (res.error) { ok = false; console.log('ERREUR', res); continue; }
  for (const o of res.outputs) { writeFileSync(here + 'out-pyodide/' + o.name, o.data); }
  console.log('  ', res.outputs.map((o) => `${o.name} ${o.size}`).join(' | '), 'avert.', res.warnings.map((w) => w.code), Date.now() - t, 'ms');
  ok = ok && res.outputs.length > 0 && res.outputs[0].data instanceof Uint8Array;
}
let t = Date.now();
const res = toJs(E.convert(new Uint8Array(readFileSync(here + 'playfair-display-latin-wght-normal.woff2')), 'p.woff2', JSON.stringify({ formats: ['woff2'], variable: 'static' })));
console.log('instances statiques', res.outputs?.length, Date.now() - t, 'ms');
ok = ok && res.outputs?.length === 6;
console.log('RESULT', ok ? 'PASS' : 'FAIL');
