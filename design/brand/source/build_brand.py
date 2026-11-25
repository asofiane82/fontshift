"""Construit les assets de marque Fontshift (logo n° 05, aplats) à partir des tracés vectorisés.

Entrées : work/monogram.json (monogramme séparé, work/separate.py), work/wordmark.json (logotype Instrument Sans 600, gen_wordmark.py).
Sortie : out/fontshift-brand/ (SVG, PNG, icônes macOS, favicons).
"""
import json, os, re, subprocess, sys, shutil
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from bezfit import fit

ROOT = os.path.dirname(os.path.abspath(__file__))        # design/brand/source
OUT = os.path.dirname(ROOT)                             # design/brand

# ---------------------------------------------------------------- couleurs
BRAND = {
    'gold': '#DDB66E',         # Or Fontshift (fonds sombres)
    'goldDeep': '#B8893A',     # Or profond (fonds clairs)
    'ivory': '#FCF8EF',        # Ivoire : forme basse et logotype sur fond sombre
    'ink': '#16140F',          # Encre : forme basse et logotype sur fond clair, fond de l'icône
    'black': '#000000',
    'white': '#FFFFFF',
}

# ---------------------------------------------------------------- monogramme (normalisé, hauteur 100)
# work/separate.py : forme haute inchangée, forme basse détourée avec un écart constant
MONO = json.load(open(f'{ROOT}/monogram.json'))
UPPER, LOWER = MONO['upper'], MONO['lower']
MW, MH = MONO['w'], MONO['h']


def fmt(v):
    s = f'{v:.2f}'.rstrip('0').rstrip('.')
    return '0' if s in ('-0', '') else s


# ---------------------------------------------------------------- logotype
W = json.load(open(f'{ROOT}/wordmark.json'))
CAP = 36.5                                   # hauteur de capitale = 0,365 × monogramme
GAP = 16.8                                   # espace monogramme / logotype (planche d’origine)
k = CAP / W['cap']
wx = MW + GAP - W['ink'][0] * k
wy = MH / 2 + CAP / 2                        # capitales centrées sur le monogramme
LOGO_W = wx + W['ink'][2] * k


def wordmark_d():
    """Contours du logotype : commandes absolues M/L/Q/C/Z, mises à l'échelle et placées."""
    out = []
    for op, pts in W['cmds']:
        if op == 'Z':
            out.append('Z')
            continue
        out.append(op + ' '.join(f'{fmt(wx + px * k)} {fmt(wy + py * k)}' for px, py in pts))
    return ''.join(out)


WORD = wordmark_d()

# ---------------------------------------------------------------- écriture SVG
HEADER = '<?xml version="1.0" encoding="UTF-8"?>\n'


def svg(view_w, view_h, body, title):
    return (HEADER + f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {fmt(view_w)} {fmt(view_h)}" '
            f'width="{fmt(view_w * 4)}" height="{fmt(view_h * 4)}" role="img" aria-label="{title}">\n'
            f'  <title>{title}</title>\n{body}</svg>\n')


def mono_body(upper, lower, indent='  ', transform=None):
    g = f'{indent}<g transform="{transform}">\n' if transform else ''
    e = f'{indent}</g>\n' if transform else ''
    i2 = indent + ('  ' if transform else '')
    return g + f'{i2}<path fill="{lower}" d="{LOWER}"/>\n{i2}<path fill="{upper}" d="{UPPER}"/>\n' + e


VARIANTS = {
    # nom : (forme haute, forme basse, logotype, titre)
    'dark': (BRAND['gold'], BRAND['ivory'], BRAND['ivory'], 'Fontshift — pour fonds sombres'),
    'light': (BRAND['goldDeep'], BRAND['ink'], BRAND['ink'], 'Fontshift — pour fonds clairs'),
    'black': (BRAND['black'], BRAND['black'], BRAND['black'], 'Fontshift — monochrome noir'),
    'white': (BRAND['white'], BRAND['white'], BRAND['white'], 'Fontshift — monochrome blanc'),
}


