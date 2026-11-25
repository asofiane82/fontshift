// Préférences indépendantes et persistantes : thème, apparence, langue.
// Enregistrement automatique, synchronisation entre fenêtres, suivi du système en direct.
import { ORDER, DEFAULT_THEME } from './theme/palette.js';
import { broadcast, listenAll, systemLocales } from './platform';

export type ThemeKey = 'champagne' | 'navy' | 'emerald' | 'burgundy' | 'plum';
export type Appearance = 'light' | 'dark' | 'system';
export type Lang = 'fr' | 'en' | 'es';
export type LangPref = Lang | 'system';

export const THEMES = ORDER as ThemeKey[];
export const LANGS: Lang[] = ['fr', 'en', 'es'];
export const LANG_INFO: Record<Lang, { native: string; flag: 'fr' | 'gb' | 'es' }> = {
  fr: { native: 'Français', flag: 'fr' },
  en: { native: 'English', flag: 'gb' },
  es: { native: 'Español', flag: 'es' },
};
export const DEFAULTS = { theme: DEFAULT_THEME as ThemeKey, appearance: 'system' as Appearance, lang: 'system' as LangPref };

const KEYS = { theme: 'fontaine.theme', appearance: 'fontaine.appearance', lang: 'fontaine.lang' } as const;
type Key = keyof typeof KEYS;

function read<T extends string>(k: Key, allowed: readonly string[], fallback: T): T {
  try {
    const v = localStorage.getItem(KEYS[k]);
    return v && allowed.includes(v) ? (v as T) : fallback;
  } catch {
    return fallback;
  }
}

function detectLang(list: readonly string[] = navigator.languages?.length ? navigator.languages : [navigator.language]): Lang {
  for (const l of list) {
    const two = String(l || '').slice(0, 2).toLowerCase();
    if ((LANGS as string[]).includes(two)) return two as Lang;
  }
  return 'en';
}

class Prefs {
  theme = $state<ThemeKey>(read('theme', THEMES, DEFAULTS.theme));
  appearance = $state<Appearance>(read('appearance', ['light', 'dark', 'system'], DEFAULTS.appearance));
  lang = $state<LangPref>(read('lang', ['fr', 'en', 'es', 'system'], DEFAULTS.lang));
  systemDark = $state(true);
  systemLang = $state<Lang>(detectLang());

  get dark() {
    return this.appearance === 'system' ? this.systemDark : this.appearance === 'dark';
  }
  get resolvedLang(): Lang {
    return this.lang === 'system' ? this.systemLang : this.lang;
  }

  constructor() {
    const mq = window.matchMedia('(prefers-color-scheme: dark)');
    this.systemDark = mq.matches;
    mq.addEventListener('change', (e) => (this.systemDark = e.matches));
    window.addEventListener('languagechange', () => (this.systemLang = detectLang()));
    void systemLocales().then((list) => {
      if (list.length) this.systemLang = detectLang(list);
    });
    window.addEventListener('storage', (e) => {
      if (e.key?.startsWith('fontaine.')) this.reload();
    });
    void listenAll('fontaine:prefs', () => this.reload());
  }

  reload() {
    this.theme = read('theme', THEMES, DEFAULTS.theme);
    this.appearance = read('appearance', ['light', 'dark', 'system'], DEFAULTS.appearance);
    this.lang = read('lang', ['fr', 'en', 'es', 'system'], DEFAULTS.lang);
  }

  set<K extends Key>(k: K, v: Prefs[K]) {
    (this as Record<Key, unknown>)[k] = v;
    try {
      localStorage.setItem(KEYS[k], String(v));
    } catch {
      /* stockage indisponible : la préférence reste valable pour la session */
    }
    void broadcast('fontaine:prefs', { [k]: v });
  }

  reset() {
    try {
      for (const k of Object.values(KEYS)) localStorage.removeItem(k);
    } catch {
      /* rien à effacer */
    }
    this.theme = DEFAULTS.theme;
    this.appearance = DEFAULTS.appearance;
    this.lang = DEFAULTS.lang;
    void broadcast('fontaine:prefs', { reset: true });
  }
}

export const prefs = new Prefs();

/** Applique thème, apparence et langue au document (attributs lus par tokens.css). */
export function applyToDocument() {
  $effect(() => {
    const root = document.documentElement;
    root.dataset.theme = prefs.theme;
    root.dataset.mode = prefs.dark ? 'dark' : 'light';
    root.lang = prefs.resolvedLang;
  });
}
