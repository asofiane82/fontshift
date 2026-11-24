// Session de conversion : file des polices, options, exécution et résultats.
// L'état vit ici, hors des composants : changer de langue ou d'écran n'interrompt rien.
import { engine } from '../engine/client.svelte';
import type { ConvertOptions, ConvertResult, FaceInfo, Format, NamedInstance, OutputFile } from '../engine/types';
import { defaultOutputDir, homeDir, prepareOutputDir, readPath, writeOutput, type PickedFile } from '../platform';
import { buildCss } from '../css';

export type Subset = 'full' | 'latin' | 'latinExt' | 'custom';
export type ExportSpec = { kind: 'auto' } | { kind: 'keep' } | { kind: 'all' } | { kind: 'instance'; instance: NamedInstance };

export interface RunState {
  state: 'waiting' | 'running' | 'done' | 'failed';
  progress: number;
  error?: string;
  outputs?: SavedOutput[];
  gain?: number;
}

export interface FontItem {
  id: string;
  fileName: string;
  path?: string;
  source: 'local' | 'google';
  bytes: Uint8Array;
  size: number;
  status: 'analysing' | 'ready' | 'error';
  error?: string;
  info?: FaceInfo;
  previewFamily?: string;
  exportSpec: ExportSpec;
  run?: RunState;
}

export interface SavedOutput extends Omit<OutputFile, 'data'> {
  path: string;
  sourceId: string;
  sourceName: string;
  sourceSize: number;
  previewFamily?: string;
}

export interface RunResults {
  outputs: SavedOutput[];
  sources: { id: string; name: string; family: string; size: number; previewFamily?: string }[];
  warnings: { code: string; file: string }[];
  failures: { name: string; error: string }[];
  dest: string;
  cssPath?: string;
  css?: string;
  finishedAt: number;
}

const OPTIONS_KEY = 'fontaine.options';
const ERROR_KEYS: Record<string, string> = {
  type1: 'conv.errorType1',
  unknownFormat: 'conv.errorUnknown',
  corrupt: 'conv.errorCorrupt',
  eotCompressed: 'conv.errorEotCompressed',
  convertFailed: 'conv.errorConvert',
  noFormat: 'conv.errorConvert',
};

let counter = 0;
const uid = () => `f${Date.now().toString(36)}${(++counter).toString(36)}`;

/** Graisses standard proposées pour les polices variables (noms repris dans les fichiers). */
export const WEIGHTS: { value: number; name: string }[] = [
  { value: 100, name: 'Thin' },
  { value: 200, name: 'ExtraLight' },
  { value: 300, name: 'Light' },
  { value: 400, name: 'Regular' },
  { value: 500, name: 'Medium' },
  { value: 600, name: 'SemiBold' },
  { value: 700, name: 'Bold' },
  { value: 800, name: 'ExtraBold' },
  { value: 900, name: 'Black' },
];

/** Style à générer : « variable » (le fichier variable complet) ou une graisse, droite ou italique (« 700i »). */
export type StyleKey = string;
export const styleKey = (weight: number, italic: boolean): StyleKey => `${weight}${italic ? 'i' : ''}`;
export function styleName(weight: number, italic: boolean) {
  const name = WEIGHTS.find((w) => w.value === weight)?.name ?? String(weight);
  return italic ? (weight === 400 ? 'Italic' : `${name} Italic`) : name;
}

/** Ce qu'une police variable sait produire : plage de graisse, versions droite et italique. */
function capability(info: FaceInfo) {
  const axis = (tag: string) => info.axes.find((a) => a.tag === tag);
  const wght = axis('wght'), ital = axis('ital'), slnt = axis('slnt');
  const slanted = !!ital || !!slnt;
  return {
    min: wght ? wght.min : 400,
    max: wght ? wght.max : 400,
    upright: !info.italic || slanted,
    italic: info.italic || slanted,
    coords(weight: number, italic: boolean): Record<string, number> {
      const c: Record<string, number> = {};
      if (wght) c.wght = weight;
      if (ital) c.ital = italic ? ital.max : ital.min;
      else if (slnt) c.slnt = italic ? slnt.min : Math.min(Math.max(0, slnt.min), slnt.max);
      return c;
    },
  };
}

