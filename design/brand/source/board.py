"""Planche d’identité (phase 1) : logos, monogramme, icône macOS, favicons, couleurs de marque."""
import json, subprocess, base64
import os
HERE = os.path.dirname(os.path.abspath(__file__))   # design/brand/source

G = json.load(open(HERE + '/brand-geometry.json'))
C = G['colors']
M = G['monogram']; WD = G['wordmark']; LOGO = G['logo']
OUT = os.path.dirname(HERE)
FONT = "font-family=\"Inter, sans-serif\""


def f(v):
    return ('%.2f' % v).rstrip('0').rstrip('.')


def mono(x, y, h, up, lo, *_):
    s = h / 100
    return (f'<g transform="translate({f(x)} {f(y)}) scale({s:.5f})"><path fill="{lo}" d="{M["lower"]}"/>'
            f'<path fill="{up}" d="{M["upper"]}"/></g>')


def logo(x, y, h, up, lo, text, *_):
    s = h / 100
    return (f'<g transform="translate({f(x)} {f(y)}) scale({s:.5f})"><path fill="{lo}" d="{M["lower"]}"/>'
            f'<path fill="{up}" d="{M["upper"]}"/><path fill="{text}" d="{WD["d"]}"/></g>')


def text(x, y, s, size=16, weight=400, fill='#10142A', anchor='start', extra=''):
    s = s.replace('&', '&amp;').replace('<', '&lt;')
    return f'<text x="{f(x)}" y="{f(y)}" {FONT} font-size="{size}" font-weight="{weight}" fill="{fill}" text-anchor="{anchor}" {extra}>{s}</text>'


def rect(x, y, w, h, fill, rx=16, stroke=None, sw=1, extra=''):
    st = f' stroke="{stroke}" stroke-width="{sw}"' if stroke else ''
    return f'<rect x="{f(x)}" y="{f(y)}" width="{f(w)}" height="{f(h)}" rx="{rx}" fill="{fill}"{st} {extra}/>'


def img(x, y, w, h, path, smooth=True):
    b64 = base64.b64encode(open(path, 'rb').read()).decode()
    r = '' if smooth else ' style="image-rendering:pixelated" image-rendering="optimizeSpeed"'
    return f'<image x="{f(x)}" y="{f(y)}" width="{w}" height="{h}" href="data:image/png;base64,{b64}"{r}/>'


INK, MUTED, LINE = '#10142A', '#5C6380', '#DDE1EB'
W = 2400
parts = []
y = 0

# --- En-tête
parts.append(rect(0, 0, W, 300, C['ink'], rx=0))
parts.append(logo(80, 90, 120, C['gold'], C['ivory'], C['ivory']))
parts.append(text(W - 80, 118, 'Identité visuelle · logo n° 05 « Futuriste & Fluide » · version 3', 30, 600, '#F4EFE6', 'end'))
parts.append(text(W - 80, 162, 'Fontshift — coin bas du F affiné (69°), intégré dans l’application', 22, 400, '#C9C2B4', 'end'))
parts.append(text(W - 80, 200, 'Formes du F nettement séparées · or & encre, sans vert · logotype Syne 600 en contours · aucune image incorporée', 18, 400, '#A69F92', 'end'))
y = 360


def section(title, sub=''):
    global y
    parts.append(text(80, y, title, 34, 600, INK))
    if sub:
        parts.append(text(80, y + 36, sub, 19, 400, MUTED))
    y += 70 if sub else 50


# --- 1. Logo horizontal
section('Logo horizontal', 'Monogramme + logotype, sans slogan · SVG vectoriels et PNG 2400 px')
cw, ch, gap = 538, 320, 36
cards = [('fontshift-logo-dark.svg', 'Fonds sombres', C['ink'], (C['gold'], C['ivory'], C['ivory'], False), '#C9C2B4'),
         ('fontshift-logo-light.svg', 'Fonds clairs', '#FFFFFF', (C['goldDeep'], C['ink'], C['ink'], False), MUTED),
         ('fontshift-logo-black.svg', 'Monochrome noir', '#F1F3F8', ('#000000', '#000000', '#000000', True), MUTED),
         ('fontshift-logo-white.svg', 'Monochrome blanc', '#6D28D9', ('#FFFFFF', '#FFFFFF', '#FFFFFF', True), '#E4DCFB')]
for i, (fname, label, bg, (g, e, t, cut), lc) in enumerate(cards):
    x = 80 + i * (cw + gap)
    parts.append(rect(x, y, cw, ch, bg, stroke=LINE if bg in ('#FFFFFF', '#F1F3F8') else None))
    lh = 84
    lw = LOGO['w'] * lh / 100
    parts.append(logo(x + (cw - lw) / 2, y + (ch - lh) / 2 - 14, lh, g, e, t, cut))
    parts.append(text(x + 24, y + ch - 26, label, 17, 600, lc))
    parts.append(text(x + cw - 24, y + ch - 26, fname, 15, 400, lc, 'end'))
y += ch + 70

