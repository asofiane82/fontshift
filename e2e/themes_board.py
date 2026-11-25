"""Planche des thèmes à partir de captures réelles de l'application compilée (écran Conversion, deux polices).

    python3 e2e/themes_board.py      # mêmes prérequis que e2e/run.py ; écrit design/brand/preview/fontshift-themes.png
"""
import base64, json, os, re, subprocess, tempfile, time
from PIL import ImageFont
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.options import ArgOptions
from selenium.webdriver.remote.file_detector import UselessFileDetector

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
APP = os.path.join(ROOT, 'src-tauri/target/release/fontshift')
OUT = os.path.join(ROOT, 'design/brand/preview/fontshift-themes.png')
SHOTS = tempfile.mkdtemp(prefix='fontshift-themes-')
FONTS = [f'{ROOT}/engine/tests/{f}' for f in ('playfair-display-latin-wght-normal.woff2', 'playfair-display-latin-600-italic.woff2')]
PAL = json.loads(subprocess.run(['node', '--input-type=module', '-e',
    f"import {{ BASE, ORDER, tokens }} from '{ROOT}/src/lib/theme/palette.js';"
    "console.log(JSON.stringify(ORDER.map(k => ({ key: k, name: BASE[k].name, light: tokens(k, false), dark: tokens(k, true) }))))"],
    capture_output=True, text=True, check=True).stdout)

