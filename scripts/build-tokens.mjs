// Génère src/styles/tokens.css à partir de src/lib/theme/palette.js (source unique des couleurs).
// Chaque combinaison thème × apparence devient un bloc :root[data-theme][data-mode] de propriétés --ftn-*.
import { writeFileSync } from 'node:fs';
import { ORDER, tokens } from '../src/lib/theme/palette.js';

const kebab = (k) => k.replace(/[A-Z]/g, (m) => '-' + m.toLowerCase());
let css = '/* Fichier généré par scripts/build-tokens.mjs : ne pas modifier à la main. */\n';
for (const theme of ORDER) {
  for (const dark of [true, false]) {
    const t = tokens(theme, dark);
    css += `\n:root[data-theme="${theme}"][data-mode="${dark ? 'dark' : 'light'}"] {\n  color-scheme: ${dark ? 'dark' : 'light'};\n`;
    for (const [k, v] of Object.entries(t)) css += `  --ftn-${kebab(k)}: ${v};\n`;
    css += '}\n';
  }
}
writeFileSync(new URL('../src/styles/tokens.css', import.meta.url), css);
console.log(`tokens.css : ${ORDER.length * 2} jeux de valeurs`);
