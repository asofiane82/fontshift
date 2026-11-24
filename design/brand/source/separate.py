"""Monogramme Fontaine : sépare nettement les deux formes du F.

La forme haute n'est pas modifiée. Le bord supérieur de la forme basse devient une courbe
parallèle au bord inférieur de la forme haute (écart constant), qui rejoint le contour gauche
du F. Les autres bords de la forme basse gardent leurs courbes d'origine (simplement coupées).
Entrée : monogram-source.json (coordonnées normalisées, hauteur 100). Sortie : monogram.json.
Usage : python3 separate.py [écart en % de la hauteur, défaut 4.5]
"""
import json, re, sys
import os
HERE = os.path.dirname(os.path.abspath(__file__))   # design/brand/source
import numpy as np
from shapely.geometry import Polygon, LineString, Point
from shapely.ops import substring
sys.path.insert(0, HERE)
from bezfit import fit, bez

GAP = float(sys.argv[1]) if len(sys.argv) > 1 else 4.5
SRC = json.load(open(HERE + '/monogram-source.json'))


def parse(d):
    toks = re.findall(r'[MLCZ]|-?\d+\.?\d*', d)
    segs, cur, i = [], None, 0
    while i < len(toks):
        t = toks[i]
        if t == 'M': cur = np.array([float(toks[i + 1]), float(toks[i + 2])]); i += 3
        elif t == 'L':
            q = np.array([float(toks[i + 1]), float(toks[i + 2])]); segs.append(('L', np.array([cur, q]))); cur = q; i += 3
        elif t == 'C':
            p = np.array([float(v) for v in toks[i + 1:i + 7]]).reshape(3, 2); segs.append(('C', np.vstack([cur, p]))); cur = p[2]; i += 7
        else: i += 1
    return segs


def sample(segs, n=400):
    pts = []
    for k, s in segs:
        pts += list(np.linspace(s[0], s[1], 20)[:-1]) if k == 'L' else list(bez(s, np.linspace(0, 1, n))[:-1])
    pts.append(segs[-1][1][-1])
    return np.array(pts)


def split(P, t):
    """De Casteljau : renvoie les deux moitiés de la cubique P coupée en t."""
    a, b = P[:-1] + t * (P[1:] - P[:-1]), None
    b = a[:-1] + t * (a[1:] - a[:-1]); c = b[:-1] + t * (b[1:] - b[:-1])
    return np.array([P[0], a[0], b[0], c[0]]), np.array([c[0], b[1], a[2], P[3]])


def crossing(P, inside, from_start):
    """Paramètre t où la cubique P sort de la zone « inside » (recherche dichotomique)."""
    lo, hi = 0.0, 1.0
    for _ in range(60):
        m = (lo + hi) / 2
        if inside(Point(bez(P, np.array([m]))[0])) == from_start: lo = m
        else: hi = m
    return (lo + hi) / 2


gold, full = parse(SRC['gold']), parse(SRC['greenFull'])
# bord inférieur de la forme haute : « L76.57 29.33 L47.2 29.33 C31.51 29.33 15.31 48.11 15.08 48.13 »
bi = [i for i, s in enumerate(gold) if s[0] == 'L' and abs(s[1][0][1] - s[1][1][1]) < 1e-6 and s[1][0][1] > 20][0]
y_bar, x_join = gold[bi][1][0][1], gold[bi][1][1][0]
curve = gold[bi + 1][1]
cs = bez(curve, np.linspace(0, 1, 800))
tc = 1 - 59 / 799                                                         # ignore le petit crochet final
tip_dir = 3 * ((1 - tc) ** 2 * (curve[1] - curve[0]) + 2 * (1 - tc) * tc * (curve[2] - curve[1]) + tc ** 2 * (curve[3] - curve[2]))
tip_dir /= np.linalg.norm(tip_dir)                                         # prolongement tangent
edge = np.vstack([[[140, y_bar]], cs[:-59], cs[-60] + tip_dir * np.linspace(0.5, 30, 60)[:, None]])
off = LineString(edge).offset_curve(-GAP, quad_segs=32, join_style='round')
if off.coords[0][0] < off.coords[-1][0]: off = LineString(list(off.coords)[::-1])   # de droite à gauche
oc = np.array(off.coords)
above = Polygon(np.vstack([oc, [[oc[-1][0] - 50, oc[-1][1]], [oc[-1][0] - 50, -300], [oc[0][0], -300]]])).buffer(0)
inside = lambda p: above.contains(p)

# bords d'origine de la forme basse
left = full[0][1]                                    # M15.08 48.13 C… 0 100  (contour gauche, vers le bas)
bottom = full[1][1]                                  # 0 100 → 36.64 76.49
right = full[2][1]                                   # 36.64 76.49 → 64.99 29.33 (remonte)
ta = crossing(left, inside, True); left_kept = split(left, ta)[1]
tb = crossing(right, inside, False); right_kept = split(right, tb)[0]
A, B = left_kept[0], right_kept[3]                   # coin haut-gauche, coin haut-droit

# bord supérieur : parallèle exacte, entre les deux coins
sa, sb = off.project(Point(A)), off.project(Point(B))
top = np.array(substring(off, min(sa, sb), max(sa, sb)).coords)
if top[0][0] < top[-1][0]: top = top[::-1]
top[0], top[-1] = B, A
x_split = x_join
flat_end = np.array([x_split, y_bar + GAP])
curved = top[top[:, 0] <= x_split + 1e-9]
curved = np.vstack([flat_end, curved[np.linalg.norm(curved - flat_end, axis=1) > 1e-6]])
dense = [curved[0]]
for a, b in zip(curved[:-1], curved[1:]):
    k = max(1, int(np.linalg.norm(b - a) / 0.15)); dense += list(np.linspace(a, b, k + 1)[1:])
top_segs = fit(np.array(dense), 0.02, t1=np.array([-1.0, 0.0]))

f = lambda v: f'{v:.2f}'.rstrip('0').rstrip('.')
pt = lambda p: f'{f(p[0])} {f(p[1])}'
C = lambda P: 'C' + ' '.join(pt(p) for p in P[1:])
d = f'M{pt(A)}' + C(left_kept) + C(bottom) + C(right_kept) + f'L{pt(flat_end)}' + ''.join(C(s) for s in top_segs) + 'Z'

gpoly = Polygon(sample(gold)).buffer(0); lpoly = Polygon(sample(parse(d))).buffer(0)
print(f'écart {GAP} — distance mini mesurée {gpoly.distance(lpoly):.2f} ; coin gauche {A.round(2).tolist()} ; '
      f'coin droit {B.round(2).tolist()} ; segments du bord supérieur {len(top_segs)} ; valide {lpoly.is_valid}')
json.dump({'w': SRC['w'], 'h': SRC['h'], 'gap': GAP, 'upper': SRC['gold'], 'lower': d}, open(HERE + '/monogram.json', 'w'), indent=1)
