// Fabrique latest.json (manifeste des mises à jour automatiques) à partir des installeurs du lot
// « téléchargements » et de leurs signatures. L'adresse des fichiers est celle du latest.json
// déclaré dans src-tauri/tauri.conf.json (plugins.updater.endpoints) : sans adresse, rien n'est créé.
// Usage : node scripts/latest-json.mjs <dossier des installeurs> <dossier des signatures .sig>
import { existsSync, readFileSync, writeFileSync } from 'node:fs';
import { join } from 'node:path';

const [dir = 'telechargements', sigDir = 'signatures'] = process.argv.slice(2);
const conf = JSON.parse(readFileSync(new URL('../src-tauri/tauri.conf.json', import.meta.url)));
const endpoint = conf.plugins?.updater?.endpoints?.[0];
if (!endpoint) {
  console.log('latest.json : aucune adresse de mise à jour configurée, fichier non créé.');
  process.exit(0);
}
const base = new URL('.', endpoint);

// Cible du programme de mise à jour → fichier du lot (la première entrée d'un fichier sert aussi de repli « os-arch »).
const TARGETS = [
  ['darwin-aarch64-app', 'Fontshift-macOS-Apple-Silicon.app.tar.gz'],
  ['darwin-aarch64', 'Fontshift-macOS-Apple-Silicon.app.tar.gz'],
  ['darwin-x86_64-app', 'Fontshift-macOS-Intel.app.tar.gz'],
  ['darwin-x86_64', 'Fontshift-macOS-Intel.app.tar.gz'],
  ['windows-x86_64-nsis', 'Fontshift-Windows.exe'],
  ['windows-x86_64', 'Fontshift-Windows.exe'],
  ['windows-x86_64-msi', 'Fontshift-Windows.msi'],
  ['linux-x86_64-appimage', 'Fontshift-Linux.AppImage'],
  ['linux-x86_64', 'Fontshift-Linux.AppImage'],
  ['linux-x86_64-deb', 'Fontshift-Linux.deb'],
  ['linux-x86_64-rpm', 'Fontshift-Linux.rpm'],
];

const platforms = {};
for (const [target, file] of TARGETS) {
  const sig = join(sigDir, file + '.sig');
  if (!existsSync(join(dir, file)) || !existsSync(sig)) continue;
  platforms[target] = { signature: readFileSync(sig, 'utf8').trim(), url: new URL(encodeURIComponent(file), base).href };
}
if (!Object.keys(platforms).length) {
  console.log('latest.json : aucune signature trouvée (clé de mise à jour absente ?), fichier non créé.');
  process.exit(0);
}
const pkg = JSON.parse(readFileSync(new URL('../package.json', import.meta.url)));
const manifest = { version: pkg.version, pub_date: new Date().toISOString().replace(/\.\d{3}Z$/, 'Z'), platforms };
writeFileSync(join(dir, 'latest.json'), JSON.stringify(manifest, null, 2) + '\n');
console.log(`latest.json : ${pkg.version}, ${Object.keys(platforms).length} cibles, fichiers attendus dans ${base.href}`);
