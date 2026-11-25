"""Thèmes Fontshift en aplats, reconstruits à partir des trios de couleurs choisis par Sofiane.

Chaque thème = un trio (couleur profonde, couleur d'accent, neutre clair) décliné en clair et en sombre :
  clair  : fond = neutre du trio, boutons = couleur profonde, surlignages = accent ;
  sombre : fonds = nuances très sombres de la couleur profonde, texte = neutre, boutons = accent.
Les couleurs du trio sont reprises telles quelles ; seules les nuances dérivées (fonds, bordures,
textes secondaires) et, si besoin, une variante plus foncée ou plus claire pour la lisibilité sont calculées.
Les clés de sortie sont celles de src/lib/theme/palette.js (BASE / METAL) pour l'intégration.
"""
import json, math
import os
HERE = os.path.dirname(os.path.abspath(__file__))   # design/brand/source

# ------------------------------------------------------------------ OKLab / OKLCH
def _lin(c): return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4
def _gam(c): return 12.92 * c if c <= 0.0031308 else 1.055 * c ** (1 / 2.4) - 0.055
def hex2rgb(h): h = h.lstrip('#'); return [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
def rgb2hex(c): return '#' + ''.join(f'{round(min(1, max(0, v)) * 255):02X}' for v in c)

def to_oklch(h):
    r, g, b = (_lin(v) for v in hex2rgb(h))
    l = (0.4122214708 * r + 0.5363325363 * g + 0.0514459929 * b) ** (1 / 3)
    m = (0.2119034982 * r + 0.6806995451 * g + 0.1073969566 * b) ** (1 / 3)
    s = (0.0883024619 * r + 0.2817188376 * g + 0.6299787005 * b) ** (1 / 3)
    L = 0.2104542553 * l + 0.7936177850 * m - 0.0040720468 * s
    A = 1.9779984951 * l - 2.4285922050 * m + 0.4505937099 * s
    B = 0.0259040371 * l + 0.7827717662 * m - 0.8086757660 * s
    return L, math.hypot(A, B), math.degrees(math.atan2(B, A)) % 360

def _raw(L, C, H):
    A, B = C * math.cos(math.radians(H)), C * math.sin(math.radians(H))
    l = (L + 0.3963377774 * A + 0.2158037573 * B) ** 3
    m = (L - 0.1055613458 * A - 0.0638541728 * B) ** 3
    s = (L - 0.0894841775 * A - 1.2914855480 * B) ** 3
    return [4.0767416621 * l - 3.3077115913 * m + 0.2309699292 * s,
            -1.2684380046 * l + 2.6097574011 * m - 0.3413193965 * s,
            -0.0041960863 * l - 0.7034186147 * m + 1.7076147010 * s]

def oklch(L, C, H):
    for _ in range(60):                                    # réduit la saturation jusqu'à rentrer dans le gamut sRGB
        rgb = _raw(L, C, H)
        if all(-1e-4 <= v <= 1 + 1e-4 for v in rgb): break
        C *= 0.95
    return rgb2hex([_gam(min(1, max(0, v))) for v in rgb])

def lum(h):
    r, g, b = (_lin(v) for v in hex2rgb(h)); return 0.2126 * r + 0.7152 * g + 0.0722 * b

def cr(a, b):
    x, y = lum(a), lum(b); return (max(x, y) + 0.05) / (min(x, y) + 0.05)

def mix(a, b, t):
    A, B = hex2rgb(a), hex2rgb(b); return rgb2hex([x + (y - x) * t for x, y in zip(A, B)])

def shade(h, L=None, C=None, dL=0.0, cmax=None):
    l, c, hh = to_oklch(h)
    l = L if L is not None else l + dL
    c = C if C is not None else c
    if cmax is not None: c = min(c, cmax)
    return oklch(max(0, min(1, l)), c, hh)

def readable(color, against, target, direction):
    """Assombrit (direction -1) ou éclaircit (+1) une couleur jusqu'au contraste visé sur toutes les surfaces données."""
    c = color
    for _ in range(80):
        if min(cr(c, a) for a in against) >= target: return c
        c = shade(c, dL=0.01 * direction)
    return c

# ------------------------------------------------------------------ trios
TRIOS = [
    # clé, nom, profonde, accent, neutre
    ('champagne', 'Champagne & Encre', '#16140F', '#DDB66E', '#FCF8EF'),
    ('navy', 'Navy & Electric Blue', '#0F172A', '#3B82F6', '#FFFFFF'),
    ('emerald', 'Emerald & Mint', '#065F46', '#A7F3D0', '#FFF8E7'),
    ('burgundy', 'Burgundy & Blush', '#7F1D1D', '#F3D5D8', '#FFFDF7'),
    ('rose', 'Raspberry & Rose', '#C71F72', '#F472B6', '#FFF7FB'),
    ('plum', 'Plum & Lavender', '#6D28D9', '#C4B5FD', '#FAF7FF'),
]
DEFAULT = 'champagne'
SEM = {'light': {'success': '#05704E', 'warning': '#965200', 'error': '#B42318'},
       'dark': {'success': '#6FE3B5', 'warning': '#F7C27A', 'error': '#FFA897'}}


# Ajustements validés (version 3 des thèmes, novembre 2026), appliqués après la dérivation automatique :
# - 8 thèmes ramenés à 5 (Charcoal, Teal et Terracotta retirés : quasi-doublons), puis Raspberry & Rose ajouté (rose vif) ;
# - modes clairs sans dominante jaune : fonds blancs cassés teintés par la couleur du thème (même luminosité,
#   saturation divisée par 3 à 4) ;
# - Champagne : accent or en clair (boutons #B5863A, texte des boutons en encre) ; Navy : bleu électrique #2563EB ;
# - borderStrong (contours des champs, menus et boutons de sélection) porté à 3:1 contre fond et carte.
AJUSTEMENTS = {
    'rose': {
        'light': {'background': '#FCF8F9', 'sidebar': '#F5EBEE', 'tabbar': '#F5EBEE', 'surfaceSunken': '#F6F1F2', 'surface': '#FEFDFD', 'tabActive': '#FEFDFD', 'border': '#DED1D6', 'borderStrong': '#9E8890'},
        'dark': {'borderStrong': '#786269'},
    },
    'champagne': {
        'light': {'sidebar': '#EEECE9', 'background': '#FAF8F6', 'surface': '#FDFDFC', 'surfaceSunken': '#F3F1EE', 'border': '#D4D2CF', 'borderStrong': '#8F8D89', 'badge': '#F3E8D3', 'tabbar': '#EEECE9', 'tabActive': '#FDFDFC', 'accent': '#B5863A', 'accentHover': '#C99A45', 'accentOn': '#16140F', 'tint': '#F3E8D3', 'tintStrong': '#F1E9DA', 'tintSoft': '#F9F7F2'},
        'dark': {'borderStrong': '#6B6962'},
    },
    'navy': {
        'light': {'borderStrong': '#8C93A2', 'accent': '#2563EB', 'accentHover': '#1D4ED8', 'focus': '#2563EB'},
        'dark': {'borderStrong': '#636C7F'},
    },
    'emerald': {
        'light': {'sidebar': '#E7EFEB', 'background': '#F5FAF7', 'surface': '#FCFDFD', 'surfaceSunken': '#ECF3F0', 'border': '#CBD7D2', 'borderStrong': '#7D948C', 'tabbar': '#E7EFEB', 'tabActive': '#FCFDFD'},
        'dark': {'borderStrong': '#5E6D62'},
    },
    'burgundy': {
        'light': {'sidebar': '#F9EFEE', 'background': '#FFFCFC', 'surface': '#FFFEFE', 'surfaceSunken': '#FAF5F4', 'border': '#E2D5D4', 'borderStrong': '#A38C8B', 'tabbar': '#F9EFEE', 'tabActive': '#FFFEFE'},
        'dark': {'borderStrong': '#796460'},
    },
    'plum': {
        'light': {'borderStrong': '#918BA0'},
        'dark': {'borderStrong': '#696679'},
    },
}


def build(key, name, deep, accent, neutral):
    Ld, Cd, Hd = to_oklch(deep)
    Ln, Cn, Hn = to_oklch(neutral)
    colored_deep = Cd >= 0.06                       # Navy, Encre : profonde quasi neutre
    out = {'name': name, 'trio': {'deep': deep, 'accent': accent, 'neutral': neutral}}

    # ----------------------------- clair
    bg = neutral
    surface = mix(neutral, '#FFFFFF', 0.65)
    tint_c = min(max(Cd, Cn), 0.02)
    sunken = shade(neutral, dL=-0.022)
    if Cn < 0.01:                                   # neutre achromatique (blanc, gris) : légère teinte de la couleur profonde
        sidebar = oklch(Ln - 0.035, tint_c * 0.8, Hd)
    elif Ln > 0.97:
        sidebar = shade(neutral, L=Ln - 0.035, C=max(Cn, tint_c * 0.8))
    else:
        sidebar = shade(neutral, dL=-0.03)
    text = deep if cr(deep, sunken) >= 12 else shade(deep, L=0.25, cmax=0.06)
    lt = {
        'sidebar': sidebar, 'background': bg, 'backgroundEnd': bg, 'surface': surface, 'surfaceSunken': sunken,
        'surfaceElevated': '#FFFFFF', 'border': mix(sidebar, text, 0.12), 'borderStrong': mix(sidebar, text, 0.24),
        'textPrimary': text,
        'textSecondary': readable(shade(text, L=0.45, cmax=0.035), [bg, surface, sunken, sidebar], 6.0, -1),
        'textTertiary': readable(shade(text, L=0.53, cmax=0.03), [bg, surface, sunken, sidebar], 4.6, -1),
        'disabled': shade(text, L=0.72, cmax=0.02), 'specimen': text,
        'tabbar': sidebar, 'tabActive': surface,
    }
    fill = deep
    on = next((c for c in (neutral, '#FFFFFF') if cr(c, fill) >= 4.5), '#FFFFFF')
    if cr(on, fill) < 4.5:
        fill = readable(fill, [on], 4.6, -1)
    source = deep if colored_deep else accent
    lt['ornament'] = readable(source, [bg, surface, sunken, sidebar], 5.5, -1)
    lt.update({
        'accent': fill, 'accentHover': shade(fill, dL=-0.05 if to_oklch(fill)[0] > 0.3 else 0.07), 'accentOn': on,
        'highlight': accent,                         # couleur d'accent du trio, en aplat clair (sélections, badges)
        'tint': mix(surface, accent, 0.16 if to_oklch(accent)[0] < 0.8 else 0.30),
        'tintStrong': mix(surface, accent, 0.28 if to_oklch(accent)[0] < 0.8 else 0.55),
        'tintSoft': mix(surface, accent, 0.08 if to_oklch(accent)[0] < 0.8 else 0.16),
        'focus': accent if cr(accent, surface) >= 3 else lt['ornament'],
    })
    lt['badge'] = lt['tint']
    for k, v in SEM['light'].items(): lt[k] = readable(v, [bg, surface, sunken], 4.8, -1)

    # ----------------------------- sombre
    if Cd < 0.06 and Ld <= 0.30:
        base_L, base_C = Ld, Cd                      # Encre, Navy : la couleur profonde sert directement de fond
    else:
        base_L, base_C = 0.19, min(Cd * 0.32, 0.035)
    D = lambda dl, cm=1.0: oklch(base_L + dl, base_C * cm, Hd)
    dbg, dsurf = D(0), D(0.035)
    dsunk, delev, dside = D(-0.025), D(0.07), D(-0.035)
    dtext = neutral if cr(neutral, delev) >= 12 else shade(neutral, L=0.96)
    dk = {
        'sidebar': dside, 'background': dbg, 'backgroundEnd': dbg, 'surface': dsurf, 'surfaceSunken': dsunk,
        'surfaceElevated': delev, 'border': D(0.11, 1.1), 'borderStrong': D(0.19, 1.1),
        'textPrimary': dtext,
        'textSecondary': readable(mix(dtext, dbg, 0.28), [dbg, dsurf, delev, dside], 7.5, +1),
        'textTertiary': readable(mix(dtext, dbg, 0.42), [dbg, dsurf, delev, dside], 5.0, +1),
        'disabled': mix(dtext, dbg, 0.62), 'specimen': dtext, 'tabbar': dside, 'tabActive': delev,
    }
    dfill = accent
    don = next((c for c in (dside, dbg, deep) if cr(c, dfill) >= 4.5), '#000000')
    if cr(don, dfill) < 4.5: dfill = readable(dfill, [don], 4.6, +1)
    dk['ornament'] = readable(accent, [dbg, dsurf, delev, dside], 6.0, +1)
    dk.update({
        'accent': dfill, 'accentHover': shade(dfill, dL=+0.05 if to_oklch(dfill)[0] < 0.9 else -0.05), 'accentOn': don,
        'highlight': accent,
        'tint': mix(dsurf, accent, 0.18), 'tintStrong': mix(dsurf, accent, 0.32), 'tintSoft': mix(dsurf, accent, 0.09),
        'focus': dk['ornament'],
    })
    dk['badge'] = dk['tint']
    for k, v in SEM['dark'].items(): dk[k] = readable(v, [dbg, dsurf, delev], 6.0, +1)
    for mode, part in (('light', lt), ('dark', dk)):
        part.update(AJUSTEMENTS.get(key, {}).get(mode, {}))
    out['light'], out['dark'] = lt, dk
    return out


def report(t):
    rows = []
    for mode in ('light', 'dark'):
        b = t[mode]
        surf = [b['background'], b['surface'], b['surfaceSunken'], b['sidebar'], b['surfaceElevated']]
        checks = {
            'texte principal': (min(cr(b['textPrimary'], s) for s in surf), 7.0),
            'texte secondaire': (min(cr(b['textSecondary'], s) for s in surf), 4.5),
            'texte tertiaire': (min(cr(b['textTertiary'], s) for s in surf), 4.5),
            'texte en couleur': (min(cr(b['ornament'], s) for s in surf), 4.5),
            'texte sur bouton': (min(cr(b['accentOn'], b['accent']), cr(b['accentOn'], b['accentHover'])), 4.5),
            'texte sur sélection': (cr(b['textPrimary'], b['tintStrong']), 4.5),
            'contour des contrôles': (min(cr(b['borderStrong'], b['background']), cr(b['borderStrong'], b['surface'])), 3.0),
            'bouton / surface (graphique)': (max(cr(b['accent'], b['surface']), 1.0), 3.0 if mode == 'light' else 1.0),
            'focus / surface': (cr(b['focus'], b['surface']), 3.0),
            'succès / avertissement / erreur': (min(cr(b[k], s) for k in ('success', 'warning', 'error') for s in surf[:3]), 4.5),
        }
        for k, (v, lim) in checks.items(): rows.append((mode, k, v, lim, v >= lim))
    return rows


if __name__ == '__main__':
    themes = {k: build(k, n, d, a, ne) for k, n, d, a, ne in TRIOS}
    fails = 0
    for k, t in themes.items():
        for mode, name, v, lim, ok in report(t):
            if not ok:
                fails += 1; print(f'  BAS {k:10} {mode:5} {name:32} {v:.2f} < {lim}')
        print(f'{k:10} clair: bouton {t["light"]["accent"]}/{t["light"]["accentOn"]} {cr(t["light"]["accent"], t["light"]["accentOn"]):.1f}  '
              f'texte couleur {t["light"]["ornament"]}  |  sombre: fond {t["dark"]["background"]} bouton {t["dark"]["accent"]}/{t["dark"]["accentOn"]} '
              f'{cr(t["dark"]["accent"], t["dark"]["accentOn"]):.1f}  texte couleur {t["dark"]["ornament"]}')
    json.dump({'default': DEFAULT, 'order': [t[0] for t in TRIOS], 'themes': themes,
               'contrast': {k: [dict(zip(('mode', 'check', 'ratio', 'min', 'ok'), (m, n, round(v, 2), l, o))) for m, n, v, l, o in report(t)] for k, t in themes.items()}},
              open(HERE + '/themes.json', 'w'), indent=1, ensure_ascii=False)
    print('contrôles en échec :', fails)
