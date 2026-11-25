"""Fontshift — moteur de conversion de polices.

Ce module tourne dans Pyodide (WebAssembly, dans un Web Worker de l'application)
et, pour les tests, dans un CPython classique. Il ne dépend que de fontTools et
d'un module `brotli` (natif sous CPython, relié à brotli-wasm dans l'application).

Trois points d'entrée, appelés par le worker :

    open_faces(data, filename)            -> dict  (analyse, une entrée par police du fichier)
    convert(data, filename, options_json) -> dict  (fichiers produits et avertissements)
    merge(datas, filenames, options_json) -> dict  (polices statiques fusionnées en police variable)

Aucune chaîne d'interface ici : erreurs et avertissements sont des codes que
l'interface traduit.
"""

from __future__ import annotations

import io
import json
import re
import struct

from fontTools.ttLib import TTCollection, TTFont, newTable
from fontTools.ttLib.sfnt import readTTCHeader  # noqa: F401  (présence vérifiée au chargement)

ENGINE_VERSION = "1.0.0"

# Plages Unicode des sous-ensembles (identiques à celles de Google Fonts).
LATIN = (
    "U+0000-00FF, U+0131, U+0152-0153, U+02BB-02BC, U+02C6, U+02DA, U+02DC, U+0304, U+0308, "
    "U+0329, U+2000-206F, U+20AC, U+2122, U+2191, U+2193, U+2212, U+2215, U+FEFF, U+FFFD"
)
LATIN_EXT = (
    "U+0100-02BA, U+02BD-02C5, U+02C7-02CC, U+02CE-02D7, U+02DD-02FF, U+0304, U+0308, U+0329, "
    "U+1D00-1DBF, U+1E00-1E9F, U+1EF2-1EFF, U+2020, U+20A0-20AB, U+20AD-20C0, U+2113, "
    "U+2C60-2C7F, U+A720-A7FF"
)

WIDTH_CLASS_TO_PCT = {1: 50, 2: 62.5, 3: 75, 4: 87.5, 5: 100, 6: 112.5, 7: 125, 8: 150, 9: 200}


def _as_bytes(data) -> bytes:
    """Accepte bytes (CPython) ou un Uint8Array JavaScript (Pyodide)."""
    if hasattr(data, "to_bytes"):
        return data.to_bytes()
    return bytes(data)


class EngineError(Exception):
    """Erreur connue, transmise à l'interface sous forme de code."""

    def __init__(self, code: str, detail: str = ""):
        super().__init__(code)
        self.code = code
        self.detail = detail


# --------------------------------------------------------------------------- #
#  Lecture des conteneurs                                                      #
# --------------------------------------------------------------------------- #

def sniff(data: bytes, filename: str = "") -> str:
    """Identifie le conteneur à partir des premiers octets (l'extension sert de repli)."""
    head = data[:4]
    if head == b"wOF2":
        return "WOFF2"
    if head == b"wOFF":
        return "WOFF"
    if head == b"ttcf":
        return "TTC"
    if head == b"OTTO":
        return "OTF"
    if head in (b"\x00\x01\x00\x00", b"true"):
        return "TTF"
    if head[:2] == b"\x80\x01" or data[:2] == b"%!":
        return "TYPE1"
    if len(data) > 36 and struct.unpack_from("<H", data, 34)[0] == 0x504C:
        return "EOT"
    ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    if ext in ("pfb", "pfa", "pfm", "afm"):
        return "TYPE1"
    if ext == "eot":
        return "EOT"
    return "UNKNOWN"


def eot_to_sfnt(data: bytes) -> bytes:
    """Extrait la police d'un conteneur EOT non compressé (MicroType Express non pris en charge)."""
    if len(data) < 82:
        raise EngineError("corrupt")
    eot_size, font_size, version, flags = struct.unpack_from("<IIII", data, 0)
    if flags & 0x4:
        raise EngineError("eotCompressed")
    if font_size == 0 or font_size > len(data):
        raise EngineError("corrupt")
    start = min(eot_size, len(data)) - font_size
    font = bytearray(data[start:start + font_size])
    if flags & 0x10000000:  # TTEMBED_XORENCRYPTDATA
        for i in range(len(font)):
            font[i] ^= 0x50
    return bytes(font)


def _load(data: bytes, filename: str, lazy: bool = False) -> list[tuple[TTFont, str]]:
    """Renvoie [(police, format source)] ; une collection donne plusieurs polices."""
    kind = sniff(data, filename)
    if kind == "TYPE1":
        raise EngineError("type1")
    if kind == "UNKNOWN":
        raise EngineError("unknownFormat")
    try:
        if kind == "EOT":
            return [(TTFont(io.BytesIO(eot_to_sfnt(data)), lazy=lazy), "EOT")]
        if kind == "TTC":
            coll = TTCollection(io.BytesIO(data), lazy=lazy)
            return [(f, "TTC") for f in coll.fonts]
        return [(TTFont(io.BytesIO(data), lazy=lazy), kind)]
    except EngineError:
        raise
    except Exception as exc:  # police illisible
        raise EngineError("corrupt", str(exc)) from exc