/** Nom du sous-dossier d'une conversion : les familles, dans l'ordre de la liste (3 au plus, puis « + N »). */
function folderName(items: FontItem[]) {
  const families = [...new Set(items.map((i) => (i.info?.family || i.fileName.replace(/\.[^.]+$/, '')).trim()))].filter(Boolean);
  if (!families.length) return 'Fontaine';
  const shown = families.slice(0, 3).join(' + ');
  return families.length > 3 ? `${shown} + ${families.length - 3}` : shown;
}

function loadOptions() {
  try {
    return JSON.parse(localStorage.getItem(OPTIONS_KEY) || '{}');
  } catch {
    return {};
  }
}

class Session {
  items = $state<FontItem[]>([]);
  selectedId = $state<string | null>(null);

  formats = $state<Record<Format, boolean>>({ woff2: true, woff: true, ttf: false, otf: false, eot: false });
  styles = $state<StyleKey[]>(['variable']);
  subset = $state<Subset>('full');
  customText = $state('');
  css = $state(true);
  dest = $state('');
  home = $state('');

  phase = $state<'idle' | 'running' | 'done'>('idle');
  progress = $state({ done: 0, total: 0 });
  results = $state<RunResults | null>(null);
  unseen = $state(false);
  toast = $state<{ kind: 'done' | 'error' | 'cancelled' | 'added'; count: number; failed?: number } | null>(null);

  private cancelled = false;
  private ticker: ReturnType<typeof setInterval> | null = null;

  constructor() {
    const o = loadOptions();
    if (o.formats) this.formats = { ...this.formats, ...o.formats };
    if (Array.isArray(o.styles) && o.styles.length) this.styles = o.styles;
    if (o.subset) this.subset = o.subset;
    if (typeof o.customText === 'string') this.customText = o.customText;
    if (typeof o.css === 'boolean') this.css = o.css;
    if (o.dest) this.dest = o.dest;
    void homeDir().then((h) => (this.home = h));
    if (!this.dest) void defaultOutputDir().then((d) => (this.dest = d));
  }

  saveOptions() {
    const { formats, styles, subset, customText, css, dest } = this;
    try {
      localStorage.setItem(OPTIONS_KEY, JSON.stringify({ formats, styles, subset, customText, css, dest }));
    } catch {
      /* options gardées pour la session */
    }
  }

  get selected() {
    return this.items.find((i) => i.id === this.selectedId) ?? this.items.find((i) => i.status === 'ready') ?? null;
  }
  get ready() {
    return this.items.filter((i) => i.status === 'ready');
  }
  get totalSize() {
    return this.ready.reduce((a, i) => a + i.size, 0);
  }
  get chosenFormats(): Format[] {
    return (['woff2', 'woff', 'ttf', 'otf', 'eot'] as Format[]).filter((f) => this.formats[f]);
  }
  get displayDest() {
    return this.home && this.dest.startsWith(this.home) ? '~' + this.dest.slice(this.home.length) : this.dest;
  }

  /** Sous-dossier où ira la prochaine conversion (« Montserrat », « Montserrat (2) »…), affiché dans Destination. */
  nextFolder = $state('');
  get folderLabel() {
    return this.ready.length ? folderName(this.ready) : '';
  }
  async refreshNextFolder() {
    const name = this.folderLabel, base = this.dest;
    // Conversion terminée : on montre le dossier où les fichiers viennent d'être enregistrés.
    if (this.phase === 'done' && this.results?.dest && this.results.dest !== base) {
      this.nextFolder = this.results.dest.split(/[\\/]/).pop() || name;
      return;
    }
    if (!name || !base) {
      this.nextFolder = '';
      return;
    }
    try {
      const dir = await prepareOutputDir(base, name);
      this.nextFolder = dir === base ? name : dir.split(/[\\/]/).pop() || name;
    } catch {
      this.nextFolder = name;
    }
  }

