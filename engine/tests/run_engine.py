"""Tests du moteur sous CPython : python3 engine/tests/run_engine.py"""
import io, json, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import fontaine_engine as E
from fontTools.ttLib import TTFont

HERE = os.path.dirname(__file__)
OUT = os.path.join(HERE, "out"); os.makedirs(OUT, exist_ok=True)
ok = True
def check(cond, label):
    global ok
    print(("OK   " if cond else "FAIL ") + label)
    ok = ok and cond

def load(name):
    return open(os.path.join(HERE, name), "rb").read()

for fname in ["inter-latin-opsz-normal.woff2", "playfair-display-latin-wght-normal.woff2", "playfair-display-latin-600-italic.woff2"]:
    data = load(fname)
    info = E.open_faces(data, fname)
    face = info["faces"][0]
    print(fname, face["family"], face["style"], face["outlines"], "var" if face["variable"] else "static", [a["tag"] for a in face["axes"]], len(face["instances"]), face["metrics"])
    for subset in ("full", "latin"):
        for mode in (["keep", "static"] if face["variable"] else ["keep"]):
            res = E.convert(data, fname, json.dumps({"formats": ["woff2", "woff", "ttf", "otf", "eot"], "variable": mode, "subset": subset}))
            if "error" in res:
                check(False, f"{fname} {subset} {mode}: {res}"); continue
            names = [o["name"] for o in res["outputs"]]
            check(len(res["outputs"]) > 0, f"{fname} {subset} {mode}: {len(names)} fichiers, avert. {[w['code'] for w in res['warnings']]}")
            for o in res["outputs"]:
                blob = o["data"]
                if o["format"] == "eot":
                    sfnt = E.eot_to_sfnt(blob)
                    f = TTFont(io.BytesIO(sfnt))
                else:
                    f = TTFont(io.BytesIO(blob))
                expect_cff = o["format"] == "otf"
                good = ("CFF " in f) == expect_cff and (("glyf" in f) != expect_cff)
                if o["format"] in ("woff", "woff2"):
                    good = f.flavor == o["format"]
                if not good:
                    check(False, f"   {o['name']} contenu inattendu")
                if subset == "full" and mode == "static":
                    open(os.path.join(OUT, o["name"]), "wb").write(blob)
            if subset == "full" and mode == "keep":
                for o in res["outputs"]:
                    open(os.path.join(OUT, o["name"]), "wb").write(o["data"])
                print("   ", [(o["name"], o["size"], o["weight"], o["fontStyle"]) for o in res["outputs"]][:6])

# Export d'une position précise (écran Polices variables)
data = load("playfair-display-latin-wght-normal.woff2")
res = E.convert(data, "x.woff2", json.dumps({"formats": ["ttf"], "instances": [{"name": "SemiBold", "coords": {"wght": 600}}]}))
f = TTFont(io.BytesIO(res["outputs"][0]["data"]))
check("fvar" not in f and f["OS/2"].usWeightClass == 600, f"instance précise : {res['outputs'][0]['name']} poids {f['OS/2'].usWeightClass} nom {f['name'].getDebugName(4)}")

# Aller-retour OTF (CFF) -> TTF / WOFF2
otf = open(os.path.join(OUT, "PlayfairDisplay-Bold.otf"), "rb").read() if os.path.exists(os.path.join(OUT, "PlayfairDisplay-Bold.otf")) else None
if otf:
    info = E.open_faces(otf, "PlayfairDisplay-Bold.otf")
    check(info["faces"][0]["outlines"] == "CFF", "OTF lu comme CFF")
    res = E.convert(otf, "PlayfairDisplay-Bold.otf", json.dumps({"formats": ["ttf", "woff2", "eot"]}))
    check("outputs" in res and len(res["outputs"]) == 3, f"OTF -> TTF/WOFF2/EOT {[o['name'] for o in res.get('outputs', [])]}")

# Sous-ensemble personnalisé
res = E.convert(load("playfair-display-latin-600-italic.woff2"), "p.woff2", json.dumps({"formats": ["woff2"], "subset": "custom", "customText": "Fontaine"}))
f = TTFont(io.BytesIO(res["outputs"][0]["data"]))
check(set(chr(c) for c in f.getBestCmap()) <= set("Fontaine  "), f"sous-ensemble perso : {sorted(chr(c) for c in f.getBestCmap())}")

# Sous-ensemble personnalisé avec plage Unicode
res = E.convert(load("playfair-display-latin-600-italic.woff2"), "p.woff2", json.dumps({"formats": ["woff2"], "subset": "custom", "customText": "U+0041-0043, xyz"}))
f = TTFont(io.BytesIO(res["outputs"][0]["data"]))
got = set(chr(c) for c in f.getBestCmap())
check({"A", "B", "C", "x", "y", "z"} <= got and got <= set("ABCxyz \u00a0"), f"plage U+0041-0043 + xyz : {sorted(got)}")

