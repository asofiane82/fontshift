# Fontshift — identité visuelle (logo n° 05, aplats) · version 4

Assets de marque intégrés dans l'application (icônes, logo de l'interface, favicons).

Version 4 : logotype en Instrument Sans 600, espacement affiné (approche −1 %, « Fo » resserré, « ft » séparé) ;
Syne est abandonnée, les titres de l'application passent en Inter comme le reste du texte.

Version 3 : l'application s'appelle Fontshift et le coin haut-droit
de la forme basse du F est affiné (environ 69° au lieu de 82°) : son bord droit penche dans le même sens
que l'extrémité de la barre or.

Changements de la version 2 par rapport à la version 1 :
- les deux formes du F sont nettement séparées, avec un écart constant de 4,5 % de la hauteur ;
- le vert est retiré : la forme haute est en or, la forme basse en encre sur fond clair et en ivoire sur fond sombre ;
- le logotype passe d'Urbanist à Syne 600.

## Fichiers

| Dossier | Contenu |
|---|---|
| `svg/` | Logos vectoriels (vrais tracés, aucune image incorporée) |
| `png/` | Logos 2400 px et monogrammes 1024 px, fond transparent |
| `macos/` | Icône 1024 px (SVG + PNG), `Fontshift.iconset` (16 à 1024 px), `Fontshift.icns` |
| `web/` | `favicon.svg`, `favicon.ico` (16/32/48), PNG 16/32/48, `apple-touch-icon.png`, `icon-192/512.png`, `site.webmanifest`, balises `head.html` |
| `preview/` | Planche d'identité, variantes de couleur du monogramme, planche des 6 thèmes (captures réelles, `e2e/themes_board.py`) et fichier JSON des thèmes |

Logos SVG : `fontshift-logo-{dark,light,black,white}.svg` (horizontal) et
`fontshift-monogram-{dark,light,black,white}.svg`. `fontshift-wordmark.svg` est le logotype seul
en `currentColor`, pour l'interface.

- `dark` : pour fonds sombres (or #DDB66E, ivoire #FCF8EF)
- `light` : pour fonds clairs (or profond #B8893A, encre #16140F)
- `black` / `white` : monochromes, avec le même écart entre les deux formes

## Règles

- Zone de protection : x = hauteur de la barre or, tout autour du logo.
- Tailles minimales : logo horizontal 24 px de haut, monogramme seul 16 px.
- Proportions : capitales du logotype = 0,365 × hauteur du monogramme ; écart monogramme / logotype = 0,168 × ;
  séparation des deux formes = 0,045 ×.
- Aplats uniquement : pas de dégradé, d'ombre ni de halo.
- L'icône macOS (pavé encre, F or et ivoire) reste identique quel que soit le thème de l'application.
- Dans l'interface, la forme basse et le logotype prennent la couleur du texte du thème, et la forme haute reste en or.

## Construction

La forme haute du monogramme est reprise sans modification du tracé validé (courbes de Bézier).
Le bord supérieur de la forme basse suit une courbe parallèle au bord inférieur de la forme haute,
à distance constante, jusqu'au contour gauche du F. Les autres bords conservent leurs courbes d'origine.
Le logotype est composé en Instrument Sans (SIL Open Font License 1.1, graisse 600, chevauchements supprimés,
espacement affiné),
puis converti en contours : aucune police n'est nécessaire pour afficher le logo.