  /** Ajoute ou retire un style ; au moins un reste choisi. */
  toggleStyle(k: StyleKey) {
    const next = this.styles.includes(k) ? this.styles.filter((x) => x !== k) : [...this.styles, k];
    if (!next.length) return;
    this.styles = next;
    this.saveOptions();
  }

  /** Polices variables de la liste concernées par le choix des styles. */
  get variableItems() {
    return this.ready.filter((i) => i.info?.variable && i.exportSpec.kind === 'auto');
  }

  /** Styles que les polices variables de la liste savent produire, par graisse. */
  get styleChoices(): { weight: number; name: string; upright: boolean; italic: boolean }[] {
    const caps = this.variableItems.map((i) => capability(i.info!));
    return WEIGHTS.map((w) => {
      const fits = caps.filter((c) => w.value >= c.min && w.value <= c.max);
      return { weight: w.value, name: w.name, upright: fits.some((c) => c.upright), italic: fits.some((c) => c.italic) };
    }).filter((w) => w.upright || w.italic);
  }

  toggleFormat(f: Format) {
    const next = { ...this.formats, [f]: !this.formats[f] };
    if (!Object.values(next).some(Boolean)) return;
    this.formats = next;
    this.saveOptions();
  }

  async addPaths(paths: string[]) {
    const files: PickedFile[] = [];
    for (const p of paths) {
      try {
        files.push(await readPath(p));
      } catch {
        const id = uid();
        this.items.push({ id, fileName: p.split(/[\\/]/).pop() || p, path: p, source: 'local', bytes: new Uint8Array(), size: 0, status: 'error', error: 'conv.errorRead', exportSpec: { kind: 'auto' } });
      }
    }
    return this.addFiles(files);
  }

  /** Ajoute des fichiers ; une collection TTC donne une entrée par police. */
  async addFiles(files: PickedFile[], source: 'local' | 'google' = 'local') {
    if (this.phase === 'done') this.phase = 'idle';
    const added: string[] = [];
    for (const file of files) {
      const id = uid();
      this.items.push({ id, fileName: file.name, path: file.path, source, bytes: file.bytes, size: file.bytes.length, status: 'analysing', exportSpec: { kind: 'auto' } });
      added.push(id);
      void this.analyse(id);
    }
    if (!this.selectedId && added.length) this.selectedId = added[0];
    return added;
  }

  private patch(id: string, fn: (item: FontItem) => void) {
    const item = this.items.find((i) => i.id === id);
    if (item) fn(item);
  }

  private async analyse(id: string) {
    const item = this.items.find((i) => i.id === id);
    if (!item) return;
    try {
      const res = await engine.open(item.bytes, item.fileName);
      if (res.error || !res.faces?.length) {
        this.patch(id, (i) => {
          i.status = 'error';
          i.error = ERROR_KEYS[res.error ?? 'corrupt'] ?? 'conv.errorCorrupt';
        });
        return;
      }
      const [first, ...rest] = res.faces;
      await this.setFace(id, first);
      // Collection : les polices suivantes deviennent des entrées distinctes.
      const index = this.items.findIndex((i) => i.id === id);
      rest.forEach((face, n) => {
        const extra: FontItem = {
          id: uid(),
          fileName: `${item.fileName} · ${face.fullName || face.family}`,
          path: item.path,
          source: item.source,
          bytes: face.extracted ?? item.bytes,
          size: face.extracted?.length ?? item.size,
          status: 'analysing',
          exportSpec: { kind: 'auto' },
        };
        this.items.splice(index + 1 + n, 0, extra);
        void this.setFace(extra.id, face);
      });
    } catch (err) {
      if ((err as Error).message === 'cancelled') return void this.analyse(id);
      this.patch(id, (i) => {
        i.status = 'error';
        i.error = engine.state === 'error' ? 'conv.errorEngine' : 'conv.errorCorrupt';
      });
    }
  }