def write(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    open(path, 'w').write(text)


def build_logos():
    for name, (upper, lower, text, title) in VARIANTS.items():
        body = mono_body(upper, lower) + f'  <path fill="{text}" d="{WORD}"/>\n'
        write(f'{OUT}/svg/fontshift-logo-{name}.svg', svg(LOGO_W, MH, body, title))
        write(f'{OUT}/svg/fontshift-monogram-{name}.svg', svg(MW, MH, mono_body(upper, lower), title.replace('Fontshift', 'Monogramme Fontshift')))
    # logotype seul (utile pour l'interface, couleur reprise du texte courant)
    ys = [p[1] for op, pts in W['cmds'] for p in pts]
    top, bottom = wy + min(ys) * k, wy + max(ys) * k          # point du i et dépassements inclus
    wbody = f'  <path fill="currentColor" transform="translate({fmt(-(MW + GAP))} {fmt(-top)})" d="{WORD}"/>\n'
    write(f'{OUT}/svg/fontshift-wordmark.svg', svg(LOGO_W - MW - GAP, bottom - top, wbody, 'Fontshift'))


# ---------------------------------------------------------------- icône macOS
def squircle_d(x0, y0, size, n=5.0):
    """Rectangle à coins continus (superellipse n = 5), proche du gabarit Apple."""
    a = size / 2
    cx, cy = x0 + a, y0 + a
    t = np.linspace(0, np.pi / 2, 400)
    q = np.c_[a * np.cos(t) ** (2 / n), a * np.sin(t) ** (2 / n)]
    segs = fit(q, 0.05, t1=np.array([0., 1.]), t2=np.array([1., 0.]))
    d = ''
    quads = [(1, 1), (-1, 1), (-1, -1), (1, -1)]
    first = True
    for qi, (sx, sy) in enumerate(quads):
        ss = segs if qi % 2 == 0 else [s[::-1] for s in segs[::-1]]
        for s in ss:
            p = [(cx + sx * pt[0], cy + sy * pt[1]) for pt in s]
            if first:
                d += f'M{fmt(p[0][0])} {fmt(p[0][1])}'
                first = False
            d += 'C' + ' '.join(f'{fmt(a_)} {fmt(b_)}' for a_, b_ in p[1:])
    return d + 'Z'


def icon_svg(size=1024, tile=824, mono_h=0.6, bg=None, full_bleed=False, radius=None):
    bg = bg or BRAND['ink']
    if full_bleed:
        shape = f'  <rect width="{size}" height="{size}" fill="{bg}"/>\n' if radius is None else \
            f'  <rect width="{size}" height="{size}" rx="{fmt(radius)}" fill="{bg}"/>\n'
        area = size
        off = 0
    else:
        off = (size - tile) / 2
        shape = f'  <path fill="{bg}" d="{squircle_d(off, off, tile)}"/>\n'
        area = tile
    h = area * mono_h
    sc = h / MH
    tx = size / 2 - MW * sc / 2
    ty = size / 2 - MH * sc / 2
    body = shape + mono_body(BRAND['gold'], BRAND['ivory'], transform=f'translate({fmt(tx)} {fmt(ty)}) scale({sc:.5f})')
    return svg(size, size, body, 'Icône de Fontshift').replace(f'width="{fmt(size * 4)}" height="{fmt(size * 4)}"', f'width="{size}" height="{size}"')


def raster(svg_path, png_path, w, h=None):
    os.makedirs(os.path.dirname(png_path), exist_ok=True)
    cmd = ['rsvg-convert', '-w', str(w)] + (['-h', str(h)] if h else []) + [svg_path, '-o', png_path]
    subprocess.run(cmd, check=True)


def build_icons():
    write(f'{OUT}/macos/fontshift-app-icon.svg', icon_svg())
    raster(f'{OUT}/macos/fontshift-app-icon.svg', f'{OUT}/macos/fontshift-app-icon-1024.png', 1024, 1024)
    iconset = f'{OUT}/macos/Fontshift.iconset'
    os.makedirs(iconset, exist_ok=True)
    for base in (16, 32, 128, 256, 512):
        for scale in (1, 2):
            px = base * scale
            name = f'icon_{base}x{base}' + ('@2x' if scale == 2 else '') + '.png'
            raster(f'{OUT}/macos/fontshift-app-icon.svg', f'{iconset}/{name}', px, px)
    # .icns (générateur Tauri, identique à iconutil)
    tmp = '/tmp/fontshift-icns'
    shutil.rmtree(tmp, ignore_errors=True)
    subprocess.run(['npx', '--yes', '@tauri-apps/cli@2', 'icon', f'{OUT}/macos/fontshift-app-icon-1024.png', '-o', tmp],
                   check=True, cwd=os.path.join(ROOT, '..', '..', '..'), capture_output=True)
    shutil.copy(f'{tmp}/icon.icns', f'{OUT}/macos/Fontshift.icns')


def build_web():
    web = f'{OUT}/web'
    # favicon vectoriel : monogramme seul, couleurs adaptées au thème du navigateur
    body = ('  <style>.g{fill:%s}.e{fill:%s}@media (prefers-color-scheme: dark){.g{fill:%s}.e{fill:%s}}</style>\n'
            % (BRAND['goldDeep'], BRAND['ink'], BRAND['gold'], BRAND['ivory']))
    pad = 6
    side = MH + 2 * pad
    body += (f'  <g transform="translate({fmt((side - MW) / 2)} {pad})">\n'
             f'    <path class="e" d="{LOWER}"/>\n    <path class="g" d="{UPPER}"/>\n  </g>\n')
    write(f'{web}/favicon.svg', svg(side, side, body, 'Fontshift').replace(f'width="{fmt(side * 4)}" height="{fmt(side * 4)}" ', ''))
    # pavé pour .ico, PNG et icônes d'application web
    write(f'{web}/favicon-tile.svg', icon_svg(64, full_bleed=True, radius=14, mono_h=0.64))
    for px in (16, 32, 48):
        raster(f'{web}/favicon-tile.svg', f'{web}/favicon-{px}.png', px, px)
    from PIL import Image
    imgs = [Image.open(f'{web}/favicon-{px}.png') for px in (16, 32, 48)]
    imgs[2].save(f'{web}/favicon.ico', sizes=[(16, 16), (32, 32), (48, 48)], append_images=imgs[:2])
    write(f'{web}/apple-touch-icon.svg', icon_svg(180, full_bleed=True, mono_h=0.58))
    raster(f'{web}/apple-touch-icon.svg', f'{web}/apple-touch-icon.png', 180, 180)
    write(f'{web}/icon-maskable.svg', icon_svg(512, full_bleed=True, mono_h=0.5))
    for px in (192, 512):
        raster(f'{web}/icon-maskable.svg', f'{web}/icon-{px}.png', px, px)
    os.remove(f'{web}/apple-touch-icon.svg')
    write(f'{web}/site.webmanifest', json.dumps({
        'name': 'Fontshift', 'short_name': 'Fontshift', 'theme_color': BRAND['ink'], 'background_color': BRAND['ink'],
        'display': 'standalone',
        'icons': [{'src': '/icon-192.png', 'sizes': '192x192', 'type': 'image/png', 'purpose': 'any maskable'},
                  {'src': '/icon-512.png', 'sizes': '512x512', 'type': 'image/png', 'purpose': 'any maskable'}]},
        indent=2) + '\n')
    write(f'{web}/head.html', '<link rel="icon" href="/favicon.ico" sizes="48x48">\n'
          '<link rel="icon" href="/favicon.svg" type="image/svg+xml">\n'
          '<link rel="apple-touch-icon" href="/apple-touch-icon.png">\n'
          '<link rel="manifest" href="/site.webmanifest">\n')


def build_desktop():
    """Icône Windows et Linux : même dessin, pavé à coins arrondis sur toute la surface (pas de marge macOS)."""
    write(f'{OUT}/desktop/fontshift-desktop-icon.svg', icon_svg(1024, full_bleed=True, radius=228, mono_h=0.5))
    raster(f'{OUT}/desktop/fontshift-desktop-icon.svg', f'{OUT}/desktop/fontshift-desktop-icon-1024.png', 1024, 1024)


def build_png():
    for name in VARIANTS:
        raster(f'{OUT}/svg/fontshift-logo-{name}.svg', f'{OUT}/png/fontshift-logo-{name}-2400.png', 2400)
        raster(f'{OUT}/svg/fontshift-monogram-{name}.svg', f'{OUT}/png/fontshift-monogram-{name}-1024.png', 1024)


if __name__ == '__main__':
    for d in ('svg', 'png', 'macos', 'web', 'desktop'):
        shutil.rmtree(f'{OUT}/{d}', ignore_errors=True)
    build_logos(); build_png(); build_icons(); build_desktop(); build_web()
    json.dump({'monogram': {'w': MW, 'h': MH, 'gap': MONO['gap'], 'upper': UPPER, 'lower': LOWER},
               'wordmark': {'font': W.get('font'), 'd': WORD, 'x': MW + GAP, 'capTop': wy - CAP, 'baseline': wy, 'w': LOGO_W - MW - GAP},
               'logo': {'w': LOGO_W, 'h': MH}, 'colors': BRAND}, open(f'{ROOT}/brand-geometry.json', 'w'), indent=1)
    print('logo', round(LOGO_W, 2), '×', MH, 'monogramme', round(MW, 2), '×', MH)
