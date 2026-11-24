// Code d'intégration : règles @font-face et thème Tailwind v4 à partir des fichiers produits.
import type { SavedOutput } from './state/session.svelte';

const FORMAT_CSS: Record<string, string> = {
  woff2: 'woff2',
  woff: 'woff',
  ttf: 'truetype',
  otf: 'opentype',
};
const ORDER = ['woff2', 'woff', 'ttf', 'otf'];

export interface FaceRule {
  family: string;
  weight: string;
  stretch: string;
  fontStyle: string;
  files: Record<string, string>; // format → nom de fichier
}

/** Regroupe les formats d'une même police (même nom de base). */
export function faceRules(outputs: SavedOutput[]): FaceRule[] {
  const byStem = new Map<string, FaceRule>();
  for (const o of outputs) {
    const key = o.stem + '\u0000' + o.family;
    let rule = byStem.get(key);
    if (!rule) {
      rule = { family: o.family, weight: o.weight, stretch: o.stretch, fontStyle: o.fontStyle, files: {} };
      byStem.set(key, rule);
    }
    rule.files[o.format] = o.name;
  }
  return [...byStem.values()];
}

const q = (s: string) => '"' + s.replace(/"/g, '\\"') + '"';

export function cssForRule(r: FaceRule): string {
  const lines = ['@font-face {', `  font-family: ${q(r.family)};`];
  const srcs: string[] = [];
  if (r.files.eot) {
    lines.push(`  src: url(${q('./' + r.files.eot)});`);
    srcs.push(`url(${q('./' + r.files.eot + '?#iefix')}) format("embedded-opentype")`);
  }
  for (const f of ORDER) if (r.files[f]) srcs.push(`url(${q('./' + r.files[f])}) format(${q(FORMAT_CSS[f])})`);
  lines.push('  src: ' + srcs.join(',\n       ') + ';');
  lines.push(`  font-weight: ${r.weight};`);
  if (r.stretch) lines.push(`  font-stretch: ${r.stretch};`);
  if (r.fontStyle && r.fontStyle !== 'normal') lines.push(`  font-style: ${r.fontStyle};`);
  lines.push('  font-display: swap;', '}');
  return lines.join('\n');
}

export function buildCss(outputs: SavedOutput[]): string {
  const rules = faceRules(outputs);
  return ['/* Fontaine · fontaine-fonts.css */', '', ...rules.map(cssForRule).flatMap((r) => [r, ''])].join('\n').trimEnd() + '\n';
}

export const slug = (s: string) => s.toLowerCase().normalize('NFD').replace(/[̀-ͯ]/g, '').replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '');

/** Thème Tailwind v4 : une variable --font-* par famille, puis un exemple d'usage Twig. */
export function tailwindSnippet(outputs: SavedOutput[], twigComment: string): string {
  const families = [...new Set(outputs.map((o) => o.family))];
  const first = families[0] ? slug(families[0]) : 'sans';
  return [
    '@import "tailwindcss";',
    '@import "./fontaine-fonts.css";',
    '',
    '@theme {',
    ...families.map((f) => `  --font-${slug(f)}: ${q(f)}, sans-serif;`),
    '}',
    '',
    `{# ${twigComment} #}`,
    `<h1 class="font-${first} font-semibold">…</h1>`,
  ].join('\n');
}

export type Token = { k: 'k' | 'p' | 's' | 'x' | 'm'; text: string };

/** Coloration minimale (CSS et Twig) pour l'affichage du code. */
export function highlight(code: string): Token[][] {
  return code.split('\n').map((line) => {
    if (/^\s*(\/\*|\{#)/.test(line)) return [{ k: 'm', text: line }];
    const out: Token[] = [];
    const re = /(@[\w-]+)|("[^"]*")|(^\s*[\w-]+(?=\s*:))|(class(?==))|([^@"]+?(?=@|"|$))/g;
    let m: RegExpExecArray | null;
    let last = 0;
    while ((m = re.exec(line))) {
      if (m.index > last) out.push({ k: 'x', text: line.slice(last, m.index) });
      if (m[1]) out.push({ k: 'k', text: m[1] });
      else if (m[2]) out.push({ k: 's', text: m[2] });
      else if (m[3] || m[4]) out.push({ k: 'p', text: m[3] || m[4] });
      else out.push({ k: 'x', text: m[0] });
      last = re.lastIndex;
      if (m[0] === '') re.lastIndex++;
    }
    if (last < line.length) out.push({ k: 'x', text: line.slice(last) });
    return out.length ? out : [{ k: 'x', text: ' ' }];
  });
}
