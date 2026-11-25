# Fontshift

Application de bureau légère (macOS, Windows, Linux) pour convertir des polices :
TTF, OTF, WOFF, WOFF2 et EOT, polices variables comprises, avec import depuis Google Fonts
et génération du CSS `@font-face`. Identité visuelle : logo n° 05 « Futuriste & Fluide » (monogramme F
or et encre, logotype Syne). Anciennement « Fontaine » (renommée en 1.5.0). 5 thèmes en aplats (Champagne & Encre par défaut, puis Navy, Emerald, Burgundy et Plum) en clair et en sombre,
en français, anglais et espagnol.

## Ce que fait l'application

- **Conversion** : glisser-déposer sur toute la fenêtre ou bouton « Parcourir », file d'attente,
  aperçu de la police (lignes de référence réelles, détails, caractères), styles à générer pour les
  polices variables (fichier variable et/ou Regular, Italic, Bold… en fichiers séparés), formats de sortie,
  options, progression, annulation immédiate.
  - Entrées : TTF, OTF (CFF et CFF2), WOFF, WOFF2, TTC/OTC (chaque police de la collection
    devient une entrée), EOT non compressé. Type 1 et EOT compressé sont refusés avec un message clair.
  - Sorties : WOFF2, WOFF, TTF (CFF → TrueType par cu2qu), OTF (TrueType → CFF, conversion exacte),
    EOT 2.1 (Internet Explorer).
  - Polices variables : « Styles à générer » — le fichier variable et/ou chaque style choisi
    (Regular, Italic, Bold…), droit ou italique, en fichiers séparés.
    Une police variable ne peut pas sortir en OTF (CFF2 non généré) ; l'EOT est produit depuis
    l'instance par défaut. Ces deux cas sont signalés dans les Résultats.
  - Jeux de caractères : complet, latin, latin étendu (plages de Google Fonts) ou liste personnalisée.
  - Fichier `fontshift-fonts.css` prêt à intégrer, dossier de destination au choix
    (par défaut `Bureau/Fontshift`). Chaque conversion range ses fichiers dans un sous-dossier
    au nom des polices (`Fontshift/Montserrat`, puis `Montserrat (2)`…) ; rien n'est écrasé.
- **Google Fonts** : catalogue officiel (mis en cache 7 jours), recherche, catégories,
  filtre « Variables uniquement », sélection multiple, téléchargement des fichiers officiels
  (variables quand ils existent) puis ajout à la conversion.
- **Aperçu avancé** (polices variables) : curseurs par axe, instances nommées, texte et taille d'aperçu,
  ligne CSS à copier, export de la police complète, d'une position précise ou de toutes les instances.
- **Résultats** : fichiers générés (taille et gain par format), code CSS et thème Tailwind v4,
  ouverture du dossier.
- **Réglages** (fenêtre séparée) : thème, apparence (clair, sombre, système) et langue
  (système, français, anglais, espagnol), indépendants, enregistrés automatiquement,
  appliqués aussitôt à toutes les fenêtres. Changer de langue n'interrompt pas une conversion.
- **Mises à jour automatiques** : voir plus bas. En veille tant qu'aucune adresse n'est configurée.

Toute la conversion est locale : seuls le catalogue Google Fonts et, une fois configurée,
la vérification des mises à jour utilisent le réseau.

## Architecture

```
src/                     Interface Svelte 5 + Tailwind CSS 4
  lib/theme/palette.js   Source unique des couleurs (5 thèmes × 2 apparences, aplats, tokens sémantiques)
  lib/brand/             Logo et icône dans l'interface, lus depuis design/brand (aucune copie des tracés)
  styles/tokens.css      Généré : propriétés --ftn-* sur :root[data-theme][data-mode]
  app.css                @theme inline : les classes Tailwind lisent les tokens (bg-surface, text-fg-muted…)
  lib/i18n/locales/      fr.json, en.json, es.json (messages ICU : pluriels et variables)
  lib/prefs.svelte.ts    Préférences thème / apparence / langue, détection du système, synchronisation
  lib/engine/            Worker Pyodide + client (file d'appels, annulation)
  lib/state/             Session de conversion, catalogue Google Fonts, navigation
  components/, screens/  Composants réutilisables et écrans (aucune couleur ni chaîne en dur)
engine/                  Moteur Python (fontTools) et ses tests
src-tauri/               Côté natif Rust minimal : lecture/écriture des fichiers, dossier par défaut, langue du système,
                         mises à jour (tauri-plugin-updater)
e2e/                     Test de bout en bout de l'application compilée (tauri-driver)
design/brand/            Assets de marque : SVG vectoriels, PNG, icône macOS (.icns), icône Windows/Linux,
                         favicons, planches ; source/ contient les scripts qui les génèrent
```

Le moteur est **fontTools exécuté par Pyodide** (CPython en WebAssembly) dans un Web Worker :
une seule implémentation, identique sur les trois systèmes, sans binaire Python à compiler
pour chaque plateforme. Tout est embarqué ; l'application ne télécharge rien pour convertir.

## Développer