# --------------------------------------------------------------------------- #
#  Analyse                                                                     #
# --------------------------------------------------------------------------- #

def _name(font: TTFont, *ids: int) -> str:
    table = font.get("name")
    if table is None:
        return ""
    for nid in ids:
        rec = table.getDebugName(nid)
        if rec:
            return str(rec)
    return ""


def outline_kind(font: TTFont) -> str:
    if "glyf" in font:
        return "TrueType"
    if "CFF2" in font:
        return "CFF2"
    if "CFF " in font:
        return "CFF"
    return "Bitmap"


def _glyph_height(font: TTFont, char: str, top: bool = True):
    cmap = font.getBestCmap() or {}
    gname = cmap.get(ord(char))
    if not gname:
        return None
    try:
        from fontTools.pens.boundsPen import BoundsPen

        gs = font.getGlyphSet()
        pen = BoundsPen(gs)
        gs[gname].draw(pen)
        if pen.bounds:
            return pen.bounds[3] if top else pen.bounds[1]
    except Exception:
        return None
    return None


def _metrics(font: TTFont) -> dict:
    upem = font["head"].unitsPerEm
    os2 = font.get("OS/2")
    hhea = font.get("hhea")
    asc = getattr(os2, "sTypoAscender", None) if os2 else None
    desc = getattr(os2, "sTypoDescender", None) if os2 else None
    if not asc and hhea:
        asc, desc = hhea.ascent, hhea.descent
    cap = getattr(os2, "sCapHeight", 0) if os2 and os2.version >= 2 else 0
    xh = getattr(os2, "sxHeight", 0) if os2 and os2.version >= 2 else 0
    if not cap:
        cap = _glyph_height(font, "H") or round(upem * 0.7)
    if not xh:
        xh = _glyph_height(font, "x") or round(upem * 0.5)
    asc_glyph = _glyph_height(font, "d") or _glyph_height(font, "l") or asc
    desc_glyph = _glyph_height(font, "p", top=False) or _glyph_height(font, "g", top=False) or desc
    return {
        "unitsPerEm": upem,
        "ascender": int(asc or upem * 0.8),
        "descender": int(desc or -upem * 0.2),
        "ascenderGlyph": int(asc_glyph or asc or upem * 0.75),
        "descenderGlyph": int(desc_glyph or desc or -upem * 0.2),
        "capHeight": int(cap),
        "xHeight": int(xh),
    }


def _axes(font: TTFont) -> list[dict]:
    if "fvar" not in font:
        return []
    out = []
    for a in font["fvar"].axes:
        out.append({
            "tag": a.axisTag,
            "name": _name(font, a.axisNameID) or a.axisTag,
            "min": a.minValue,
            "default": a.defaultValue,
            "max": a.maxValue,
            "hidden": bool(a.flags & 0x1),
        })
    return out


def _instances(font: TTFont) -> list[dict]:
    if "fvar" not in font:
        return []
    out = []
    for inst in font["fvar"].instances:
        out.append({"name": _name(font, inst.subfamilyNameID) or "", "coords": dict(inst.coordinates)})
    return out


def _is_italic(font: TTFont) -> bool:
    os2 = font.get("OS/2")
    if os2 is not None and os2.fsSelection & 0x1:
        return True
    return bool(font["head"].macStyle & 0x2)


def _sample_chars(font: TTFont, limit: int = 96) -> list[str]:
    cmap = font.getBestCmap() or {}
    chars = []
    for cp in sorted(cmap):
        if cp < 0x21 or 0x7F <= cp < 0xA1 or 0xD800 <= cp <= 0xDFFF or cp in (0xAD,):
            continue
        chars.append(chr(cp))
        if len(chars) >= limit:
            break
    return chars


def describe(font: TTFont, source_format: str) -> dict:
    os2 = font.get("OS/2")
    axes = _axes(font)
    cmap = font.getBestCmap() or {}
    return {
        "family": _name(font, 16, 1),
        "style": _name(font, 17, 2),
        "fullName": _name(font, 4),
        "postscriptName": _name(font, 6),
        "version": _name(font, 5),
        "sourceFormat": source_format,
        "flavor": font.flavor or "",
        "outlines": outline_kind(font),
        "glyphs": len(font.getGlyphOrder()),
        "codepoints": len(cmap),
        "variable": bool(axes),
        "axes": axes,
        "instances": _instances(font),
        "weight": getattr(os2, "usWeightClass", 400) if os2 else 400,
        "widthClass": getattr(os2, "usWidthClass", 5) if os2 else 5,
        "italic": _is_italic(font),
        "tables": sorted(t.strip() for t in font.keys() if t != "GlyphOrder"),
        "metrics": _metrics(font),
        "sample": _sample_chars(font),
    }


def _sfnt_bytes(font: TTFont) -> bytes:
    """Police autonome, sans compression WOFF : directement chargeable par l'aperçu."""
    buf = io.BytesIO()
    font.flavor = None
    font.save(buf, reorderTables=False)
    return buf.getvalue()


