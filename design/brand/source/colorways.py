"""Variantes de couleur du monogramme (pour décision) : A recommandée, B et C alternatives."""
import json, subprocess
import os
HERE = os.path.dirname(os.path.abspath(__file__))   # design/brand/source
G = json.load(open(HERE + '/brand-geometry.json'))
M, WD, LOGO = G['monogram'], G['wordmark'], G['logo']
f = lambda v: ('%.2f' % v).rstrip('0').rstrip('.')
def logo(x, y, h, up, lo, tx):
    s = h / 100
    return (f'<g transform="translate({f(x)} {f(y)}) scale({s:.5f})"><path fill="{lo}" d="{M["lower"]}"/>'
            f'<path fill="{up}" d="{M["upper"]}"/><path fill="{tx}" d="{WD["d"]}"/></g>')
def mono(x, y, h, up, lo):
    s = h / 100
    return f'<g transform="translate({f(x)} {f(y)}) scale({s:.5f})"><path fill="{lo}" d="{M["lower"]}"/><path fill="{up}" d="{M["upper"]}"/></g>'
def t(x, y, s, size, w, fill, anchor='start'):
    s = s.replace('&', '&amp;')
    return f'<text x="{x}" y="{y}" font-family="Inter" font-size="{size}" font-weight="{w}" fill="{fill}" text-anchor="{anchor}">{s}</text>'
INK, IVORY = '#16140F', '#FCF8EF'
OPTS = [
    ('A · Or & Encre — recommandée', 'Or sur forme basse couleur du texte : neutre, premium, fonctionne avec tous les thèmes',
     ('#B8893A', INK, INK), ('#DDB66E', IVORY, IVORY), (INK, '#DDB66E', IVORY)),
    ('B · Or dominant & émeraude profonde', 'Couleurs inversées : l’or devient la grande forme, l’émeraude #065F46 de ta palette en accent',
     ('#065F46', '#B8893A', INK), ('#3FA67F', '#DDB66E', IVORY), (INK, '#3FA67F', '#DDB66E')),
    ('C · Or ton sur ton', 'Deux ors en aplat, sans autre couleur : très sobre, un peu moins de contraste entre les formes',
     ('#C9A25A', '#8A6420', INK), ('#E8CD94', '#B8893A', IVORY), (INK, '#E8CD94', '#B8893A')),
]
W, RH = 2000, 300; parts = []
for i, (title, sub, light, dark, icon) in enumerate(OPTS):
    y = 30 + i * (RH + 90)
    parts.append(t(40, y + 26, title, 26, 700, '#10142A')); parts.append(t(40, y + 56, sub, 17, 400, '#5C6380'))
    y += 76
    parts.append(f'<rect x="40" y="{y}" width="760" height="{RH}" rx="16" fill="#FFFFFF" stroke="#DDE1EB"/>')
    parts.append(logo(40 + (760 - LOGO['w'] * 0.8) / 2, y + (RH - 80) / 2, 80, *light))
    parts.append(f'<rect x="830" y="{y}" width="760" height="{RH}" rx="16" fill="{INK}"/>')
    parts.append(logo(830 + (760 - LOGO['w'] * 0.8) / 2, y + (RH - 80) / 2, 80, *dark))
    bg, up, lo = icon
    parts.append(f'<rect x="1620" y="{y}" width="{RH}" height="{RH}" rx="66" fill="{bg}"/>')
    parts.append(mono(1620 + (RH - 104.5 * 1.7) / 2, y + (RH - 170) / 2, 170, up, lo))
H = 30 + 3 * (RH + 90) + 60
svg = f'<svg xmlns="http://www.w3.org/2000/svg" width="{W - 40}" height="{H}"><rect width="100%" height="100%" fill="#F1F3F8"/>{"".join(parts)}</svg>'
open(HERE + '/colorways.svg', 'w').write(svg)
subprocess.run(['rsvg-convert', HERE + '/colorways.svg', '-o', os.path.dirname(HERE) + '/preview/variantes-couleur-monogramme.png'], check=True)
