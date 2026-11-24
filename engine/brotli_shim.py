"""Module `brotli` minimal pour Pyodide : délègue à brotli-wasm côté JavaScript.

fontTools n'utilise que compress() et decompress() pour le WOFF2.
"""
from js import fontaineBrotli  # objet exposé par le worker

MODE_GENERIC = 0
MODE_TEXT = 1
MODE_FONT = 2


class error(Exception):
    pass


def _bytes(js_array) -> bytes:
    return bytes(js_array.to_py())


def compress(data, mode=MODE_GENERIC, quality=11, lgwin=22, lgblock=0):
    from pyodide.ffi import to_js

    try:
        return _bytes(fontaineBrotli.compress(to_js(bytes(data)), int(quality)))
    except Exception as exc:  # pragma: no cover
        raise error(str(exc)) from exc


def decompress(data):
    from pyodide.ffi import to_js

    try:
        return _bytes(fontaineBrotli.decompress(to_js(bytes(data))))
    except Exception as exc:  # pragma: no cover
        raise error(str(exc)) from exc