def open_faces(data: bytes, filename: str) -> dict:
    """Analyse un fichier. Renvoie {"faces": [...]} ou {"error": code}."""
    try:
        loaded = _load(_as_bytes(data), filename)
    except EngineError as err:
        return {"error": err.code, "detail": err.detail}
    faces = []
    for idx, (font, kind) in enumerate(loaded):
        try:
            info = describe(font, kind)
        except Exception as exc:
            return {"error": "corrupt", "detail": str(exc)}
        # Une collection ou un EOT est extrait en police autonome pour la suite du traitement.
        if kind in ("TTC", "EOT"):
            info["extracted"] = _sfnt_bytes(font)
        info["index"] = idx
        faces.append(info)
    return {"faces": faces}


# --------------------------------------------------------------------------- #
#  Transformations                                                             #
# --------------------------------------------------------------------------- #

def _parse_ranges(spec: str) -> set[int]:
    out: set[int] = set()
    for part in spec.split(","):
        part = part.strip().upper().replace("U+", "")
        if not part:
            continue
        if "-" in part:
            a, b = part.split("-", 1)
            out.update(range(int(a, 16), int(b, 16) + 1))
        else:
            out.add(int(part, 16))
    return out


def subset_unicodes(mode: str, custom_text: str = "") -> set[int] | None:
    if mode == "latin":
        return _parse_ranges(LATIN)
    if mode == "latinExt":
        return _parse_ranges(LATIN) | _parse_ranges(LATIN_EXT)
    if mode == "custom":
        # Plages Unicode (« U+0041 », « U+0100-017F ») et caractères tapés tels quels.
        text = custom_text or ""
        ranges = re.findall(r"[Uu]\+[0-9A-Fa-f]{1,6}(?:\s*-\s*(?:[Uu]\+)?[0-9A-Fa-f]{1,6})?", text)
        cps = _parse_ranges(",".join(r.replace(" ", "") for r in ranges)) if ranges else set()
        for r in ranges:
            text = text.replace(r, " ")
        cps |= {ord(c) for c in text if c not in ",;\n\r\t"}
        cps |= {0x20, 0xA0}
        return {c for c in cps if c <= 0x10FFFF}
    return None


def apply_subset(font: TTFont, unicodes: set[int]) -> None:
    from fontTools import subset

    opts = subset.Options()
    opts.layout_features = ["*"]
    opts.name_IDs = ["*"]
    opts.name_languages = ["*"]
    opts.name_legacy = True
    opts.notdef_outline = True
    opts.glyph_names = True
    opts.legacy_kern = True
    opts.symbol_cmap = True
    opts.hinting = True
    opts.drop_tables = [t for t in opts.drop_tables if t not in ("FFTM",)]
    sub = subset.Subsetter(options=opts)
    sub.populate(unicodes=unicodes)
    sub.subset(font)


def _clone(font: TTFont) -> TTFont:
    buf = io.BytesIO()
    flavor = font.flavor
    font.flavor = None
    font.save(buf, reorderTables=False)
    font.flavor = flavor
    buf.seek(0)
    return TTFont(buf)


def _set_static_names(font: TTFont, family: str, style: str) -> None:
    """Noms cohérents pour une instance statique quand STAT ne permet pas de les déduire."""
    name = font["name"]
    ps_family = re.sub(r"[^A-Za-z0-9]", "", family)
    ps_style = re.sub(r"[^A-Za-z0-9]", "", style) or "Regular"
    ribbi = style in ("Regular", "Italic", "Bold", "Bold Italic")
    for nid, value in (
        (1, family if ribbi else f"{family} {style}"),
        (2, style if ribbi else ("Italic" if "Italic" in style else "Regular")),
        (4, f"{family} {style}"),
        (6, f"{ps_family}-{ps_style}"),
        (16, family),
        (17, style),
    ):
        name.setName(value, nid, 3, 1, 0x409)
        name.setName(value, nid, 1, 0, 0)


def instantiate(font: TTFont, coords: dict, style: str) -> TTFont:
    """Instance statique d'une police variable, axes manquants fixés à leur défaut."""
    from fontTools.varLib import instancer

    limits = {a.axisTag: coords.get(a.axisTag, a.defaultValue) for a in font["fvar"].axes}
    family = _name(font, 16, 1)
    cff2 = "CFF2" in font
    src = _clone(font)
    try:
        static = instancer.instantiateVariableFont(src, limits, updateFontNames=True, downgradeCFF2=cff2, static=True)
    except Exception:
        src = _clone(font)
        static = instancer.instantiateVariableFont(src, limits, downgradeCFF2=cff2, static=True)
        _set_static_names(static, family, style or "Regular")
    if style and _name(static, 17, 2) != style:
        _set_static_names(static, family, style)
    os2 = static.get("OS/2")
    if os2 is not None and "wght" in limits:
        os2.usWeightClass = max(1, min(1000, int(round(limits["wght"]))))
    if os2 is not None and "wdth" in limits:
        pct = limits["wdth"]
        os2.usWidthClass = min(WIDTH_CLASS_TO_PCT, key=lambda k: abs(WIDTH_CLASS_TO_PCT[k] - pct))
    return static