# --- 2. Monogramme, construction, tailles minimales
section('Monogramme', 'Deux formes en aplat nettement séparées (écart constant = 4,5 % de la hauteur) · or au-dessus, encre ou ivoire en dessous · forme haute inchangée')
mw = 262
tiles = [(C['ink'], (C['gold'], C['ivory'], False), 'Fonds sombres'), ('#FFFFFF', (C['goldDeep'], C['ink'], False), 'Fonds clairs'),
         ('#F1F3F8', ('#000000', '#000000', True), 'Noir'), ('#6D28D9', ('#FFFFFF', '#FFFFFF', True), 'Blanc')]
for i, (bg, (g, e, cut), label) in enumerate(tiles):
    x = 80 + i * (mw + 24)
    parts.append(rect(x, y, mw, mw, bg, stroke=LINE if bg in ('#FFFFFF', '#F1F3F8') else None))
    parts.append(mono(x + (mw - 104.5 * 1.55) / 2, y + (mw - 155) / 2 - 12, 155, g, e, cut))
    parts.append(text(x + 20, y + mw - 20, label, 16, 600, '#C9C2B4' if bg in (C['ink'], '#6D28D9') else MUTED))
# Construction : zone de protection
x0 = 80 + 4 * (mw + 24)
cw2 = W - 80 - x0
parts.append(rect(x0, y, cw2, mw, '#FFFFFF', stroke=LINE))
u = 36.2 / 123.41 * 100   # hauteur de la barre or, en unités monogramme (100)
h = 96; s = h / 100; pad = u * s
lx, ly = x0 + 64, y + 60
lw = LOGO['w'] * s
parts.append(rect(lx - pad, ly - pad, lw + 2 * pad, h + 2 * pad, 'none', rx=0, stroke='#8B93B0', sw=1.2, extra='stroke-dasharray="6 5"'))
parts.append(rect(lx, ly, lw, h, 'none', rx=0, stroke='#C5CAD9', sw=1))
parts.append(logo(lx, ly, h, C['goldDeep'], C['ink'], C['ink']))
parts.append(rect(lx - pad, ly, pad, u * s, '#C49A4E', rx=0, extra='opacity=".35"'))
parts.append(text(lx - pad / 2, ly + u * s / 2 + 6, 'x', 16, 700, '#7A5716', 'middle'))
tx = lx + lw + pad + 56
parts.append(text(tx, y + 64, 'Zone de protection : x = hauteur de la barre or', 18, 600, INK))
parts.append(text(tx, y + 96, 'Logo horizontal : 24 px de haut minimum', 17, 400, MUTED))
parts.append(text(tx, y + 122, 'Monogramme seul : 16 px minimum', 17, 400, MUTED))
parts.append(text(tx, y + 148, 'Proportions : logotype en capitales = 0,365 × monogramme', 17, 400, MUTED))
parts.append(text(tx, y + 174, 'Écart monogramme / logotype = 0,168 × monogramme', 17, 400, MUTED))
parts.append(text(tx, y + 200, 'Logotype : Syne 600 (SIL OFL 1.1), en contours', 17, 400, MUTED))
parts.append(text(tx, y + 226, 'Séparation des formes : 0,045 × monogramme', 17, 400, MUTED))
# petites tailles réelles
sx = lx - pad
for hh in (48, 32, 24, 16):
    parts.append(mono(sx, y + 196 + (48 - hh), hh * 0.96, C['goldDeep'], C['ink']))
    sx += hh + 22
parts.append(logo(sx + 10, y + 220, 24, C['goldDeep'], C['ink'], C['ink']))
parts.append(text(lx - pad, y + mw - 4, 'Tailles réelles : 48, 32, 24 et 16 px · logo à 24 px', 14, 400, MUTED))
y += mw + 70

# --- 3. Icône macOS
section('Icône de l’application (macOS)', 'Identique pour tous les thèmes · gabarit Apple 1024 px, pavé 824 px à coins continus · .icns et Fontshift.iconset (16 à 1024 px)')
ih = 420
parts.append(rect(80, y, 560, ih, '#E9ECF3', stroke=LINE))
parts.append(img(80 + 60, y + 0, ih, ih, f'{OUT}/macos/fontshift-app-icon-1024.png'))
# tailles réelles sur fond clair et sombre
x1 = 680
parts.append(rect(x1, y, 760, ih / 2 - 10, '#FFFFFF', stroke=LINE))
parts.append(rect(x1, y + ih / 2 + 10, 760, ih / 2 - 10, '#1E2236'))
sizes = [(128, 'icon_128x128.png'), (64, 'icon_32x32@2x.png'), (32, 'icon_32x32.png'), (16, 'icon_16x16.png')]
for row, (by, lc) in enumerate(((y, MUTED), (y + ih / 2 + 10, '#B9BFD6'))):
    cx = x1 + 40
    for px, fn in sizes:
        parts.append(img(cx, by + (ih / 2 - 10 - px) / 2 - 8, px, px, f'{OUT}/macos/Fontshift.iconset/{fn}'))
        parts.append(text(cx + px / 2, by + ih / 2 - 26, f'{px} px', 14, 500, lc, 'middle'))
        cx += px + 70