  private async setFace(id: string, face: FaceInfo) {
    const extracted = face.extracted;
    delete face.extracted;
    let previewFamily: string | undefined;
    const item = this.items.find((i) => i.id === id);
    if (!item) return;
    const bytes = extracted ?? item.bytes;
    try {
      const name = 'ftn-' + id;
      const ff = new FontFace(name, bytes.slice().buffer as ArrayBuffer);
      await ff.load();
      document.fonts.add(ff);
      previewFamily = name;
    } catch {
      previewFamily = undefined;
    }
    this.patch(id, (i) => {
      i.info = face;
      i.bytes = bytes;
      i.status = 'ready';
      i.previewFamily = previewFamily;
      if (extracted && i.fileName.endsWith('.eot')) i.size = item.size;
    });
  }

  remove(id: string) {
    this.items = this.items.filter((i) => i.id !== id);
    if (this.selectedId === id) this.selectedId = this.items[0]?.id ?? null;
  }

  clear() {
    if (this.phase === 'running') this.cancel();
    this.items = [];
    this.selectedId = null;
    this.phase = 'idle';
  }

  newSession() {
    this.clear();
    this.toast = null;
  }

  /** Ajout depuis l'écran Polices variables : même police, export choisi. */
  addDerived(sourceId: string, spec: ExportSpec) {
    const src = this.items.find((i) => i.id === sourceId);
    if (!src?.info) return;
    if (src.exportSpec.kind === 'auto' && !src.run) {
      src.exportSpec = spec;
      this.selectedId = src.id;
      return;
    }
    const copy: FontItem = { ...src, id: uid(), exportSpec: spec, run: undefined, info: src.info };
    this.items.splice(this.items.indexOf(src) + 1, 0, copy);
    this.selectedId = copy.id;
    if (this.phase === 'done') this.phase = 'idle';
  }

  /** Une ou deux conversions par police : le fichier variable et/ou les styles statiques choisis. */
  private jobsFor(item: FontItem): ConvertOptions[] {
    const spec = item.exportSpec;
    const base: ConvertOptions = {
      formats: this.chosenFormats,
      variable: 'keep',
      subset: this.subset,
      customText: this.customText,
      stem: item.fileName.replace(/\.[^.]+$/, '').replace(/ · .*$/, ''),
    };
    if (spec.kind === 'all') return [{ ...base, variable: 'static' }];
    if (spec.kind === 'instance') return [{ ...base, instances: [spec.instance] }];
    if (spec.kind !== 'auto' || !item.info?.variable) return [base];

    const cap = capability(item.info);
    const instances = WEIGHTS.flatMap((w) =>
      [false, true]
        .filter((it) => this.styles.includes(styleKey(w.value, it)))
        .filter((it) => w.value >= cap.min && w.value <= cap.max && (it ? cap.italic : cap.upright))
        .map((it) => ({ name: styleName(w.value, it), coords: cap.coords(w.value, it) })),
    );
    const jobs: ConvertOptions[] = [];
    if (this.styles.includes('variable')) jobs.push(base);
    if (instances.length) jobs.push({ ...base, variable: 'static', instances });
    return jobs.length ? jobs : [base]; // aucun style choisi n'existe dans cette police : fichier variable
  }

