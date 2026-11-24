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

# Erreurs
check(E.open_faces(b"\x80\x01abcdef", "Ancienne-Police.pfb").get("error") == "type1", "Type 1 refusé avec code")
check(E.open_faces(b"garbage-data-here", "x.ttf").get("error") in ("unknownFormat", "corrupt"), "fichier illisible refusé")
print("RESULT", "PASS" if ok else "FAIL")
