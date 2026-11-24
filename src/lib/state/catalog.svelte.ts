// Catalogue Google Fonts : métadonnées publiques, filtres, sélection et téléchargement
// des fichiers officiels (variables quand ils existent), puis ajout à la conversion.
import { httpFetch, isTauri } from '../platform';
import { session } from './session.svelte';

export type Category = 'sans' | 'serif' | 'display' | 'hand' | 'mono';
export interface Family {
  family: string;
  category: Category;
  axes: { tag: string; min: number; max: number }[];
  styles: number;
  popularity: number;
  previewWeight: string;
}

const CACHE_KEY = 'fontaine.gfCatalog';
const CACHE_DAYS = 7;
const METADATA_URL = 'https://fonts.google.com/metadata/fonts';
const LIST_URL = 'https://fonts.google.com/download/list?family=';
const CATEGORY: Record<string, Category> = {
  'Sans Serif': 'sans',
  Serif: 'serif',
  Display: 'display',
  Handwriting: 'hand',
  Monospace: 'mono',
};

/** Les réponses Google commencent parfois par « )]}' » (protection XSSI). */
function parseGoogleJson(text: string) {
  const start = text.indexOf('{');
  return JSON.parse(start > 0 ? text.slice(start) : text);
}

type RawFamily = {
  family: string;
  category?: string;
  axes?: { tag: string; min: number; max: number }[];
  fonts?: Record<string, unknown>;
  popularity?: number;
};

function slim(raw: RawFamily): Family {
  const keys = Object.keys(raw.fonts ?? {});
  const upright = keys.filter((k) => !k.endsWith('i')).map(Number).sort((a, b) => Math.abs(a - 400) - Math.abs(b - 400));
  return {
    family: raw.family,
    category: CATEGORY[raw.category ?? ''] ?? 'display',
    axes: (raw.axes ?? []).map((a) => ({ tag: a.tag, min: a.min, max: a.max })),
    styles: keys.length || 1,
    popularity: raw.popularity ?? 9999,
    previewWeight: String(upright[0] ?? 400),
  };
}

class Catalog {
  state = $state<'idle' | 'loading' | 'ready' | 'error' | 'unavailable'>('idle');
  families = $state<Family[]>([]);
  query = $state('');
  category = $state<'all' | Category>('all');
  variableOnly = $state(false);
  selected = $state<string[]>([]);
  limit = $state(60);
  download = $state<{ done: number; total: number; failed: string[] } | null>(null);

  get filtered() {
    const q = this.query.trim().toLowerCase();
    return this.families.filter(
      (f) => (this.category === 'all' || f.category === this.category) && (!this.variableOnly || f.axes.length > 0) && (!q || f.family.toLowerCase().includes(q)),
    );
  }

  async load(force = false) {
    if (!isTauri) {
      this.state = 'unavailable';
      return;
    }
    if (this.state === 'loading' || (this.state === 'ready' && !force)) return;
    if (!force) {
      try {
        const cached = JSON.parse(localStorage.getItem(CACHE_KEY) || 'null');
        if (cached && Date.now() - cached.at < CACHE_DAYS * 86_400_000 && cached.families?.length) {
          this.families = cached.families;
          this.state = 'ready';
          return;
        }
      } catch {
        /* cache illisible : on recharge */
      }
    }
    this.state = 'loading';
    try {
      const res = await httpFetch(METADATA_URL);
      if (!res.ok) throw new Error(String(res.status));
      const data = parseGoogleJson(await res.text());
      const list: Family[] = (data.familyMetadataList as RawFamily[]).map(slim).sort((a, b) => a.popularity - b.popularity);
      this.families = list;
      this.state = 'ready';
      try {
        localStorage.setItem(CACHE_KEY, JSON.stringify({ at: Date.now(), families: list }));
      } catch {
        /* quota dépassé : le catalogue reste en mémoire */
      }
    } catch {
      this.state = 'error';
    }
  }

  toggle(name: string) {
    this.selected = this.selected.includes(name) ? this.selected.filter((n) => n !== name) : [...this.selected, name];
  }

  resetFilters() {
    this.query = '';
    this.category = 'all';
    this.variableOnly = false;
    this.limit = 60;
  }

  /** Télécharge les familles choisies et les place dans la file de conversion. */
  async downloadSelected(): Promise<number> {
    const names = [...this.selected];
    if (!names.length || this.download) return 0;
    this.download = { done: 0, total: names.length, failed: [] };
    let added = 0;
    for (const name of names) {
      try {
        const res = await httpFetch(LIST_URL + encodeURIComponent(name));
        if (!res.ok) throw new Error(String(res.status));
        const manifest = parseGoogleJson(await res.text()).manifest;
        const refs: { filename: string; url: string }[] = (manifest.fileRefs ?? []).filter((r: { filename: string }) => /\.(ttf|otf)$/i.test(r.filename));
        const variable = refs.filter((r) => !r.filename.includes('static/'));
        const chosen = variable.length ? variable : refs;
        const files = [];
        for (const ref of chosen) {
          const r = await httpFetch(ref.url);
          if (!r.ok) throw new Error(String(r.status));
          files.push({ name: ref.filename.split('/').pop() || ref.filename, bytes: new Uint8Array(await r.arrayBuffer()) });
        }
        await session.addFiles(files, 'google');
        added += files.length;
      } catch {
        this.download.failed.push(name);
      }
      this.download.done += 1;
    }
    const failed = this.download.failed;
    this.selected = this.selected.filter((n) => failed.includes(n));
    this.download = failed.length ? { done: names.length, total: names.length, failed } : null;
    return added;
  }

  previewHref(f: Family, text: string) {
    const fam = encodeURIComponent(f.family).replace(/%20/g, '+');
    const weight = f.previewWeight === '400' ? '' : `:wght@${f.previewWeight}`;
    return `https://fonts.googleapis.com/css2?family=${fam}${weight}&text=${encodeURIComponent(text + f.family)}&display=swap`;
  }
}

export const catalog = new Catalog();
