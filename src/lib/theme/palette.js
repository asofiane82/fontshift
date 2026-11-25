/*
 * Fontshift — palettes et tokens sémantiques.
 * Source unique des couleurs : 5 thèmes × 2 apparences (un par famille : or, bleu, vert, rouge, violet),
 * mêmes clés, couleurs en aplat (sans dégradé).
 * Chaque thème part d'un trio (couleur profonde, accent, neutre clair) :
 *   clair  : fond = blanc cassé teinté par le thème (sans dominante jaune), boutons = couleur profonde
 *            (or pour Champagne, bleu électrique pour Navy), surlignages = accent ;
 *   sombre : fonds = couleur profonde assombrie, texte = neutre, boutons = accent.
 * Nuances dérivées et contrastes (WCAG) calculés par design/brand/themes_build.py (ajustements validés compris) :
 * textes ≥ 4,5:1, contours des éléments cliquables (borderStrong) ≥ 3:1.
 * scripts/build-tokens.mjs en dérive src/styles/tokens.css (propriétés --ftn-*).
 */
var BASE = {
  champagne: {
    name: 'Champagne & Encre',
    trio: { deep: '#16140F', accent: '#DDB66E', neutral: '#FCF8EF' },
    light: {
      sidebar: '#EEECE9', background: '#FAF8F6', surface: '#FDFDFC', surfaceSunken: '#F3F1EE', surfaceElevated: '#FFFFFF', border: '#D4D2CF',
      borderStrong: '#8F8D89', textPrimary: '#16140F', textSecondary: '#57554F', textTertiary: '#6B6962', ornament: '#7C570C',
      specimen: '#16140F', badge: '#F3E8D3', disabled: '#A7A49D', success: '#05704E', warning: '#965200', error: '#B42318', tabbar: '#EEECE9',
      tabActive: '#FDFDFC', accent: '#B5863A', accentHover: '#C99A45', accentOn: '#16140F', tint: '#F3E8D3', tintStrong: '#F1E9DA',
      tintSoft: '#F9F7F2', focus: '#7C570C'
    },
    dark: {
      sidebar: '#0E0C08', background: '#16140F', surface: '#1E1C17', surfaceSunken: '#100F0A', surfaceElevated: '#26241F', border: '#302E28',
      borderStrong: '#6B6962', textPrimary: '#FCF8EF', textSecondary: '#BCB8B0', textTertiary: '#9B9891', ornament: '#DDB66E',
      specimen: '#FCF8EF', badge: '#403827', disabled: '#6D6B64', success: '#6FE3B5', warning: '#F7C27A', error: '#FFA897', tabbar: '#0E0C08',
      tabActive: '#26241F', accent: '#DDB66E', accentHover: '#EEC67E', accentOn: '#0E0C08', tint: '#403827', tintStrong: '#5B4D33',
      tintSoft: '#2F2A1F', focus: '#DDB66E'
    }
  },
  navy: {
    name: 'Navy & Electric Blue',
    trio: { deep: '#0F172A', accent: '#3B82F6', neutral: '#FFFFFF' },
    light: {
      sidebar: '#EEF4FF', background: '#FFFFFF', surface: '#FFFFFF', surfaceSunken: '#F8F8F8', surfaceElevated: '#FFFFFF', border: '#D3D9E5',
      borderStrong: '#8C93A2', textPrimary: '#0F172A', textSecondary: '#4C5569', textTertiary: '#646C7E', ornament: '#105BCF',
      specimen: '#0F172A', badge: '#E0EBFE', disabled: '#9FA5B2', success: '#05704E', warning: '#965200', error: '#B42318', tabbar: '#EEF4FF',
      tabActive: '#FFFFFF', accent: '#2563EB', accentHover: '#1D4ED8', accentOn: '#FFFFFF', tint: '#E0EBFE', tintStrong: '#C8DCFC',
      tintSoft: '#EFF5FE', focus: '#2563EB'
    },
    dark: {
      sidebar: '#080F21', background: '#0F172A', surface: '#171F33', surfaceSunken: '#0A1124', surfaceElevated: '#1F283C', border: '#283249',
      borderStrong: '#636C7F', textPrimary: '#FFFFFF', textSecondary: '#BCBEC3', textTertiary: '#9A9EA6', ornament: '#73A8FD',
      specimen: '#FFFFFF', badge: '#1D3156', disabled: '#6A6F7B', success: '#6FE3B5', warning: '#F7C27A', error: '#FFA897', tabbar: '#080F21',
      tabActive: '#1F283C', accent: '#3B82F6', accentHover: '#5394FD', accentOn: '#080F21', tint: '#1D3156', tintStrong: '#233F71',
      tintSoft: '#1A2845', focus: '#73A8FD'
    }
  },
  emerald: {
    name: 'Emerald & Mint',
    trio: { deep: '#065F46', accent: '#A7F3D0', neutral: '#FFF8E7' },
    light: {
      sidebar: '#E7EFEB', background: '#F5FAF7', surface: '#FCFDFD', surfaceSunken: '#ECF3F0', surfaceElevated: '#FFFFFF', border: '#CBD7D2',
      borderStrong: '#7D948C', textPrimary: '#00291C', textSecondary: '#435C51', textTertiary: '#566C62', ornament: '#065F46',
      specimen: '#00291C', badge: '#E5FAEB', disabled: '#99A9A2', success: '#05704E', warning: '#965200', error: '#B42318', tabbar: '#E7EFEB',
      tabActive: '#FCFDFD', accent: '#065F46', accentHover: '#01503A', accentOn: '#FFF8E7', tint: '#E5FAEB', tintStrong: '#CFF8E2',
      tintSoft: '#F1FBF1', focus: '#065F46'
    },
    dark: {
      sidebar: '#02100A', background: '#061811', surface: '#0E2019', surfaceSunken: '#03120C', surfaceElevated: '#162821', border: '#1E332B',
      borderStrong: '#5E6D62', textPrimary: '#FFF8E7', textSecondary: '#B9B9AB', textTertiary: '#969A8D', ornament: '#A7F3D0',
      specimen: '#FFF8E7', badge: '#2A463A', disabled: '#656D62', success: '#6FE3B5', warning: '#F7C27A', error: '#FFA897', tabbar: '#02100A',
      tabActive: '#162821', accent: '#A7F3D0', accentHover: '#97E2C0', accentOn: '#02100A', tint: '#2A463A', tintStrong: '#3F6454',
      tintSoft: '#1C3329', focus: '#A7F3D0'
    }
  },
  burgundy: {
    name: 'Burgundy & Blush',
    trio: { deep: '#7F1D1D', accent: '#F3D5D8', neutral: '#FFFDF7' },
    light: {
      sidebar: '#F9EFEE', background: '#FFFCFC', surface: '#FFFEFE', surfaceSunken: '#FAF5F4', surfaceElevated: '#FFFFFF', border: '#E2D5D4',
      borderStrong: '#A38C8B', textPrimary: '#3A1412', textSecondary: '#684E4B', textTertiary: '#7C6563', ornament: '#7F1D1D',
      specimen: '#3A1412', badge: '#FBF2F1', disabled: '#B1A09E', success: '#05704E', warning: '#965200', error: '#B42318', tabbar: '#F9EFEE',
      tabActive: '#FFFEFE', accent: '#7F1D1D', accentHover: '#6F080F', accentOn: '#FFFDF7', tint: '#FBF2F1', tintStrong: '#F8E7E8',
      tintSoft: '#FDF7F6', focus: '#7F1D1D'
    },
    dark: {
      sidebar: '#190605', background: '#210D0B', surface: '#2A1513', surfaceSunken: '#1B0807', surfaceElevated: '#331D1B', border: '#3F2624',
      borderStrong: '#796460', textPrimary: '#FFFDF7', textSecondary: '#C1BAB5', textTertiary: '#A29894', ornament: '#F3D5D8',
      specimen: '#FFFDF7', badge: '#4E3836', disabled: '#756865', success: '#6FE3B5', warning: '#F7C27A', error: '#FFA897', tabbar: '#190605',
      tabActive: '#331D1B', accent: '#F3D5D8', accentHover: '#FEE8EA', accentOn: '#190605', tint: '#4E3836', tintStrong: '#6A5252',
      tintSoft: '#3C2625', focus: '#F3D5D8'
    }
  },
  plum: {
    name: 'Plum & Lavender',
    trio: { deep: '#6D28D9', accent: '#C4B5FD', neutral: '#FAF7FF' },
    light: {
      sidebar: '#EFEBF6', background: '#FAF7FF', surface: '#FDFCFF', surfaceSunken: '#F3F0F8', surfaceElevated: '#FFFFFF', border: '#D7D2E0',
      borderStrong: '#918BA0', textPrimary: '#231B3C', textSecondary: '#565267', textTertiary: '#696679', ornament: '#6D28D9',
      specimen: '#231B3C', badge: '#ECE7FE', disabled: '#A5A3B0', success: '#05704E', warning: '#965200', error: '#B42318', tabbar: '#EFEBF6',
      tabActive: '#FDFCFF', accent: '#6D28D9', accentHover: '#6008C8', accentOn: '#FAF7FF', tint: '#ECE7FE', tintStrong: '#DED5FE',
      tintSoft: '#F4F1FF', focus: '#6D28D9'
    },
    dark: {
      sidebar: '#0D091A', background: '#141122', surface: '#1C192B', surfaceSunken: '#0F0B1C', surfaceElevated: '#242134', border: '#2E2A40',
      borderStrong: '#696679', textPrimary: '#FAF7FF', textSecondary: '#BAB7C1', textTertiary: '#9996A2', ornament: '#C4B5FD',
      specimen: '#FAF7FF', badge: '#3A3551', disabled: '#6B6876', success: '#6FE3B5', warning: '#F7C27A', error: '#FFA897', tabbar: '#0D091A',
      tabActive: '#242134', accent: '#C4B5FD', accentHover: '#D3C9FE', accentOn: '#0D091A', tint: '#3A3551', tintStrong: '#524B6E',
      tintSoft: '#2B273E', focus: '#C4B5FD'
    }
  }
};
var ORDER = ['champagne', 'navy', 'emerald', 'burgundy', 'plum'];