Prérequis : Node 22, Rust stable, et sous Linux les bibliothèques WebKitGTK
([liste Tauri](https://tauri.app/start/prerequisites/)).

```bash
npm install
npm run tauri dev        # application de bureau avec rechargement à chaud
npm run dev              # interface seule dans le navigateur (sans Google Fonts ni accès disque)
```

Modifier les couleurs : `src/lib/theme/palette.js`, puis `npm run prepare:assets`
(régénère `tokens.css`). Les nuances dérivées et les contrastes des thèmes sont calculés par
`design/brand/source/themes_build.py` à partir des trios de couleurs (ajustements validés compris) ;
la planche des thèmes (`design/brand/preview/fontshift-themes.png`) est faite de captures réelles :
`python3 e2e/themes_board.py` après une compilation (mêmes prérequis que le test de bout en bout).

Régénérer la marque (Python 3, fontTools, uharfbuzz, shapely, numpy, rsvg-convert) :
`python3 design/brand/source/gen_wordmark.py && python3 design/brand/source/separate.py && python3 design/brand/source/build_brand.py`,
puis `npx tauri icon design/brand/desktop/fontshift-desktop-icon-1024.png -o src-tauri/icons` (supprimer
ensuite `android/` et `ios/`) et `icon.icns` depuis `design/brand/macos/Fontshift.icns` (l'icône macOS garde la marge du gabarit Apple). Ajouter une chaîne : la même clé dans les trois fichiers de `locales/`.

## Tester

```bash
npm run check            # types et composants Svelte
npm run test:engine      # moteur sous CPython (pip install fonttools brotli) puis sous Pyodide
cargo test --manifest-path src-tauri/Cargo.toml
python3 e2e/run.py       # Linux : Xvfb, webkit2gtk-driver, cargo install tauri-driver, pip install selenium
```

Le test de bout en bout ouvre l'application compilée, ajoute deux polices, lance la conversion,
vérifie les fichiers écrits sur le disque, parcourt les écrans, change le thème, l'apparence et la
langue dans la fenêtre Réglages et contrôle que la fenêtre principale suit. Les captures sont dans `e2e/shots/`.

## Construire les installeurs

```bash
npm run tauri build      # sur la machine cible : .dmg/.app (macOS), .msi/.exe (Windows), .deb/.rpm/.AppImage (Linux)
```

Avec GitHub : pousser une étiquette `v1.2.0` déclenche `.github/workflows/release.yml`, qui produit
les installeurs macOS (Apple Silicon et Intel), Windows et Linux dans un brouillon de publication.
Sans certificat Apple, macOS demandera d'ouvrir l'application via clic droit › Ouvrir la première fois ;
les secrets `APPLE_*` du workflow permettent la signature et la notarisation.

macOS 13 minimum (moteur WebAssembly dans WKWebView), Windows 10/11 (WebView2), Linux avec WebKitGTK 4.1.

## Publier et mettre à jour

La compilation (GitHub Actions › Publication › Run workflow) produit les installeurs des quatre
plateformes, puis le lot `fontshift-telechargements` : installeurs sous des noms fixes,
`version.json` et, quand tout est configuré, `latest.json` et les archives macOS de mise à jour.

**Mises à jour automatiques.** Au lancement, Fontshift lit `latest.json` ; si une version plus récente
existe, un bandeau discret s'affiche dans la barre latérale (et dans Réglages › À propos).
L'application télécharge la mise à jour, vérifie sa signature, l'installe puis redémarre.
macOS, Windows (installeur NSIS ou MSI) et Linux (AppImage, .deb et .rpm) sont pris en charge.

1. Adresse : renseigner l'URL complète de `latest.json` dans `src-tauri/tauri.conf.json` >
   `plugins.updater.endpoints` (HTTPS obligatoire). Les installeurs doivent être déposés dans le
   même dossier que `latest.json`. Tant que la liste est vide, aucune vérification n'a lieu
   et rien n'apparaît dans l'interface.
2. Clé de signature : secrets du dépôt `TAURI_SIGNING_PRIVATE_KEY` (contenu du fichier `.key`) et
   `TAURI_SIGNING_PRIVATE_KEY_PASSWORD`. La clé publique correspondante est dans `tauri.conf.json`.
   Sans ces secrets, la compilation fonctionne mais ne produit pas de fichiers de mise à jour.
   **Si la clé privée est perdue, les applications installées ne pourront plus être mises à jour.**
3. À chaque version : augmenter le numéro (package.json, tauri.conf.json, Cargo.toml), lancer la
   compilation, puis déposer tout le contenu du lot sur le site (installeurs, archives `.app.tar.gz`,
   `latest.json`).

**Signature macOS.** Avec les secrets `APPLE_CERTIFICATE` (certificat Developer ID Application en
base64), `APPLE_CERTIFICATE_PASSWORD`, `APPLE_SIGNING_IDENTITY` (« Developer ID Application: Nom (TEAMID) »),
`APPLE_ID`, `APPLE_PASSWORD` (mot de passe pour app) et `APPLE_TEAM_ID`, l'application est signée et
notarisée par Apple. Sans eux, elle reçoit une signature ad hoc (alerte au premier lancement).