  async start() {
    if (this.phase === 'running') return;
    const queue = this.ready;
    if (!queue.length) return;
    this.saveOptions();
    this.cancelled = false;
    this.phase = 'running';
    this.toast = null;
    this.progress = { done: 0, total: queue.length };
    for (const item of queue) item.run = { state: 'waiting', progress: 0 };
    // Chaque conversion range ses fichiers dans un sous-dossier au nom des polices (« Montserrat », « Roboto + Bitter »…).
    let dest = this.dest;
    try {
      dest = await prepareOutputDir(this.dest, folderName(queue));
    } catch {
      /* dossier de destination tel quel */
    }
    const results: RunResults = { outputs: [], sources: [], warnings: [], failures: [], dest, finishedAt: 0 };

    for (const item of queue) {
      if (this.cancelled) break;
      const live = this.items.find((i) => i.id === item.id);
      if (!live) continue;
      live.run = { state: 'running', progress: 0 };
      this.animate(live);
      try {
        const outputs: NonNullable<ConvertResult['outputs']> = [];
        const warnings: NonNullable<ConvertResult['warnings']> = [];
        for (const job of this.jobsFor(live)) {
          const res = await engine.convert(live.bytes, live.fileName, job);
          if (this.cancelled) break;
          if (res.error || !res.outputs) throw new Error(ERROR_KEYS[res.error ?? 'convertFailed'] ?? 'conv.errorConvert');
          outputs.push(...res.outputs);
          warnings.push(...(res.warnings ?? []));
        }
        if (this.cancelled) break;
        const saved: SavedOutput[] = [];
        for (const out of outputs) {
          let path: string;
          try {
            path = await writeOutput(dest, out.name, out.data);
          } catch {
            throw new Error('conv.errorWrite');
          }
          const { data: _data, ...meta } = out;
          saved.push({ ...meta, name: path.split(/[\\/]/).pop() || out.name, path, sourceId: live.id, sourceName: live.fileName, sourceSize: live.size, previewFamily: live.previewFamily });
        }
        results.outputs.push(...saved);
        results.warnings.push(...warnings);
        results.sources.push({ id: live.id, name: live.fileName, family: live.info?.family ?? live.fileName, size: live.size, previewFamily: live.previewFamily });
        const primary = saved.find((o) => o.format === 'woff2') ?? saved[0];
        live.run = { state: 'done', progress: 1, outputs: saved, gain: primary ? primary.size / live.size - 1 : 0 };
      } catch (err) {
        if (this.cancelled || (err as Error).message === 'cancelled') break;
        const key = (err as Error).message.startsWith('conv.') ? (err as Error).message : 'conv.errorConvert';
        live.run = { state: 'failed', progress: 0, error: key };
        results.failures.push({ name: live.fileName, error: key });
      } finally {
        this.stopAnimation();
      }
      this.progress = { done: this.progress.done + 1, total: queue.length };
    }

    if (this.cancelled) {
      for (const i of this.items) if (i.run && i.run.state !== 'done' && i.run.state !== 'failed') i.run = undefined;
      this.phase = 'idle';
      this.toast = { kind: 'cancelled', count: 0 };
      return;
    }

    if (this.css && results.outputs.length) {
      const css = buildCss(results.outputs);
      results.css = css;
      try {
        results.cssPath = await writeOutput(dest, 'fontaine-fonts.css', new TextEncoder().encode(css));
      } catch {
        results.failures.push({ name: 'fontaine-fonts.css', error: 'conv.errorWrite' });
      }
    } else if (results.outputs.length) {
      results.css = buildCss(results.outputs);
    }
    results.finishedAt = Date.now();
    this.results = results;
    this.unseen = true;
    this.phase = 'done';
    this.toast = { kind: results.failures.length ? 'error' : 'done', count: results.sources.length, failed: results.failures.length };
  }

  /** Progression estimée pendant qu'une police est traitée par le moteur. */
  private animate(item: FontItem) {
    const t0 = Date.now();
    const expected = 900 + (item.size / 1000) * 6 * Math.max(1, this.chosenFormats.length);
    this.ticker = setInterval(() => {
      const live = this.items.find((i) => i.id === item.id);
      if (!live?.run || live.run.state !== 'running') return;
      const x = (Date.now() - t0) / expected;
      live.run.progress = Math.min(0.95, 1 - Math.exp(-2.2 * x));
    }, 80);
  }

  private stopAnimation() {
    if (this.ticker) clearInterval(this.ticker);
    this.ticker = null;
  }

  cancel() {
    if (this.phase !== 'running') return;
    this.cancelled = true;
    this.stopAnimation();
    engine.cancel();
  }

  replay() {
    for (const i of this.items) i.run = undefined;
    this.phase = 'idle';
    this.toast = null;
  }
}

export const session = new Session();
