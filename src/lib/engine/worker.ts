/// <reference lib="webworker" />
// Moteur de conversion : Pyodide (CPython en WebAssembly) + fontTools, isolé dans un worker
// pour que l'interface reste fluide. Tout est embarqué dans l'application, sans réseau.

type Py = {
  runPython: (code: string) => unknown;
  unpackArchive: (buf: Uint8Array, format: string) => void;
  FS: { writeFile: (path: string, data: string | Uint8Array) => void };
  pyimport: (name: string) => Record<string, (...args: unknown[]) => PyProxy>;
};
type PyProxy = { toJs: (o: object) => unknown; destroy: () => void };

const ctx = self as unknown as DedicatedWorkerGlobalScope;
const base = new URL('/engine/', ctx.location.href).href;
let engine: ReturnType<Py['pyimport']> | null = null;

async function boot() {
  const manifest = await (await fetch(base + 'engine.json')).json();
  const brotli = await import(/* @vite-ignore */ base + 'brotli_wasm.js');
  await brotli.default(base + 'brotli_wasm_bg.wasm');
  (ctx as unknown as Record<string, unknown>).fontaineBrotli = {
    compress: (u8: Uint8Array, quality: number) => brotli.compress(u8, { quality }),
    decompress: (u8: Uint8Array) => brotli.decompress(u8),
  };
  const { loadPyodide } = await import(/* @vite-ignore */ base + 'pyodide.mjs');
  const py: Py = await loadPyodide({ indexURL: base, stdout: () => {}, stderr: () => {} });
  for (const wheel of manifest.wheels as string[]) {
    py.unpackArchive(new Uint8Array(await (await fetch(base + wheel)).arrayBuffer()), 'wheel');
  }
  const site = py.runPython('import site; site.getsitepackages()[0]') as string;
  py.FS.writeFile(site + '/brotli.py', await (await fetch(base + 'brotli_shim.py')).text());
  py.FS.writeFile(site + '/fontaine_engine.py', await (await fetch(base + 'fontaine_engine.py')).text());
  engine = py.pyimport('fontaine_engine');
}

const ready = boot().then(
  () => ctx.postMessage({ type: 'status', state: 'ready' }),
  (err) => {
    ctx.postMessage({ type: 'status', state: 'error', detail: String(err?.message ?? err) });
    throw err;
  },
);

function toPlain(proxy: PyProxy) {
  const value = proxy.toJs({ dict_converter: Object.fromEntries, create_pyproxies: false });
  proxy.destroy();
  return value as Record<string, unknown>;
}

/** Rassemble les ArrayBuffer à transférer (sans copie) vers l'interface. */
function transferables(value: unknown, acc: ArrayBuffer[] = []): ArrayBuffer[] {
  if (value instanceof Uint8Array) acc.push(value.buffer as ArrayBuffer);
  else if (Array.isArray(value)) value.forEach((v) => transferables(v, acc));
  else if (value && typeof value === 'object') Object.values(value).forEach((v) => transferables(v, acc));
  return acc;
}

ctx.onmessage = async (e: MessageEvent) => {
  const { id, op, bytes, filename, options } = e.data;
  try {
    await ready;
    const fn = engine![op === 'open' ? 'open_faces' : op === 'merge' ? 'merge' : 'convert'];
    // Fusion : bytes et filename sont des listes (un fichier par graisse).
    const args = op === 'open' ? [bytes, filename] : [bytes, filename, JSON.stringify(options)];
    const result = toPlain(fn(...args));
    ctx.postMessage({ id, ok: true, result }, transferables(result));
  } catch (err) {
    ctx.postMessage({ id, ok: false, error: String((err as Error)?.message ?? err) });
  }
};
