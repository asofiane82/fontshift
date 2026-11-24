/*
 * Fontshift — palettes et tokens sémantiques.
 * Source unique des couleurs : 8 thèmes × 2 apparences, mêmes clés, couleurs en aplat (sans dégradé).
 * Chaque thème part d'un trio (couleur profonde, accent, neutre clair) :
 *   clair  : fond = neutre, boutons = couleur profonde, surlignages = accent ;
 *   sombre : fonds = couleur profonde assombrie, texte = neutre, boutons = accent.
 * Nuances dérivées et contrastes (WCAG) calculés par design/brand/themes_build.py.
 * scripts/build-tokens.mjs en dérive src/styles/tokens.css (propriétés --ftn-*).
 */
var BASE = {
  champagne: {
    name: 'Champagne & Encre',
    trio: { deep: '#16140F', accent: '#DDB66E', neutral: '#FCF8EF' },
    light: {
      sidebar: '#F0ECE3', background: '#FCF8EF', surface: '#FEFDF9', surfaceSunken: '#F5F1E8', surfaceElevated: '#FFFFFF', border: '#D6D2CA',
      borderStrong: '#BCB8B0', textPrimary: '#16140F', textSecondary: '#57554F', textTertiary: '#6B6962', ornament: '#7C570C',
      specimen: '#16140F', badge: '#F9F2E3', disabled: '#A7A49D', success: '#05704E', warning: '#965200', error: '#B42318', tabbar: '#F0ECE3',
      tabActive: '#FEFDF9', accent: '#16140F', accentHover: '#26241F', accentOn: '#FCF8EF', tint: '#F9F2E3', tintStrong: '#F5E9D2',
      tintSoft: '#FBF7EE', focus: '#7C570C'
    },
    dark: {
      sidebar: '#0E0C08', background: '#16140F', surface: '#1E1C17', surfaceSunken: '#100F0A', surfaceElevated: '#26241F', border: '#302E28',
      borderStrong: '#45433C', textPrimary: '#FCF8EF', textSecondary: '#BCB8B0', textTertiary: '#9B9891', ornament: '#DDB66E',
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
      borderStrong: '#B8BFCC', textPrimary: '#0F172A', textSecondary: '#4C5569', textTertiary: '#646C7E', ornament: '#105BCF',
      specimen: '#0F172A', badge: '#E0EBFE', disabled: '#9FA5B2', success: '#05704E', warning: '#965200', error: '#B42318', tabbar: '#EEF4FF',
      tabActive: '#FFFFFF', accent: '#0F172A', accentHover: '#1F283C', accentOn: '#FFFFFF', tint: '#E0EBFE', tintStrong: '#C8DCFC',
      tintSoft: '#EFF5FE', focus: '#3B82F6'
    },
    dark: {
      sidebar: '#080F21', background: '#0F172A', surface: '#171F33', surfaceSunken: '#0A1124', surfaceElevated: '#1F283C', border: '#283249',
      borderStrong: '#3C475F', textPrimary: '#FFFFFF', textSecondary: '#BCBEC3', textTertiary: '#9A9EA6', ornament: '#73A8FD',
      specimen: '#FFFFFF', badge: '#1D3156', disabled: '#6A6F7B', success: '#6FE3B5', warning: '#F7C27A', error: '#FFA897', tabbar: '#080F21',
      tabActive: '#1F283C', accent: '#3B82F6', accentHover: '#5394FD', accentOn: '#080F21', tint: '#1D3156', tintStrong: '#233F71',
      tintSoft: '#1A2845', focus: '#73A8FD'
    }
  },
  charcoal: {
    name: 'Charcoal & Lime',
    trio: { deep: '#1F2937', accent: '#A3E635', neutral: '#F3F4F6' },
    light: {
      sidebar: '#E2E9F3', background: '#F3F4F6', surface: '#FBFBFC', surfaceSunken: '#ECEDEF', surfaceElevated: '#FFFFFF', border: '#CBD2DC',
      borderStrong: '#B3BBC6', textPrimary: '#1F2937', textSecondary: '#4B5666', textTertiary: '#5B6777', ornament: '#416504',
      specimen: '#1F2937', badge: '#E1F5C0', disabled: '#9DA5B1', success: '#05704E', warning: '#965200', error: '#B42318', tabbar: '#E2E9F3',
      tabActive: '#FBFBFC', accent: '#1F2937', accentHover: '#303B4A', accentOn: '#F3F4F6', tint: '#E1F5C0', tintStrong: '#CBEF8F',
      tintSoft: '#EDF8DC', focus: '#416504'
    },
    dark: {
      sidebar: '#17202E', background: '#1F2937', surface: '#273240', surfaceSunken: '#192331', surfaceElevated: '#303B4A', border: '#394556',
      borderStrong: '#4F5B6D', textPrimary: '#F1F2F4', textSecondary: '#D1D5DA', textTertiary: '#A8ADB4', ornament: '#A3E635',
      specimen: '#F1F2F4', badge: '#3D523E', disabled: '#6F757F', success: '#6FE3B5', warning: '#F7C27A', error: '#FFA897', tabbar: '#17202E',
      tabActive: '#303B4A', accent: '#A3E635', accentHover: '#B3F74C', accentOn: '#17202E', tint: '#3D523E', tintStrong: '#4F6C3C',
      tintSoft: '#32423F', focus: '#A3E635'
    }
  },
  emerald: {
    name: 'Emerald & Mint',
    trio: { deep: '#065F46', accent: '#A7F3D0', neutral: '#FFF8E7' },
    light: {
      sidebar: '#F3ECDB', background: '#FFF8E7', surface: '#FFFDF7', surfaceSunken: '#F8F1E0', surfaceElevated: '#FFFFFF', border: '#D6D5C4',
      borderStrong: '#B9BDAD', textPrimary: '#00291C', textSecondary: '#435C51', textTertiary: '#566C62', ornament: '#065F46',
      specimen: '#00291C', badge: '#E5FAEB', disabled: '#99A9A2', success: '#05704E', warning: '#965200', error: '#B42318', tabbar: '#F3ECDB',
      tabActive: '#FFFDF7', accent: '#065F46', accentHover: '#01503A', accentOn: '#FFF8E7', tint: '#E5FAEB', tintStrong: '#CFF8E2',
      tintSoft: '#F1FBF1', focus: '#065F46'
    },
    dark: {
      sidebar: '#02100A', background: '#061811', surface: '#0E2019', surfaceSunken: '#03120C', surfaceElevated: '#162821', border: '#1E332B',
      borderStrong: '#33483F', textPrimary: '#FFF8E7', textSecondary: '#B9B9AB', textTertiary: '#969A8D', ornament: '#A7F3D0',
      specimen: '#FFF8E7', badge: '#2A463A', disabled: '#656D62', success: '#6FE3B5', warning: '#F7C27A', error: '#FFA897', tabbar: '#02100A',
      tabActive: '#162821', accent: '#A7F3D0', accentHover: '#97E2C0', accentOn: '#02100A', tint: '#2A463A', tintStrong: '#3F6454',
      tintSoft: '#1C3329', focus: '#A7F3D0'
    }
  },
  burgundy: {
    name: 'Burgundy & Blush',
    trio: { deep: '#7F1D1D', accent: '#F3D5D8', neutral: '#FFFDF7' },
    light: {
      sidebar: '#FCEEEC', background: '#FFFDF7', surface: '#FFFEFC', surfaceSunken: '#F8F6F0', surfaceElevated: '#FFFFFF', border: '#E5D4D2',
      borderStrong: '#CDBAB8', textPrimary: '#3A1412', textSecondary: '#684E4B', textTertiary: '#7C6563', ornament: '#7F1D1D',
      specimen: '#3A1412', badge: '#FBF2F1', disabled: '#B1A09E', success: '#05704E', warning: '#965200', error: '#B42318', tabbar: '#FCEEEC',
      tabActive: '#FFFEFC', accent: '#7F1D1D', accentHover: '#6F080F', accentOn: '#FFFDF7', tint: '#FBF2F1', tintStrong: '#F8E7E8',
      tintSoft: '#FDF7F6', focus: '#7F1D1D'
    },
    dark: {
      sidebar: '#190605', background: '#210D0B', surface: '#2A1513', surfaceSunken: '#1B0807', surfaceElevated: '#331D1B', border: '#3F2624',
      borderStrong: '#553B38', textPrimary: '#FFFDF7', textSecondary: '#C1BAB5', textTertiary: '#A29894', ornament: '#F3D5D8',
      specimen: '#FFFDF7', badge: '#4E3836', disabled: '#756865', success: '#6FE3B5', warning: '#F7C27A', error: '#FFA897', tabbar: '#190605',
      tabActive: '#331D1B', accent: '#F3D5D8', accentHover: '#FEE8EA', accentOn: '#190605', tint: '#4E3836', tintStrong: '#6A5252',
      tintSoft: '#3C2625', focus: '#F3D5D8'
    }
  },
  teal: {
    name: 'Teal & Coral',
    trio: { deep: '#0F766E', accent: '#FF7F50', neutral: '#F5E6CA' },
    light: {
      sidebar: '#EBDCC0', background: '#F5E6CA', surface: '#FCF6EC', surfaceSunken: '#EEDFC3', surfaceElevated: '#FFFFFF', border: '#CFC6AD',
      borderStrong: '#B3B19B', textPrimary: '#022825', textSecondary: '#36534F', textTertiary: '#496360', ornament: '#0B5F59',
      specimen: '#022825', badge: '#FCE3D3', disabled: '#97A9A7', success: '#0E6C4C', warning: '#8E4D03', error: '#B42318', tabbar: '#EBDCC0',
      tabActive: '#FCF6EC', accent: '#0F766E', accentHover: '#0B665F', accentOn: '#FFFFFF', tint: '#FCE3D3', tintStrong: '#FDD5C0',
      tintSoft: '#FCECE0', focus: '#0B5F59'
    },
    dark: {
      sidebar: '#00100E', background: '#041816', surface: '#0B201E', surfaceSunken: '#011210', surfaceElevated: '#132826', border: '#1B3330',
      borderStrong: '#304845', textPrimary: '#F5E6CA', textSecondary: '#BBB5A1', textTertiary: '#969584', ornament: '#FF7F50',
      specimen: '#F5E6CA', badge: '#373127', disabled: '#60665A', success: '#6FE3B5', warning: '#F7C27A', error: '#FFA897', tabbar: '#00100E',
      tabActive: '#132826', accent: '#FF7F50', accentHover: '#FC9D7B', accentOn: '#00100E', tint: '#373127', tintStrong: '#593E2E',
      tintSoft: '#212922', focus: '#FF7F50'
    }
  },
  plum: {
    name: 'Plum & Lavender',
    trio: { deep: '#6D28D9', accent: '#C4B5FD', neutral: '#FAF7FF' },
    light: {
      sidebar: '#EFEBF6', background: '#FAF7FF', surface: '#FDFCFF', surfaceSunken: '#F3F0F8', surfaceElevated: '#FFFFFF', border: '#D7D2E0',
      borderStrong: '#BEB9C9', textPrimary: '#231B3C', textSecondary: '#565267', textTertiary: '#696679', ornament: '#6D28D9',
      specimen: '#231B3C', badge: '#ECE7FE', disabled: '#A5A3B0', success: '#05704E', warning: '#965200', error: '#B42318', tabbar: '#EFEBF6',
      tabActive: '#FDFCFF', accent: '#6D28D9', accentHover: '#6008C8', accentOn: '#FAF7FF', tint: '#ECE7FE', tintStrong: '#DED5FE',
      tintSoft: '#F4F1FF', focus: '#6D28D9'
    },
    dark: {
      sidebar: '#0D091A', background: '#141122', surface: '#1C192B', surfaceSunken: '#0F0B1C', surfaceElevated: '#242134', border: '#2E2A40',
      borderStrong: '#433F55', textPrimary: '#FAF7FF', textSecondary: '#BAB7C1', textTertiary: '#9996A2', ornament: '#C4B5FD',
      specimen: '#FAF7FF', badge: '#3A3551', disabled: '#6B6876', success: '#6FE3B5', warning: '#F7C27A', error: '#FFA897', tabbar: '#0D091A',
      tabActive: '#242134', accent: '#C4B5FD', accentHover: '#D3C9FE', accentOn: '#0D091A', tint: '#3A3551', tintStrong: '#524B6E',
      tintSoft: '#2B273E', focus: '#C4B5FD'
    }
  },
  terracotta: {
    name: 'Terracotta & Mustard',
    trio: { deep: '#C2410C', accent: '#EAB308', neutral: '#FFF7E6' },
    light: {
      sidebar: '#F3EBDA', background: '#FFF7E6', surface: '#FFFCF6', surfaceSunken: '#F8F0DF', surfaceElevated: '#FFFFFF', border: '#DDD1C1',
      borderStrong: '#C6B8A8', textPrimary: '#39160A', textSecondary: '#674F47', textTertiary: '#79635C', ornament: '#A83706',
      specimen: '#39160A', badge: '#FCF0D0', disabled: '#B0A19B', success: '#05704E', warning: '#965200', error: '#B42318', tabbar: '#F3EBDA',
      tabActive: '#FFFCF6', accent: '#C2410C', accentHover: '#AA390B', accentOn: '#FFF7E6', tint: '#FCF0D0', tintStrong: '#F9E8B3',
      tintSoft: '#FDF6E3', focus: '#A83706'
    },
    dark: {
      sidebar: '#180703', background: '#210E08', surface: '#2A160F', surfaceSunken: '#1B0804', surfaceElevated: '#331E17', border: '#3F271F',
      borderStrong: '#553B33', textPrimary: '#FFF7E6', textSecondary: '#C1B6A8', textTertiary: '#A29589', ornament: '#EAB308',
      specimen: '#FFF7E6', badge: '#4D320E', disabled: '#75675C', success: '#6FE3B5', warning: '#F7C27A', error: '#FFA897', tabbar: '#180703',
      tabActive: '#331E17', accent: '#EAB308', accentHover: '#FBC32F', accentOn: '#180703', tint: '#4D320E', tintStrong: '#67480D',
      tintSoft: '#3B240E', focus: '#EAB308'
    }
  }
};
var ORDER = ['champagne', 'navy', 'charcoal', 'emerald', 'burgundy', 'teal', 'plum', 'terracotta'];

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
