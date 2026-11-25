// Identité Fontshift dans l'interface : une seule source, les fichiers de design/brand.
// Géométrie vectorielle (monogramme séparé + logotype Instrument Sans 600 en contours) produite par
// design/brand/source/build_brand.py ; l'icône d'application est le même SVG que l'icône macOS.
import geometry from '../../../design/brand/source/brand-geometry.json';
import appIconSvg from '../../../design/brand/macos/fontshift-app-icon.svg?raw';

export const MONOGRAM = geometry.monogram; // { w, h, upper, lower } — hauteur 100
export const WORDMARK = geometry.wordmark; // { d, x, capTop, baseline, w } — dans le repère du logo
export const LOGO = geometry.logo; // { w, h }
export const BRAND_COLORS = geometry.colors;

/** Icône d'application (pavé encre, F or et ivoire), identique quel que soit le thème. */
export const APP_ICON_SVG = appIconSvg.replace(/<\?xml[^>]*>\s*/, '').replace(/<title>[^<]*<\/title>\s*/, '');