# Dock
dx = 1480
parts.append(rect(dx, y, W - 80 - dx, ih, '#DCE0EA', stroke=LINE))
parts.append(rect(dx + 60, y + ih - 150, W - 80 - dx - 120, 110, '#FFFFFF', rx=26, extra='opacity=".72"'))
parts.append(text(dx + (W - 80 - dx) / 2, y + 70, 'Dock et Finder', 20, 600, INK, 'middle'))
for i in range(5):
    ix = dx + 100 + i * 150
    if i == 2:
        parts.append(img(ix - 4, y + ih - 146, 102, 102, f'{OUT}/macos/Fontshift.iconset/icon_128x128@2x.png'))
        parts.append(f'<circle cx="{ix + 47}" cy="{y + ih - 46}" r="4" fill="#10142A" opacity=".7"/>')
    else:
        parts.append(rect(ix + 6, y + ih - 136, 82, 82, '#C8CDDA', rx=20))
# Finder
parts.append(rect(dx + 60, y + 100, 240, 150, '#FFFFFF', rx=14, stroke='#C5CAD9'))
parts.append(img(dx + 130, y + 112, 100, 100, f'{OUT}/macos/Fontshift.iconset/icon_128x128@2x.png'))
parts.append(text(dx + 180, y + 236, 'Fontshift.app', 15, 500, INK, 'middle'))
y += ih + 70

# --- 4. Favicons
section('Favicon du site', 'favicon.svg (s’adapte au thème du navigateur), favicon.ico 16/32/48, apple-touch-icon 180, icônes 192 et 512')
fh = 200
for i, (bg, tab, fg, scheme) in enumerate((('#DEE2EB', '#FFFFFF', INK, 'light'), ('#1B1F33', '#2A2F48', '#EEF0F8', 'dark'))):
    x = 80 + i * 760
    parts.append(rect(x, y, 720, fh, bg))
    parts.append(rect(x + 30, y + 40, 330, 52, tab, rx=10))
    gold, em = (C['goldDeep'], C['ink']) if scheme == 'light' else (C['gold'], C['ivory'])
    parts.append(mono(x + 48, y + 57, 18, gold, em))
    parts.append(text(x + 80, y + 72, 'Fontshift — conversion de polices', 15, 500, fg))
    parts.append(text(x + 30, y + 150, 'favicon.svg · thème ' + ('clair' if scheme == 'light' else 'sombre') + ' du navigateur', 15, 400, MUTED if scheme == 'light' else '#B9BFD6'))
fx = 80 + 2 * 760
parts.append(rect(fx, y, W - 80 - fx, fh, '#FFFFFF', stroke=LINE))
cx = fx + 40
for px, fn in ((48, 'favicon-48.png'), (32, 'favicon-32.png'), (16, 'favicon-16.png')):
    parts.append(img(cx, y + 50, px, px, f'{OUT}/web/{fn}'))
    parts.append(text(cx + px / 2, y + 36, f'{px}', 13, 500, MUTED, 'middle'))
    cx += max(px, 30) + 50
parts.append(img(cx + 20, y + 40, 120, 120, f'{OUT}/web/apple-touch-icon.png'))
parts.append(text(cx + 80, y + 184, 'apple-touch-icon (180)', 13, 500, MUTED, 'middle'))
parts.append(text(fx + 40, y + 140, 'favicon.ico : 16, 32 et 48 px', 14, 400, MUTED))
y += fh + 70

# --- 5. Couleurs de marque
section('Couleurs de marque', 'Aplats, sans dégradé · aucun vert · l’or profond sert sur fond clair')
sw = [('Or Fontshift', C['gold'], 'forme haute, fonds sombres'), ('Or profond', C['goldDeep'], 'forme haute, fonds clairs'),
      ('Encre', C['ink'], 'forme basse et logotype sur clair, fond de l’icône'), ('Ivoire', C['ivory'], 'forme basse et logotype sur sombre')]
bw = (W - 160 - 3 * 24) / 4
for i, (n, hx, use) in enumerate(sw):
    x = 80 + i * (bw + 24)
    parts.append(rect(x, y, bw, 120, hx, stroke=LINE if hx in ('#FCF8EF',) else None))
    parts.append(text(x, y + 150, n, 17, 600, INK))
    parts.append(text(x, y + 174, hx + ' · ' + use, 15, 400, MUTED))
y += 230

H = y + 40
svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{f(H)}" viewBox="0 0 {W} {f(H)}">'
       f'<rect width="100%" height="100%" fill="#F1F3F8"/>' + ''.join(parts) + '</svg>')
open(HERE + '/board.svg', 'w').write(svg)
subprocess.run(['rsvg-convert', HERE + '/board.svg', '-o', f'{OUT}/preview/fontshift-planche-identite.png'], check=True)
print('planche', W, '×', round(H))