def to_truetype(font: TTFont) -> TTFont:
    """Contours cubiques (CFF/CFF2 statique) vers TrueType quadratique (cu2qu)."""
    if "glyf" in font:
        return font
    from fontTools.pens.cu2quPen import Cu2QuPen
    from fontTools.pens.ttGlyphPen import TTGlyphPen

    if "CFF2" in font:
        from fontTools.cffLib.CFF2ToCFF import convertCFF2ToCFF

        convertCFF2ToCFF(font)
    upem = font["head"].unitsPerEm
    gs = font.getGlyphSet()
    glyphs = {}
    for gname in font.getGlyphOrder():
        tt = TTGlyphPen(gs)
        gs[gname].draw(Cu2QuPen(tt, max_err=upem / 1000.0, reverse_direction=True))
        glyphs[gname] = tt.glyph(dropImpliedOnCurves=True)
    return _install_glyf(font, glyphs)


def _install_glyf(font: TTFont, glyphs: dict) -> TTFont:
    """Remplace les contours CFF par une table glyf déjà construite (glyphes TrueType)."""
    order = font.getGlyphOrder()
    glyf = newTable("glyf")
    glyf.glyphOrder = order
    glyf.glyphs = dict(glyphs)
    font["glyf"] = glyf
    font["loca"] = newTable("loca")
    for tag in ("CFF ", "VORG"):
        if tag in font:
            del font[tag]
    font["head"].glyphDataFormat = 0
    font["head"].indexToLocFormat = 0
    maxp = font["maxp"]
    maxp.tableVersion = 0x00010000
    for field, value in (
        ("maxZones", 1), ("maxTwilightPoints", 0), ("maxStorage", 0), ("maxFunctionDefs", 0),
        ("maxInstructionDefs", 0), ("maxStackElements", 0), ("maxSizeOfInstructions", 0),
        ("maxComponentElements", 0), ("maxComponentDepth", 0), ("maxPoints", 0),
        ("maxContours", 0), ("maxCompositePoints", 0), ("maxCompositeContours", 0),
    ):
        setattr(maxp, field, value)
    post = font["post"]
    post.formatType = 2.0
    post.extraNames = []
    post.mapping = {}
    post.glyphOrder = order
    font.sfntVersion = "\x00\x01\x00\x00"
    return _clone(font)


def to_cff(font: TTFont) -> TTFont:
    """Contours TrueType (statiques) vers CFF : conversion exacte des quadratiques en cubiques."""
    if "CFF " in font:
        return font
    if "CFF2" in font:
        from fontTools.cffLib.CFF2ToCFF import convertCFF2ToCFF

        convertCFF2ToCFF(font)
        return _clone(font)
    from fontTools.fontBuilder import FontBuilder
    from fontTools.pens.t2CharStringPen import T2CharStringPen

    order = font.getGlyphOrder()
    gs = font.getGlyphSet()
    hmtx = font["hmtx"]
    charstrings = {}
    for gname in order:
        pen = T2CharStringPen(hmtx[gname][0], gs)
        gs[gname].draw(pen)
        charstrings[gname] = pen.getCharString()
    post = font["post"]
    ps_name = _name(font, 6) or re.sub(r"[^A-Za-z0-9-]", "", _name(font, 4)) or "Font"
    info = {
        "FullName": _name(font, 4),
        "FamilyName": _name(font, 1),
        "Weight": _name(font, 2),
        "version": _name(font, 5).replace("Version ", ""),
        "Notice": _name(font, 7),
        "ItalicAngle": post.italicAngle,
        "UnderlinePosition": post.underlinePosition,
        "UnderlineThickness": post.underlineThickness,
        "isFixedPitch": bool(post.isFixedPitch),
    }
    for tag in ("glyf", "loca", "cvt ", "fpgm", "prep", "gasp", "hdmx", "LTSH", "VDMX", "gvar", "cvar"):
        if tag in font:
            del font[tag]
    fb = FontBuilder(font=font, isTTF=False)
    fb.isTTF = False
    fb.setupCFF(ps_name, info, charstrings, {})
    font["maxp"].tableVersion = 0x00005000
    post.formatType = 3.0
    font.sfntVersion = "OTTO"
    return _clone(font)


# --------------------------------------------------------------------------- #
#  EOT                                                                         #
# --------------------------------------------------------------------------- #

def _win_name(font: TTFont, nid: int) -> bytes:
    rec = font["name"].getName(nid, 3, 1, 0x409) or font["name"].getName(nid, 3, 1)
    text = rec.toUnicode() if rec else _name(font, nid)
    return text.encode("utf-16-le")


