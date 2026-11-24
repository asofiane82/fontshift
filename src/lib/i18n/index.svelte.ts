// Traductions centralisées (messages ICU) et formats localisés.
import { IntlMessageFormat } from 'intl-messageformat';
import fr from './locales/fr.json';
import en from './locales/en.json';
import es from './locales/es.json';
import { prefs, type Lang } from '../prefs.svelte';

const MESSAGES: Record<Lang, Record<string, unknown>> = { fr, en, es };
const cache = new Map<string, IntlMessageFormat>();

function lookup(lang: Lang, key: string): string | undefined {
  const v = key.split('.').reduce<unknown>((o, k) => (o && typeof o === 'object' ? (o as Record<string, unknown>)[k] : undefined), MESSAGES[lang]);
  return typeof v === 'string' ? v : undefined;
}

/** t('conv.cta', { count: 4 }) — repli sur l'anglais, puis sur la clé. */
export function t(key: string, vars?: Record<string, string | number>): string {
  const lang = prefs.resolvedLang;
  const src = lookup(lang, key) ?? lookup('en', key);
  if (src === undefined) return key;
  if (!vars && !src.includes('{')) return src;
  const id = lang + '\u0000' + key;
  let mf = cache.get(id);
  if (!mf) {
    mf = new IntlMessageFormat(src, lang);
    cache.set(id, mf);
  }
  return String(mf.format(vars ?? {}));
}

export const fmt = {
  num(n: number, digits = 0) {
    return new Intl.NumberFormat(prefs.resolvedLang, { maximumFractionDigits: digits }).format(n);
  },
  /** Taille de fichier en octets → « 727 ko », « 1,6 Mo », « 727 kB »… */
  size(bytes: number) {
    const lang = prefs.resolvedLang;
    if (bytes < 1000) return new Intl.NumberFormat(lang, { style: 'unit', unit: 'byte' }).format(bytes);
    if (bytes < 1_000_000)
      return new Intl.NumberFormat(lang, { style: 'unit', unit: 'kilobyte', maximumFractionDigits: 0 }).format(bytes / 1000);
    return new Intl.NumberFormat(lang, { style: 'unit', unit: 'megabyte', maximumFractionDigits: 1 }).format(bytes / 1_000_000);
  },
  pct(x: number) {
    return new Intl.NumberFormat(prefs.resolvedLang, { style: 'percent', signDisplay: 'exceptZero', maximumFractionDigits: 0 }).format(x);
  },
  list(items: string[]) {
    return new Intl.ListFormat(prefs.resolvedLang, { style: 'long', type: 'conjunction' }).format(items);
  },
};
