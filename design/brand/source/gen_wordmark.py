"""Logotype « Fontshift » en Syne 600 → work/wordmark.json (contours vectoriels, y vers le bas, ligne de base à 0)."""
import io, json, sys
import os
HERE = os.path.dirname(os.path.abspath(__file__))   # design/brand/source
from fontTools.ttLib import TTFont
from fontTools.varLib import instancer
from fontTools.ttLib.removeOverlaps import removeOverlaps
from fontTools.pens.recordingPen import DecomposingRecordingPen
from fontTools.pens.boundsPen import BoundsPen
import uharfbuzz as hb

SRC = os.path.join(HERE, '..', '..', '..', 'node_modules', '@fontsource-variable', 'syne', 'files', 'syne-latin-wght-normal.woff2')
WGHT, TRACK, TEXT = 600, 0.0, 'Fontshift'

f = TTFont(SRC); f.flavor = None
f = instancer.instantiateVariableFont(f, {'wght': WGHT}, static=True)
removeOverlaps(f)                                   # contours propres (pas de chevauchements hérités du variable)
buf = io.BytesIO(); f.save(buf); data = buf.getvalue()
gs, order, upem = f.getGlyphSet(), f.getGlyphOrder(), f['head'].unitsPerEm
cap = f['OS/2'].sCapHeight

font = hb.Font(hb.Face(data)); b = hb.Buffer(); b.add_str(TEXT); b.guess_segment_properties()
hb.shape(font, b, {'kern': True, 'liga': False})

cmds, d, kern = [], [], []
x = 0.0; xmin, xmax, ymin = 1e9, -1e9, 1e9
P = lambda px, py: [round(x + px, 2), round(-py, 2)]
for info, pos in zip(b.glyph_infos, b.glyph_positions):
    g = order[info.codepoint]
    rp = DecomposingRecordingPen(gs); gs[g].draw(rp)
    for op, args in rp.value:
        if op == 'moveTo': cmds.append(['M', [P(*args[0])]])
        elif op == 'lineTo': cmds.append(['L', [P(*args[0])]])
        elif op == 'curveTo': cmds.append(['C', [P(*p) for p in args]])
        elif op == 'qCurveTo':
            offs, on = list(args[:-1]), args[-1]
            for i in range(len(offs) - 1):
                mid = ((offs[i][0] + offs[i + 1][0]) / 2, (offs[i][1] + offs[i + 1][1]) / 2)
                cmds.append(['Q', [P(*offs[i]), P(*mid)]])
            cmds.append(['Q', [P(*offs[-1]), P(*on)]])
        elif op in ('closePath', 'endPath'): cmds.append(['Z', []])
    bp = BoundsPen(gs); gs[g].draw(bp)
    if bp.bounds:
        xmin = min(xmin, x + bp.bounds[0]); xmax = max(xmax, x + bp.bounds[2]); ymin = min(ymin, bp.bounds[1])
    kern.append([g, pos.x_advance])
    x += pos.x_advance + TRACK * upem

fmt = lambda v: f'{v:.2f}'.rstrip('0').rstrip('.')
dd = ''.join(op + ' '.join(f'{fmt(a)} {fmt(c)}' for a, c in pts) for op, pts in cmds)
json.dump({'font': f'Syne {WGHT}', 'd': dd, 'upem': upem, 'cap': cap, 'ink': [round(xmin, 2), round(ymin, 2), round(xmax, 2), cap],
           'advance': x, 'kern': kern, 'tracking': TRACK, 'cmds': cmds}, open(HERE + '/wordmark.json', 'w'))
print('Syne', WGHT, 'upem', upem, 'cap', cap, 'ink', round(xmin, 1), round(xmax, 1), 'glyphs', [k[0] for k in kern])