def build_eot(font: TTFont) -> bytes:
    """Embedded OpenType 2.1, données non compressées (Internet Explorer 6 à 11)."""
    sfnt = _sfnt_bytes(font)
    loaded = TTFont(io.BytesIO(sfnt))
    os2 = loaded["OS/2"]
    head = loaded["head"]
    panose = os2.panose
    panose_bytes = bytes([
        panose.bFamilyType, panose.bSerifStyle, panose.bWeight, panose.bProportion, panose.bContrast,
        panose.bStrokeVariation, panose.bArmStyle, panose.bLetterForm, panose.bMidline, panose.bXHeight,
    ])
    names = b""
    for i, nid in enumerate((1, 2, 5, 4)):
        raw = _win_name(loaded, nid)
        if i > 0:
            names += struct.pack("<H", 0)  # Padding2…4
        names += struct.pack("<H", len(raw)) + raw
    names += struct.pack("<HH", 0, 0)  # Padding5, RootStringSize (pas de restriction de domaine)
    fixed = struct.pack(
        "<IIII10sBBIHH4I2II4IH",
        0, len(sfnt), 0x00020001, 0,
        panose_bytes, 1, 1 if _is_italic(loaded) else 0,
        os2.usWeightClass, os2.fsType, 0x504C,
        os2.ulUnicodeRange1, os2.ulUnicodeRange2, os2.ulUnicodeRange3, os2.ulUnicodeRange4,
        getattr(os2, "ulCodePageRange1", 0), getattr(os2, "ulCodePageRange2", 0),
        head.checkSumAdjustment,
        0, 0, 0, 0, 0,
    )
    header = fixed + names
    total = len(header) + len(sfnt)
    header = struct.pack("<I", total) + header[4:]
    return header + sfnt


# --------------------------------------------------------------------------- #
#  Conversion                                                                  #
# --------------------------------------------------------------------------- #

FORMAT_ORDER = ["woff2", "woff", "ttf", "otf", "eot"]
EXT = {"woff2": ".woff2", "woff": ".woff", "ttf": ".ttf", "otf": ".otf", "eot": ".eot"}


def _stem(filename: str) -> str:
    base = filename.rsplit("/", 1)[-1].rsplit("\\", 1)[-1]
    return base.rsplit(".", 1)[0] if "." in base else base


def _safe(text: str) -> str:
    return re.sub(r"[^A-Za-z0-9]+", "", text) or "Font"


def _css_meta(font: TTFont) -> dict:
    """Valeurs @font-face d'une police (plages pour les axes conservés)."""
    axes = {a.axisTag: a for a in font["fvar"].axes} if "fvar" in font else {}
    os2 = font.get("OS/2")
    meta = {"family": _name(font, 16, 1), "style": _name(font, 17, 2), "variable": bool(axes)}
    if "wght" in axes:
        meta["weight"] = f"{_num(axes['wght'].minValue)} {_num(axes['wght'].maxValue)}"
    else:
        meta["weight"] = str(getattr(os2, "usWeightClass", 400) if os2 else 400)
    if "wdth" in axes:
        meta["stretch"] = f"{_num(axes['wdth'].minValue)}% {_num(axes['wdth'].maxValue)}%"
    else:
        pct = WIDTH_CLASS_TO_PCT.get(getattr(os2, "usWidthClass", 5) if os2 else 5, 100)
        meta["stretch"] = "" if pct == 100 else f"{_num(pct)}%"
    if "slnt" in axes:
        a = axes["slnt"]
        meta["fontStyle"] = f"oblique {_num(-a.maxValue)}deg {_num(-a.minValue)}deg"
    elif "ital" in axes and axes["ital"].minValue == 0 and axes["ital"].maxValue >= 1:
        meta["fontStyle"] = "normal"
    else:
        meta["fontStyle"] = "italic" if _is_italic(font) else "normal"
    return meta


def _num(v: float) -> str:
    return str(int(v)) if float(v).is_integer() else f"{v:g}"


def _encode(font: TTFont, fmt: str) -> bytes:
    if fmt == "eot":
        return build_eot(to_truetype(_clone(font)))
    target = font
    if fmt == "ttf":
        target = to_truetype(_clone(font))
    elif fmt == "otf":
        target = to_cff(_clone(font))
    else:
        target = _clone(font)
    buf = io.BytesIO()
    target.flavor = fmt if fmt in ("woff", "woff2") else None
    target.save(buf)
    return buf.getvalue()


