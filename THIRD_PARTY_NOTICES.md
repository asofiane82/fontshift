# Composants tiers embarqués

| Composant | Rôle | Licence |
|---|---|---|
| [Tauri](https://tauri.app) 2 et ses extensions dialog, http, opener, updater | fenêtre native, accès aux fichiers, réseau | MIT ou Apache-2.0 |
| [Pyodide](https://pyodide.org) | CPython compilé en WebAssembly (moteur) | MPL-2.0 |
| [fontTools](https://github.com/fonttools/fonttools) | lecture, conversion, sous-ensembles, instances | MIT |
| [brotli-wasm](https://github.com/httptoolkit/brotli-wasm) | compression Brotli du WOFF2 | Apache-2.0 |
| [Svelte](https://svelte.dev) 5, [Vite](https://vite.dev), [Tailwind CSS](https://tailwindcss.com) 4 | interface | MIT |
| [intl-messageformat](https://formatjs.github.io) | messages ICU (pluriels, variables) | BSD-3-Clause |
| [Heroicons](https://heroicons.com) 2 | icônes | MIT |
| [Inter](https://rsms.me/inter/), [Instrument Sans](https://fonts.google.com/specimen/Instrument+Sans), [JetBrains Mono](https://www.jetbrains.com/lp/mono/) (via Fontsource) | Inter et JetBrains Mono : polices de l'interface ; Instrument Sans 600 : logotype, converti en contours (aucune police chargée par l'application) | SIL OFL 1.1 |
| [Playfair Display](https://github.com/clauseggers/Playfair) | contours du spécimen anatomique « Ag » (src/lib/glyphs.ts) | SIL OFL 1.1 |
| [sys-locale](https://github.com/1Password/sys-locale) | langue du système | MIT ou Apache-2.0 |

Les polices de test de `engine/tests/` (Inter, Playfair Display) sont sous SIL OFL 1.1.
