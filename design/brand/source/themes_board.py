"""Planche des thèmes (phase 1) : 8 thèmes en aplats, clair et sombre, sur une maquette réduite de Fontshift."""
import json, subprocess
import os
HERE = os.path.dirname(os.path.abspath(__file__))   # design/brand/source
from themes_build import cr

T = json.load(open(HERE + '/themes.json'))
G = json.load(open(HERE + '/brand-geometry.json'))
M, WD, C = G['monogram'], G['wordmark'], G['colors']
OUT = os.path.join(os.path.dirname(HERE), 'preview')
f = lambda v: ('%.2f' % v).rstrip('0').rstrip('.')
INK, MUTED, LINE = '#10142A', '#5C6380', '#DDE1EB'


def text(x, y, s, size=16, weight=400, fill=INK, anchor='start'):
    s = s.replace('&', '&amp;').replace('<', '&lt;')
    return f'<text x="{f(x)}" y="{f(y)}" font-family="Inter, sans-serif" font-size="{size}" font-weight="{weight}" fill="{fill}" text-anchor="{anchor}">{s}</text>'


def rect(x, y, w, h, fill, rx=10, stroke=None, sw=1):
    st = f' stroke="{stroke}" stroke-width="{sw}"' if stroke else ''
    return f'<rect x="{f(x)}" y="{f(y)}" width="{f(w)}" height="{f(h)}" rx="{rx}" fill="{fill}"{st}/>'


def ui(x, y0, b, dark, pw, ph):
    up = C['gold'] if dark else C['goldDeep']
    o = [rect(x, y0, pw, ph, b['background'], rx=14, stroke=b['border'])]
    sbw = 150
    o.append(f'<path d="M{f(x + 14)} {f(y0)}H{f(x + sbw)}V{f(y0 + ph)}H{f(x + 14)}A14 14 0 0 1 {f(x)} {f(y0 + ph - 14)}V{f(y0 + 14)}A14 14 0 0 1 {f(x + 14)} {f(y0)}Z" fill="{b["sidebar"]}"/>')
    o.append(f'<line x1="{f(x + sbw)}" y1="{f(y0)}" x2="{f(x + sbw)}" y2="{f(y0 + ph)}" stroke="{b["border"]}"/>')
    # logo de l'interface : forme haute or, forme basse et logotype à la couleur du texte
    s = 24 / 100
    o.append(f'<g transform="translate({f(x + 16)} {f(y0 + 20)}) scale({s:.4f})"><path fill="{b["textPrimary"]}" d="{M["lower"]}"/>'
             f'<path fill="{up}" d="{M["upper"]}"/><path fill="{b["textPrimary"]}" d="{WD["d"]}"/></g>')
    for k, (lab, on) in enumerate((('Conversion', True), ('Google Fonts', False), ('Variables', False), ('Résultats', False))):
        yy = y0 + 76 + k * 32
        if on:
            o.append(rect(x + 10, yy - 20, sbw - 20, 29, b['tint'], rx=7))
        o.append(text(x + 22, yy, lab, 12.5, 600 if on else 450, b['ornament'] if on else b['textSecondary']))
    o.append(text(x + 22, y0 + ph - 22, 'Réglages', 12, 450, b['textTertiary']))
    cx, cw = x + sbw + 18, pw - sbw - 36
    o.append(text(cx, y0 + 36, 'Convertir vos polices', 17, 650, b['textPrimary']))
    o.append(text(cx, y0 + 57, 'Formats, axes variables, CSS', 12, 400, b['textSecondary']))
    o.append(rect(cx + cw - 64, y0 + 22, 64, 22, b['badge'], rx=11))
    o.append(text(cx + cw - 32, y0 + 37, '4 polices', 11, 600, b['textPrimary'], 'middle'))
    o.append(rect(cx, y0 + 74, cw, 112, b['surface'], rx=10, stroke=b['border']))
    for k, (lab, on) in enumerate((('WOFF2', True), ('WOFF', True), ('TTF', False))):
        yy = y0 + 101 + k * 27
        o.append(rect(cx + 14, yy - 13, 16, 16, b['accent'] if on else b['surface'], rx=4, stroke=None if on else b['borderStrong'], sw=1.5))
        if on:
            o.append(f'<path d="M{f(cx + 17.5)} {f(yy - 5)}l3 3 6-6.5" fill="none" stroke="{b["accentOn"]}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>')
        o.append(text(cx + 38, yy, lab, 12.5, 500, b['textPrimary']))
    # aperçu de la police (spécimen) dans la carte
    o.append(text(cx + cw - 16, y0 + 140, 'Aa', 40, 600, b['specimen'], 'end'))
    o.append(text(cx + cw - 16, y0 + 172, 'Voir le détail →', 12, 600, b['ornament'], 'end'))
    o.append(rect(cx, y0 + 198, cw, 38, b['accent'], rx=9))
    o.append(text(cx + cw / 2, y0 + 222, 'Convertir 4 polices', 13.5, 650, b['accentOn'], 'middle'))
    o.append(f'<circle cx="{f(cx + 7)}" cy="{f(y0 + 258)}" r="4" fill="{b["success"]}"/>')
    o.append(text(cx + 18, y0 + 262, 'Conversion terminée', 12, 500, b['success']))
    o.append(f'<circle cx="{f(cx + cw / 2 + 20)}" cy="{f(y0 + 258)}" r="4" fill="{b["error"]}"/>')
    o.append(text(cx + cw / 2 + 31, y0 + 262, '1 erreur', 12, 500, b['error']))
    return ''.join(o)