def convert(data: bytes, filename: str, options_json: str) -> dict:
    """Convertit une police (ou une police extraite d'une collection).

    options : {
      formats: ["woff2", "woff", "ttf", "otf", "eot"],
      variable: "keep" | "static",
      instances: [{"name": "SemiBold", "coords": {"wght": 600}}] | null,   # export choisi
      subset: "full" | "latin" | "latinExt" | "custom",
      customText: "…",
      stem: "Montserrat[wght]"                                           # nom des fichiers variables
    }
    """
    opts = json.loads(options_json)
    formats = [f for f in FORMAT_ORDER if f in (opts.get("formats") or [])]
    if not formats:
        return {"error": "noFormat"}
    try:
        loaded = _load(_as_bytes(data), filename)
    except EngineError as err:
        return {"error": err.code, "detail": err.detail}
    font, _kind = loaded[0]
    warnings: list[dict] = []
    outputs: list[dict] = []
    try:
        unicodes = subset_unicodes(opts.get("subset", "full"), opts.get("customText", ""))
        if unicodes is not None:
            apply_subset(font, unicodes)
            font = _clone(font)

        is_var = "fvar" in font
        family = _name(font, 16, 1) or _stem(filename)
        variants: list[tuple[TTFont, str, bool]] = []  # (police, nom de fichier, variable ?)
        explicit = opts.get("instances")
        if is_var and explicit:
            for inst in explicit:
                style = inst.get("name") or "Custom"
                variants.append((instantiate(font, inst.get("coords") or {}, style), f"{_safe(family)}-{_safe(style)}", False))
        elif is_var and opts.get("variable") == "static":
            for inst in font["fvar"].instances:
                style = _name(font, inst.subfamilyNameID) or "Instance"
                variants.append((instantiate(font, dict(inst.coordinates), style), f"{_safe(family)}-{_safe(style)}", False))
            if not variants:
                variants.append((instantiate(font, {}, "Regular"), f"{_safe(family)}-Regular", False))
        else:
            variants.append((font, opts.get("stem") or _stem(filename), is_var))

        default_static = None
        for vfont, stem, variable in variants:
            meta = _css_meta(vfont)
            for fmt in formats:
                target = vfont
                out_stem = stem
                if variable and fmt == "otf":
                    warnings.append({"code": "otfVariable", "file": stem})
                    continue
                if variable and fmt == "eot":
                    if default_static is None:
                        default_static = instantiate(font, {}, "Regular")
                    target = default_static
                    out_stem = f"{_safe(family)}-Regular"
                    warnings.append({"code": "eotStatic", "file": stem})
                blob = _encode(target, fmt)
                fmeta = meta if target is vfont else _css_meta(target)
                outputs.append({
                    "name": out_stem + EXT[fmt],
                    "format": fmt,
                    "size": len(blob),
                    "data": blob,
                    "family": fmeta["family"] or family,
                    "styleName": fmeta["style"],
                    "weight": fmeta["weight"],
                    "stretch": fmeta["stretch"],
                    "fontStyle": fmeta["fontStyle"],
                    "variable": fmeta["variable"],
                    "stem": out_stem,
                })
    except EngineError as err:
        return {"error": err.code, "detail": err.detail}
    except Exception as exc:
        return {"error": "convertFailed", "detail": f"{type(exc).__name__}: {exc}"}
    return {"outputs": outputs, "warnings": warnings}


# --------------------------------------------------------------------------- #
#  Fusion de polices statiques en une police variable                          #
# --------------------------------------------------------------------------- #

WEIGHT_NAMES = {100: "Thin", 200: "ExtraLight", 300: "Light", 400: "Regular", 500: "Medium",
                600: "SemiBold", 700: "Bold", 800: "ExtraBold", 900: "Black"}
WIDTH_NAMES = {50: "UltraCondensed", 62.5: "ExtraCondensed", 75: "Condensed", 87.5: "SemiCondensed",
               100: "", 112.5: "SemiExpanded", 125: "Expanded", 150: "ExtraExpanded", 200: "UltraExpanded"}


def _location(font: TTFont) -> tuple[float, float]:
    """Graisse et chasse (en %) annoncées par une police statique."""
    os2 = font.get("OS/2")
    weight = getattr(os2, "usWeightClass", 400) if os2 else 400
    width = WIDTH_CLASS_TO_PCT.get(getattr(os2, "usWidthClass", 5) if os2 else 5, 100)
    return float(weight), float(width)


def _location_name(weight: float, width: float, italic: bool, fallback: str) -> str:
    """Nom de style d'une position : « Bold », « Condensed Light », « SemiBold Italic », « Italic »."""
    wname = WEIGHT_NAMES.get(int(weight)) if float(weight).is_integer() else None
    if wname is None or width not in WIDTH_NAMES:
        return fallback or _num(weight)
    parts = [p for p in (WIDTH_NAMES[width], wname) if p]
    if wname == "Regular" and (WIDTH_NAMES[width] or italic):
        parts.remove("Regular")
    if italic:
        parts.append("Italic")
    return " ".join(parts)


def _axis_label(tag: str, value: float) -> str:
    if tag == "wght":
        return WEIGHT_NAMES.get(int(value)) if float(value).is_integer() and int(value) in WEIGHT_NAMES else _num(value)
    return WIDTH_NAMES.get(value) or ("Normal" if value == 100 else f"{_num(value)}%")


def _chars_for(fonts: list[TTFont], glyph_names) -> str:
    """Caractères visibles correspondant à des glyphes (pour l'explication donnée à l'utilisateur)."""
    wanted = set(glyph_names)
    chars = set()
    for font in fonts:
        for cp, gname in (font.getBestCmap() or {}).items():
            if gname in wanted and cp > 0x20 and not 0x7F <= cp < 0xA1 and not 0xD800 <= cp <= 0xDFFF:
                chars.add(chr(cp))
    return "".join(sorted(chars, key=ord))


def _clear_overlap_flags(font: TTFont) -> None:
    """Les drapeaux de chevauchement ne changent pas le dessin : on les ignore pour comparer."""
    from fontTools.ttLib.tables._g_l_y_f import OVERLAP_COMPOUND, flagOverlapSimple

    glyf = font["glyf"]
    for gname in font.getGlyphOrder():
        glyph = glyf[gname]
        if glyph.isComposite():
            for comp in glyph.components:
                comp.flags &= ~OVERLAP_COMPOUND
        elif glyph.numberOfContours > 0:
            glyph.flags = bytearray(f & ~flagOverlapSimple for f in glyph.flags)