function hx(h) { return [parseInt(h.slice(1, 3), 16), parseInt(h.slice(3, 5), 16), parseInt(h.slice(5, 7), 16)]; }
function rgba(h, a) { var v = hx(h); return 'rgba(' + v[0] + ', ' + v[1] + ', ' + v[2] + ', ' + a + ')'; }
function lum(h) {
  var f = function (v) { v = v / 255; return v <= 0.03928 ? v / 12.92 : Math.pow((v + 0.055) / 1.055, 2.4); };
  var v = hx(h); return 0.2126 * f(v[0]) + 0.7152 * f(v[1]) + 0.0722 * f(v[2]);
}
function contrast(a, b) { var x = lum(a), y = lum(b); return (Math.max(x, y) + 0.05) / (Math.min(x, y) + 0.05); }

/* Tokens sémantiques : seule source de couleurs pour les composants. */
function tokens(theme, dark) {
  var P = BASE[theme] || BASE[DEFAULT_THEME], b = P[dark ? 'dark' : 'light'];
  var k = {
    background: b.background,
    backgroundFill: b.background,
    sidebar: b.sidebar,
    surface: b.surface,
    surfaceFill: b.surface,
    surfaceSunken: b.surfaceSunken,
    surfaceElevated: b.surfaceElevated,
    border: b.border,
    borderStrong: b.borderStrong,
    textPrimary: b.textPrimary,
    textSecondary: b.textSecondary,
    textTertiary: b.textTertiary,
    accent: b.accent,
    accentFill: b.accent,
    accentTop: b.accent, accentLow: b.accentHover,
    accentHover: b.accentHover,
    accentEdge: 'transparent',
    accentForeground: b.accentOn,
    accentText: b.ornament,
    accentLine: rgba(b.ornament, dark ? 0.6 : 0.5),
    accentDash: rgba(b.ornament, dark ? 0.6 : 0.5),
    hover: dark ? rgba(b.textPrimary, 0.05) : rgba(b.textPrimary, 0.04),
    selected: b.tint,
    selectedSoft: b.tintSoft,
    selectedStrong: b.tintStrong,
    focus: b.focus,
    disabled: b.disabled,
    success: b.success, successSoft: rgba(b.success, dark ? 0.14 : 0.1),
    warning: b.warning, warningSoft: rgba(b.warning, dark ? 0.14 : 0.09),
    error: b.error, errorSoft: rgba(b.error, dark ? 0.14 : 0.08), errorLine: rgba(b.error, 0.45),
    specimen: b.specimen,
    leader: rgba(b.textSecondary, 0.6),
    badge: b.badge,
    tabbar: b.tabbar,
    tabActive: b.tabActive,
    brandGold: dark ? '#DDB66E' : '#B8893A',
    shadow: dark ? '0 18px 40px rgba(0, 0, 0, 0.35)' : '0 16px 36px ' + rgba(b.textPrimary, 0.1),
    shadowSoft: dark ? 'none' : '0 1px 2px ' + rgba(b.textPrimary, 0.05),
    buttonShadow: 'none',
    codeKeyword: b.ornament, codeProperty: b.textPrimary, codeString: dark ? b.accent : b.ornament, codeText: b.textSecondary, codeComment: b.textTertiary,
    knob: dark ? b.textPrimary : '#FFFFFF',
    overlay: dark ? 'rgba(0, 0, 0, 0.5)' : rgba(b.textPrimary, 0.25)
  };
  return k;
}

var DEFAULT_THEME = 'champagne';
export { BASE, ORDER, tokens, contrast, rgba, DEFAULT_THEME };
export const themeName = (k) => (BASE[k] || BASE[DEFAULT_THEME]).name;