# Fusion de statiques en police variable
from fontTools.varLib import instancer as _inst
pf = load("playfair-display-latin-wght-normal.woff2")
res = E.convert(pf, "p.woff2", json.dumps({"formats": ["ttf", "otf"], "instances": [{"name": n, "coords": {"wght": w}} for n, w in (("Regular", 400), ("Bold", 700), ("Black", 900))]}))
statics = {o["name"]: o["data"] for o in res["outputs"]}
for ext in ("ttf", "otf"):
    names = sorted(n for n in statics if n.endswith(ext))
    chk = E.merge([statics[n] for n in names], names, json.dumps({"family": "Playfair Display"}))
    check(chk.get("ok") and "font" not in chk and [a["tag"] for a in chk["axes"]] == ["wght"], f"fusion {ext} : vérification seule {chk.get('axes')}")
    built = E.merge([statics[n] for n in names], names, json.dumps({"family": "Playfair Display", "build": True}))
    vf = TTFont(io.BytesIO(built["font"]))
    axis = vf["fvar"].axes[0]
    styles = sorted(vf["name"].getDebugName(i.subfamilyNameID) for i in vf["fvar"].instances)
    check("glyf" in vf and (axis.minValue, axis.defaultValue, axis.maxValue) == (400, 400, 900) and styles == ["Black", "Bold", "Regular"] and built["stem"] == "PlayfairDisplay-VariableFont_wght",
          f"fusion {ext} : police variable {built['size']} octets, instances {styles}")
    out = E.convert(built["font"], built["stem"] + ".ttf", json.dumps({"formats": ["woff2"], "stem": built["stem"]}))
    check(out["outputs"][0]["variable"] and out["outputs"][0]["weight"] == "400 900", f"fusion {ext} → WOFF2 {out['outputs'][0]['name']}")
bold = TTFont(io.BytesIO(statics["PlayfairDisplay-Bold.ttf"]))
at700 = _inst.instantiateVariableFont(TTFont(io.BytesIO(E.merge([statics[n] for n in sorted(statics) if n.endswith("ttf")], sorted(n for n in statics if n.endswith("ttf")), '{"build": true}')["font"])), {"wght": 700}, static=True)
from fontTools.pens.areaPen import AreaPen
from fontTools.pens.boundsPen import BoundsPen
def _shape(font, g):
    gs = font.getGlyphSet(); a, b = AreaPen(gs), BoundsPen(gs); gs[g].draw(a); gs[g].draw(b)
    return a.value, b.bounds or (0, 0, 0, 0)
def _same(x, y):  # l'optimisation des variations tolère une demi-unité par point
    return abs(x[0] - y[0]) <= max(1.0, abs(y[0]) * 0.01) and all(abs(p - q) <= 1 for p, q in zip(x[1], y[1]))
check(all(_same(_shape(at700, g), _shape(bold, g)) for g in bold.getGlyphOrder()), "fusion : le Bold recalculé correspond au fichier Bold (aire à 1 % près, boîte à 1 unité)")
# Contours fusionnés à l'export (cas courant des polices du commerce) : refus explicite
from fontTools.varLib.instancer import OverlapMode
try:
    import pathops  # noqa: F401
    rm = []
    for w in (100, 400, 900):
        f = TTFont(io.BytesIO(load("inter-latin-opsz-normal.woff2")))
        s = _inst.instantiateVariableFont(f, {"wght": w, "opsz": 14}, overlap=OverlapMode.REMOVE, static=True)
        s.flavor = None; b = io.BytesIO(); s.save(b); rm.append(b.getvalue())
    bad = E.merge(rm, ["a.ttf", "b.ttf", "c.ttf"], "{}")
    check(bad.get("error") == "mergeIncompatible" and bad["count"] > 0 and "&" in bad["chars"], f"fusion refusée : {bad.get('count')} glyphes incompatibles sur {bad.get('total')} ({bad.get('chars', '')[:12]}…)")
except ImportError:
    print("SKIP fusion contours fusionnés (skia-pathops absent)")
check(E.merge([statics["PlayfairDisplay-Bold.ttf"], statics["PlayfairDisplay-Black.otf"]], ["a.ttf", "b.otf"], "{}").get("error") == "mergeMixed", "fusion TTF + OTF refusée")
check(E.merge([statics["PlayfairDisplay-Bold.ttf"]] * 2, ["a.ttf", "b.ttf"], "{}").get("error") == "mergeSameStyle", "fusion de deux fichiers de même graisse refusée")
check(E.merge([pf, statics["PlayfairDisplay-Bold.ttf"]], ["v.woff2", "b.ttf"], "{}").get("error") == "mergeVariable", "fusion avec une police déjà variable refusée")

# Erreurs
check(E.open_faces(b"\x80\x01abcdef", "Ancienne-Police.pfb").get("error") == "type1", "Type 1 refusé avec code")
check(E.open_faces(b"garbage-data-here", "x.ttf").get("error") in ("unknownFormat", "corrupt"), "fichier illisible refusé")
print("RESULT", "PASS" if ok else "FAIL")