def _cff_masters_to_glyf(masters: list[TTFont]) -> tuple[list[TTFont], list[str]]:
    """Contours CFF vers TrueType, convertis ensemble pour rester interpolables."""
    from fontTools.pens.cu2quPen import Cu2QuMultiPen
    from fontTools.pens.recordingPen import RecordingPen
    from fontTools.pens.ttGlyphPen import TTGlyphPen

    for m in masters:
        if "CFF2" in m:
            from fontTools.cffLib.CFF2ToCFF import convertCFF2ToCFF

            convertCFF2ToCFF(m)
    order = masters[0].getGlyphOrder()
    sets = [m.getGlyphSet() for m in masters]
    max_err = masters[0]["head"].unitsPerEm / 1000.0
    out = [{} for _ in masters]
    bad = []
    for gname in order:
        recs = []
        for gs in sets:
            pen = RecordingPen()
            gs[gname].draw(pen)
            recs.append(pen.value)
        shape = [(op, len(args)) for op, args in recs[0]]
        if any([(op, len(args)) for op, args in r] != shape for r in recs[1:]):
            bad.append(gname)
            continue
        pens = [TTGlyphPen(None) for _ in masters]
        try:
            multi = Cu2QuMultiPen(pens, max_err, reverse_direction=True)
            for i, (op, _args) in enumerate(recs[0]):
                if op in ("closePath", "endPath"):
                    getattr(multi, op)()
                else:
                    getattr(multi, op)([r[i][1] for r in recs])
            for k, pen in enumerate(pens):
                out[k][gname] = pen.glyph(dropImpliedOnCurves=False)
        except Exception:
            bad.append(gname)
    if bad:
        return masters, bad
    return [_install_glyf(m, glyphs) for m, glyphs in zip(masters, out)], []


def _incompatible_glyphs(masters: list[TTFont], default_idx: int) -> list[str]:
    """Glyphes que l'interpolation ne peut pas relier (même critère que fontTools.varLib)."""
    datas = [(m["glyf"], m["hmtx"].metrics) for m in masters]
    bad = []
    for gname in masters[default_idx].getGlyphOrder():
        found = [glyf._getCoordinatesAndControls(gname, hm) for glyf, hm in datas]
        if any(d is None for d in found):
            bad.append(gname)
            continue
        ctrls = [d[1] for d in found]
        if ctrls[default_idx].numberOfContours != 0:
            # Un glyphe vide dans un fichier compte comme absent : la fusion le calcule.
            ctrls = [c for c in ctrls if c.numberOfContours != 0]
        if any(c != ctrls[0] for c in ctrls[1:]):
            bad.append(gname)
    return bad


def _stat_table(font: TTFont, axes: list[tuple[str, list[float], float]], italic: bool) -> None:
    """Table STAT : nomme les positions des axes pour les menus des logiciels."""
    from fontTools.otlLib.builder import buildStatTable

    stat_axes = []
    for tag, values, default in axes:
        entries = []
        for value in values:
            label = _axis_label(tag, value)
            entry = {"value": value, "name": label}
            if value == default and label in ("Regular", "Normal"):
                entry["flags"] = 0x2  # nom omis : « Inter » plutôt que « Inter Regular »
            entries.append(entry)
        stat_axes.append({"tag": tag, "name": {"wght": "Weight", "wdth": "Width"}[tag], "values": entries})
    if italic:
        stat_axes.append({"tag": "ital", "name": "Italic", "values": [{"value": 1, "name": "Italic"}]})
    else:
        stat_axes.append({"tag": "ital", "name": "Italic", "values": [{"value": 0, "name": "Roman", "flags": 0x2, "linkedValue": 1}]})
    buildStatTable(font, stat_axes, elidedFallbackName="Regular")


def _merge_masters(raw: list[tuple[bytes, str]]) -> tuple[list[TTFont], str]:
    """Charge les fichiers à fusionner ; renvoie aussi le type de contours (glyf ou cff)."""
    masters = []
    for data, name in raw:
        font, _kind = _load(data, name)[0]
        if "fvar" in font:
            raise EngineError("mergeVariable")
        masters.append(_clone(font))
    kinds = {"glyf" if "glyf" in m else "cff" if ("CFF " in m or "CFF2" in m) else "other" for m in masters}
    if "other" in kinds:
        raise EngineError("mergeFailed", "bitmap")
    if len(kinds) > 1:
        raise EngineError("mergeMixed")
    return masters, kinds.pop()