W, PAD, GX = 2400, 80, 40
pw, ph = (W - 2 * PAD - GX - 2 * 20) / 4, 284
parts = [rect(0, 0, W, 210, C['ink'], rx=0)]
parts.append(f'<g transform="translate({PAD} 62) scale(0.86)"><path fill="{C["ivory"]}" d="{M["lower"]}"/><path fill="{C["gold"]}" d="{M["upper"]}"/>'
             f'<path fill="{C["ivory"]}" d="{WD["d"]}"/></g>')
parts.append(text(W - PAD, 92, 'Thèmes de l’application — refonte en aplats', 30, 650, '#F4EFE6', 'end'))
parts.append(text(W - PAD, 130, 'Construits à partir de tes 7 palettes · Champagne & Encre par défaut · clair et sombre', 20, 400, '#C9C2B4', 'end'))
parts.append(text(W - PAD, 164, 'Clair : fond = neutre, boutons = couleur profonde · Sombre : fonds = couleur profonde assombrie, boutons = accent', 17, 400, '#A69F92', 'end'))
y = 270
order = T['order']
for i in range(0, len(order), 2):
    for j, key in enumerate(order[i:i + 2]):
        t = T['themes'][key]
        x = PAD + j * (2 * pw + 20 + GX)
        tag = '  · par défaut' if key == T['default'] else ('  · tons roses' if key == 'burgundy' else '')
        parts.append(text(x, y, t['name'] + tag, 22, 700))
        tx = x + 2 * pw + 20
        for k, (role, hx) in enumerate(zip(('profonde', 'accent', 'neutre'), (t['trio']['deep'], t['trio']['accent'], t['trio']['neutral']))):
            cx = tx - (3 - k) * 150
            parts.append(rect(cx, y - 19, 22, 22, hx, rx=6, stroke='#C5CAD9'))
            parts.append(text(cx + 30, y - 2, hx, 14, 500, MUTED))
        for m, mode in enumerate(('light', 'dark')):
            b = t[mode]
            px = x + m * (pw + 20)
            parts.append(ui(px, y + 18, b, mode == 'dark', pw, ph))
            ratio = lambda a, c: ('%.1f' % cr(a, c)).replace('.', ',')
            parts.append(text(px, y + 18 + ph + 24, f"{'Clair' if mode == 'light' else 'Sombre'} · bouton {b['accent']} / libellé {ratio(b['accentOn'], b['accent'])}:1 · texte {ratio(b['textPrimary'], b['background'])}:1 · couleur {ratio(b['ornament'], b['surface'])}:1",
                              13, 500, MUTED))
    y += 18 + ph + 24 + 76
fails = sum(not r['ok'] for v in T['contrast'].values() for r in v)
parts.append(text(PAD, y - 10, f'Contrastes WCAG vérifiés sur chaque fond et surface (texte ≥ 4,5:1, texte principal ≥ 7:1, libellés de bouton ≥ 4,5:1, focus ≥ 3:1) : '
                  f'{"aucun échec" if not fails else f"{fails} échec(s)"} · détail dans themes.json', 16, 500, MUTED))
H = y + 30
svg = f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{f(H)}" viewBox="0 0 {W} {f(H)}"><rect width="100%" height="100%" fill="#F1F3F8"/>{"".join(parts)}</svg>'
open(HERE + '/themes_board.svg', 'w').write(svg)
subprocess.run(['rsvg-convert', HERE + '/themes_board.svg', '-o', f'{OUT}/fontshift-themes.png'], check=True)
print('planche thèmes', W, '×', round(H))
