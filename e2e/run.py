"""Test de bout en bout de l'application compilée (Linux, WebKitGTK) via tauri-driver.

    python3 e2e/run.py            # nécessite Xvfb, WebKitWebDriver et tauri-driver
"""
import os, subprocess, sys, tempfile, time, shutil, json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.options import ArgOptions
from selenium.webdriver.remote.file_detector import UselessFileDetector

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
APP = os.path.join(ROOT, "src-tauri/target/release/fontaine")
SHOTS = os.path.join(ROOT, "e2e/shots"); os.makedirs(SHOTS, exist_ok=True)
FONTS = [os.path.join(ROOT, "engine/tests", f) for f in ("playfair-display-latin-wght-normal.woff2", "playfair-display-latin-600-italic.woff2")]
home = tempfile.mkdtemp(prefix="fontaine-home-")
os.makedirs(os.path.join(home, "Desktop"), exist_ok=True)
env = dict(os.environ, HOME=home, LANG=os.environ.get("E2E_LANG", "fr_FR.UTF-8"), LANGUAGE=os.environ.get("E2E_LANGUAGE", "fr"), DISPLAY=":99",
           XDG_CONFIG_HOME=os.path.join(home, ".config"), XDG_DATA_HOME=os.path.join(home, ".local/share"))
env.pop("XDG_DESKTOP_DIR", None)
xvfb = subprocess.Popen(["Xvfb", ":99", "-screen", "0", "1440x960x24"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
time.sleep(1.5)
driver_proc = subprocess.Popen([os.path.expanduser("~/.cargo/bin/tauri-driver")], env=env, stdout=open("/tmp/tauri-driver.log", "w"), stderr=subprocess.STDOUT)
time.sleep(1.5)
ok = True
def nav(label):
    btns = d.find_elements(By.CSS_SELECTOR, "aside button")
    for b in btns:
        if label.lower() in (b.get_attribute("textContent") or "").lower():
            d.execute_script("arguments[0].click()", b)
            return True
    print("   boutons :", [b.get_attribute("textContent") for b in btns])
    return False

def check(cond, label):
    global ok
    print(("OK   " if cond else "FAIL ") + label, flush=True)
    ok = ok and bool(cond)

opts = ArgOptions()
opts.set_capability("tauri:options", {"application": APP})
opts.set_capability("browserName", "wry")
d = webdriver.Remote(command_executor="http://127.0.0.1:4444", options=opts)
d.file_detector = UselessFileDetector()
try:
    d.set_window_size(1280, 840)
    wait = WebDriverWait(d, 60)
    wait.until(lambda x: x.find_elements(By.CSS_SELECTOR, "aside nav button"))
    time.sleep(1.5)
    d.save_screenshot(os.path.join(SHOTS, "01-conversion-vide.png"))
    check("Convertir vos polices" in d.page_source, "écran Conversion en français")

    inp = d.find_element(By.CSS_SELECTOR, "input[type=file]")
    inp.send_keys("\n".join(FONTS))
    wait.until(lambda x: len(x.find_elements(By.CSS_SELECTOR, "main ul li")) >= 2 and "Analyse" not in x.find_element(By.TAG_NAME, "main").text)
    time.sleep(1)
    d.save_screenshot(os.path.join(SHOTS, "02-conversion-fichiers.png"))
    check("Variable" in d.find_element(By.TAG_NAME, "main").text, "police variable reconnue")

    cta = [b for b in d.find_elements(By.CSS_SELECTOR, "main button") if b.text.startswith("Convertir 2")]
    check(cta, "bouton Convertir 2 polices")
    cta[0].click()
    time.sleep(0.6)
    d.save_screenshot(os.path.join(SHOTS, "03-conversion-en-cours.png"))
    WebDriverWait(d, 240).until(lambda x: "Voir les résultats" in x.find_element(By.TAG_NAME, "main").text)
    time.sleep(0.8)
    d.save_screenshot(os.path.join(SHOTS, "04-conversion-terminee.png"))
    out_dir = next((p for p in (os.path.join(home, "Desktop", "Fontaine"), os.path.join(home, "Documents", "Fontaine"), os.path.join(home, "Fontaine")) if os.path.isdir(p)), "")
    files = sorted(os.listdir(out_dir)) if os.path.isdir(out_dir) else []
    print("   fichiers :", files)
    check(any(f.endswith(".woff2") for f in files) and "fontaine-fonts.css" in files, "fichiers WOFF2/WOFF et CSS écrits sur le disque")

    nav("Résultats")
    time.sleep(1)
    d.save_screenshot(os.path.join(SHOTS, "05-resultats.png"))
    check("@font-face" in d.page_source, "code @font-face affiché")

    nav("variables")
    time.sleep(1)
    d.save_screenshot(os.path.join(SHOTS, "06-variables.png"))
    check("Graisse" in d.page_source, "curseur d'axe wght")

    nav("Google")
    try:
        WebDriverWait(d, 25).until(lambda x: "Chargement du catalogue" not in x.find_element(By.TAG_NAME, "main").text)
    except Exception:
        pass
    time.sleep(2)
    d.save_screenshot(os.path.join(SHOTS, "07-google-fonts.png"))
    main_text = d.find_element(By.TAG_NAME, "main").text
    print("   catalogue :", "indisponible (réseau)" if "indisponible" in main_text else "chargé")

    # Réglages : nouvelle fenêtre, changement de thème et de langue répercuté sur la fenêtre principale
    main_handle = d.current_window_handle
    nav("Réglages")
    WebDriverWait(d, 20).until(lambda x: len(x.window_handles) > 1)
    settings = [h for h in d.window_handles if h != main_handle][0]
    d.switch_to.window(settings)
    WebDriverWait(d, 20).until(lambda x: "Thème" in x.page_source)
    time.sleep(1)
    d.save_screenshot(os.path.join(SHOTS, "08-reglages.png"))
    [b for b in d.find_elements(By.CSS_SELECTOR, "[role=radio]") if "Plum & Lavender" in b.text][0].click()
    [b for b in d.find_elements(By.CSS_SELECTOR, "[role=radio]") if "Sombre" in b.text][0].click()
    time.sleep(0.8)
    d.save_screenshot(os.path.join(SHOTS, "09-reglages-plum-sombre.png"))
    d.find_element(By.CSS_SELECTOR, "[aria-haspopup=listbox]").click()
    time.sleep(0.3)
    [o for o in d.find_elements(By.CSS_SELECTOR, "[role=option]") if "English" in o.text][0].click()
    time.sleep(0.8)
    check("Settings" in d.page_source, "réglages traduits en anglais")
    d.switch_to.window(main_handle)
    time.sleep(1.2)
    theme = d.execute_script("return document.documentElement.dataset.theme + '/' + document.documentElement.dataset.mode + '/' + document.documentElement.lang")
    print("   fenêtre principale :", theme)
    check(theme == "plum/dark/en", "thème, apparence et langue synchronisés")
    nav("Conversion")
    time.sleep(1)
    d.save_screenshot(os.path.join(SHOTS, "10-conversion-plum-en.png"))
finally:
    try:
        d.quit()
    except Exception:
        pass
    driver_proc.terminate(); xvfb.terminate()
    shutil.rmtree(home, ignore_errors=True)
print("RESULT", "PASS" if ok else "FAIL")