def merge(datas, filenames, options_json: str = "{}") -> dict:
    """Fusionne des polices statiques d'une même famille en une police variable TrueType.

    options : { family: "Inter", build: false }
      build = false : vérification seule, build = true : renvoie aussi la police (« font »).

    La fusion est refusée dès qu'un glyphe n'est pas interpolable, plutôt que de livrer une
    police dont certains caractères resteraient figés.
    """
    from fontTools import varLib
    from fontTools.designspaceLib import AxisDescriptor, DesignSpaceDocument, InstanceDescriptor, SourceDescriptor
    from fontTools.varLib.instancer import setMacOverlapFlags

    opts = json.loads(options_json or "{}")
    names = [str(n) for n in filenames]
    raw = [(_as_bytes(d), n) for d, n in zip(datas, names)]
    if len(raw) < 2:
        return {"error": "mergeTooFew"}
    try:
        masters, kind = _merge_masters(raw)
    except EngineError as err:
        return {"error": err.code, "detail": err.detail}
    if len({m["head"].unitsPerEm for m in masters}) > 1:
        return {"error": "mergeFailed", "detail": "unitsPerEm"}

    locs = [_location(m) for m in masters]
    seen: dict[tuple[float, float], str] = {}
    for loc, name in zip(locs, names):
        if loc in seen:
            return {"error": "mergeSameStyle", "files": [seen[loc], name], "weight": _num(loc[0])}
        seen[loc] = name

    glyph_sets = [set(m.getGlyphOrder()) for m in masters]
    differ = set().union(*glyph_sets) - set.intersection(*glyph_sets)
    if differ:
        return {"error": "mergeGlyphSet", "count": len(differ), "chars": _chars_for(masters, differ)}

    default_idx = min(range(len(locs)), key=lambda i: (abs(locs[i][0] - 400), abs(locs[i][1] - 100), locs[i][0]))
    total = len(masters[0].getGlyphOrder())

    def prepared(fonts: list[TTFont]) -> tuple[list[TTFont], list[str]]:
        if kind == "cff":
            fonts, bad = _cff_masters_to_glyf(fonts)
            if bad:
                return fonts, bad
        for f in fonts:
            _clear_overlap_flags(f)
        return fonts, _incompatible_glyphs(fonts, default_idx)

    try:
        masters, bad = prepared(masters)
    except Exception as exc:
        return {"error": "mergeFailed", "detail": f"{type(exc).__name__}: {exc}"}
    if bad:
        return {"error": "mergeIncompatible", "count": len(bad), "total": total, "chars": _chars_for(masters, bad)}

    family = (opts.get("family") or _name(masters[default_idx], 16, 1) or _stem(names[0])).strip()
    italic = _is_italic(masters[default_idx])
    axes = []
    for tag, axis_name, idx in (("wght", "Weight", 0), ("wdth", "Width", 1)):
        values = sorted({loc[idx] for loc in locs})
        if len(values) > 1:
            axes.append((tag, axis_name, values, locs[default_idx][idx]))
    styles = [_location_name(w, wd, italic, _name(m, 17, 2)) for m, (w, wd) in zip(masters, locs)]
    info = {
        "family": family,
        "italic": italic,
        "axes": [{"tag": tag, "min": vals[0], "default": dflt, "max": vals[-1]} for tag, _n, vals, dflt in axes],
        "masters": [{"file": n, "style": s, "weight": w, "width": wd} for n, s, (w, wd) in zip(names, styles, locs)],
        "stem": f"{_safe(family)}{'-Italic' if italic else ''}-VariableFont_{','.join(sorted(a[0] for a in axes))}",
    }
    if not opts.get("build"):
        return {"ok": True, **info}

    def design(fonts: list[TTFont]) -> DesignSpaceDocument:
        ds = DesignSpaceDocument()
        for tag, axis_name, vals, dflt in axes:
            a = AxisDescriptor()
            a.tag, a.name, a.minimum, a.default, a.maximum = tag, axis_name, vals[0], dflt, vals[-1]
            ds.addAxis(a)
        for i, (font, (w, wd), style) in enumerate(zip(fonts, locs, styles)):
            where = {"Weight": w, "Width": wd}
            src = SourceDescriptor()
            src.name, src.font = f"master{i}", font
            src.location = {a[1]: where[a[1]] for a in axes}
            ds.addSource(src)
            inst = InstanceDescriptor()
            inst.familyName, inst.styleName = family, style
            inst.location = dict(src.location)
            ds.addInstance(inst)
        return ds

    warnings = []
    try:
        try:
            vf, _model, _ = varLib.build(design(masters), exclude=["STAT"], drop_implied_oncurves=True)
        except Exception:
            # Crénage impossible à faire varier : on repart de fichiers neufs et on garde celui du style par défaut.
            fresh, _bad = prepared(_merge_masters(raw)[0])
            vf, _model, _ = varLib.build(design(fresh), exclude=["STAT", "GDEF", "GPOS"], drop_implied_oncurves=True)
            for tag in ("GDEF", "GPOS"):
                if tag in fresh[default_idx]:
                    vf[tag] = fresh[default_idx][tag]
            warnings.append({"code": "mergeLayoutStatic", "file": family})
        setMacOverlapFlags(vf["glyf"])
        _set_static_names(vf, family, styles[default_idx])
        vf["name"].setName(re.sub(r"[^A-Za-z0-9]", "", family), 25, 3, 1, 0x409)
        _stat_table(vf, [(tag, vals, dflt) for tag, _n, vals, dflt in axes], italic)
        blob = _sfnt_bytes(vf)
        TTFont(io.BytesIO(blob)).getGlyphOrder()  # relecture : la police produite doit s'ouvrir
    except Exception as exc:
        return {"error": "mergeFailed", "detail": f"{type(exc).__name__}: {exc}"}
    return {"ok": True, **info, "font": blob, "size": len(blob), "warnings": warnings}