# ---------------------------------------------------------------- captures
home = tempfile.mkdtemp(prefix='fontshift-home-'); os.makedirs(home + '/Desktop', exist_ok=True)
env = dict(os.environ, HOME=home, LANG='fr_FR.UTF-8', LANGUAGE='fr', DISPLAY=':97', XDG_CONFIG_HOME=home + '/.config', XDG_DATA_HOME=home + '/.local/share')
xvfb = subprocess.Popen(['Xvfb', ':97', '-screen', '0', '1600x1300x24'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL); time.sleep(1.5)
drv = subprocess.Popen([os.path.expanduser('~/.cargo/bin/tauri-driver')], env=env, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT); time.sleep(1.5)
opts = ArgOptions(); opts.set_capability('tauri:options', {'application': APP}); opts.set_capability('browserName', 'wry')
d = webdriver.Remote(command_executor='http://127.0.0.1:4444', options=opts); d.file_detector = UselessFileDetector()
try:
    d.set_window_size(1280, 1080); w = WebDriverWait(d, 90)
    for t in PAL:
        for mode in ('light', 'dark'):
            w.until(lambda x: x.find_elements(By.CSS_SELECTOR, 'aside nav button'))
            d.execute_script("localStorage.setItem('fontaine.theme', arguments[0]); localStorage.setItem('fontaine.appearance', arguments[1]);"
                             "localStorage.setItem('fontaine.lang', 'fr'); location.reload();", t['key'], mode)
            time.sleep(2); w.until(lambda x: x.find_elements(By.CSS_SELECTOR, 'aside nav button'))
            d.find_element(By.CSS_SELECTOR, 'input[type=file]').send_keys('\n'.join(FONTS))
            w.until(lambda x: len(x.find_elements(By.CSS_SELECTOR, 'main ul li')) >= 2 and 'Analyse' not in x.find_element(By.TAG_NAME, 'main').text)
            time.sleep(1.2); d.save_screenshot(f"{SHOTS}/{t['key']}-{mode}.png"); print('capture', t['key'], mode, flush=True)
finally:
    try: d.quit()
    except Exception: pass
    drv.terminate(); xvfb.terminate()

# ---------------------------------------------------------------- planche
def lum(h):
    f = lambda v: v / 12.92 if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4
    r, g, b = (f(int(h[i:i + 2], 16) / 255) for i in (1, 3, 5)); return 0.2126 * r + 0.7152 * g + 0.0722 * b
cr = lambda a, b: (max(lum(a), lum(b)) + 0.05) / (min(lum(a), lum(b)) + 0.05)
num = lambda v: f'{v:.1f}'.replace('.', ',')
FONT = 'font-family="Inter, sans-serif"'
INK, MUTED, BG, LINE = '#16140F', '#5E5A52', '#F1F1EF', '#D4D4D2'
W, M, G = 2000, 60, 40
SW = (W - 2 * M - G) // 2; SH = round(SW * 1080 / 1280)
esc = lambda s: s.replace('&', '&amp;').replace('<', '&lt;')
text = lambda x, y, s, size=16, weight=400, fill=INK, anchor='start': (
    f'<text x="{x}" y="{y}" {FONT} font-size="{size}" font-weight="{weight}" fill="{fill}" text-anchor="{anchor}">{esc(s)}</text>')
def img(x, y, w, h, path, n=[0]):
    n[0] += 1; b64 = base64.b64encode(open(path, 'rb').read()).decode()
    return (f'<clipPath id="c{n[0]}"><rect x="{x}" y="{y}" width="{w}" height="{h}" rx="14"/></clipPath>'
            f'<image x="{x}" y="{y}" width="{w}" height="{h}" href="data:image/png;base64,{b64}" clip-path="url(#c{n[0]})" preserveAspectRatio="none"/>'
            f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="14" fill="none" stroke="{LINE}"/>')
logo = open(f'{ROOT}/design/brand/svg/fontshift-logo-dark.svg').read()
vb = re.search(r'viewBox="([^"]+)"', logo).group(1).split()
inner = re.sub(r'<title>.*?</title>', '', re.sub(r'^.*?<svg[^>]*>|</svg>\s*$', '', logo, flags=re.S), flags=re.S)
parts = [f'<rect width="{W}" height="230" fill="{INK}"/>', f'<g transform="translate({M},83) scale({64 / float(vb[3])})">{inner}</g>',
         text(W - M, 92, f'Thèmes de l’application — {len(PAL)} thèmes', 38, 600, '#FCF8EF', 'end'),
         text(W - M, 136, 'Captures réelles · écran Conversion · clair et sombre', 22, 400, '#C9C2B4', 'end'),
         text(W - M, 176, 'Textes ≥ 4,5:1 · contours des champs, menus et boutons de sélection ≥ 3:1 (WCAG 1.4.11)', 19, 400, '#A39B8C', 'end')]
y = 310
semi = ImageFont.truetype('/usr/share/fonts/opentype/inter/Inter-SemiBold.otf', 34)
for i, t in enumerate(PAL):
    parts.append(text(M, y, t['name'], 34, 600))
    if i == 0: parts.append(text(round(M + semi.getlength(t['name']) + 14), y, '· par défaut', 24, 400, MUTED))
    sx = W - M
    for label, c in reversed((('fond clair', t['light']['background']), ('accent clair', t['light']['accentFill']), ('accent sombre', t['dark']['accentFill']))):
        sx -= 250
        parts.append(f'<rect x="{sx}" y="{y - 24}" width="30" height="30" rx="7" fill="{c}" stroke="#00000022"/>' + text(sx + 40, y - 3, f'{label} {c.upper()}', 17, 500))
    y += 28
    for j, mode in enumerate(('light', 'dark')):
        T = t[mode]; x = M + j * (SW + G)
        parts.append(img(x, y, SW, SH, f"{SHOTS}/{t['key']}-{mode}.png"))
        bgs = (T['background'], T['surface'], T['sidebar'], T['surfaceSunken'])
        cap = (f"{'Clair' if mode == 'light' else 'Sombre'} · texte {num(min(cr(T['textPrimary'], b) for b in bgs))}:1 · "
               f"texte discret {num(min(cr(T['textTertiary'], b) for b in bgs[:2] + bgs[3:]))}:1 · "
               f"bouton {num(cr(T['accentForeground'], T['accentFill']))}:1 · "
               f"contours {num(min(cr(T['borderStrong'], b) for b in bgs[:2]))}:1")
        parts.append(text(x, y + SH + 34, cap, 18, 400, MUTED))
    y += SH + 110
H = y - 20
svg = f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}"><rect width="{W}" height="{H}" fill="{BG}"/>' + ''.join(parts) + '</svg>'
tmp = os.path.join(SHOTS, 'board.svg'); open(tmp, 'w').write(svg)
subprocess.run(['rsvg-convert', tmp, '-o', OUT], check=True)
print('planche', OUT, W, '×', H)
