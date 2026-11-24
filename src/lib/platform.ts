// Pont vers le système : Tauri dans l'application, repli navigateur pour le développement d'interface.
import { invoke } from '@tauri-apps/api/core';

export const isTauri = typeof window !== 'undefined' && '__TAURI_INTERNALS__' in window;
export const isMac = typeof navigator !== 'undefined' && /Mac/i.test(navigator.userAgent);

export const FONT_EXTENSIONS = ['ttf', 'otf', 'woff', 'woff2', 'ttc', 'otc', 'eot', 'pfb', 'pfa'];

export interface PickedFile {
  name: string;
  path?: string;
  bytes: Uint8Array;
}

const baseName = (p: string) => p.split(/[\\/]/).pop() || p;

export async function readPath(path: string): Promise<PickedFile> {
  const buf = await invoke<ArrayBuffer>('read_file', { path });
  return { name: baseName(path), path, bytes: new Uint8Array(buf) };
}

export async function filesFromBrowser(list: FileList | File[]): Promise<PickedFile[]> {
  const files = Array.from(list);
  return Promise.all(files.map(async (f) => ({ name: f.name, bytes: new Uint8Array(await f.arrayBuffer()) })));
}

/** Fenêtre de choix de fichiers native ; renvoie null si l'utilisateur annule. */
export async function pickFontPaths(title: string): Promise<string[] | null> {
  const { open } = await import('@tauri-apps/plugin-dialog');
  const res = await open({ title, multiple: true, directory: false, filters: [{ name: 'Fonts', extensions: FONT_EXTENSIONS }] });
  if (!res) return null;
  return Array.isArray(res) ? res : [res];
}

export async function pickFolder(title: string, defaultPath?: string): Promise<string | null> {
  if (!isTauri) return null;
  const { open } = await import('@tauri-apps/plugin-dialog');
  const res = await open({ title, directory: true, multiple: false, defaultPath });
  return typeof res === 'string' ? res : null;
}

export async function defaultOutputDir(): Promise<string> {
  if (!isTauri) return '~/Fontshift';
  return invoke<string>('default_output_dir');
}

/** Langues du système d'exploitation, par ordre de préférence (BCP 47). */
export async function systemLocales(): Promise<string[]> {
  if (!isTauri) return [];
  try {
    return await invoke<string[]>('system_locales');
  } catch {
    return [];
  }
}

export async function homeDir(): Promise<string> {
  if (!isTauri) return '';
  return invoke<string>('home_dir');
}

/** Écrit un fichier ; un nom déjà pris reçoit un suffixe « (2) ». Renvoie le chemin final. */
/** Chemin libre pour le sous-dossier d'une conversion (créé à l'écriture du premier fichier). */
export async function prepareOutputDir(base: string, name: string): Promise<string> {
  if (!isTauri) return base;
  return invoke<string>('prepare_output_dir', { base, name });
}

export async function writeOutput(dir: string, name: string, bytes: Uint8Array): Promise<string> {
  if (!isTauri) {
    const url = URL.createObjectURL(new Blob([bytes as BlobPart]));
    const a = document.createElement('a');
    a.href = url;
    a.download = name;
    a.click();
    setTimeout(() => URL.revokeObjectURL(url), 2000);
    return name;
  }
  return invoke<string>('write_file', bytes, {
    headers: { 'x-dir': encodeURIComponent(dir), 'x-name': encodeURIComponent(name) },
  });
}

export async function reveal(path: string) {
  if (!isTauri) return;
  const { revealItemInDir } = await import('@tauri-apps/plugin-opener');
  await revealItemInDir(path);
}

/** Requête HTTP hors CORS (Google Fonts) : passe par Rust dans l'application. */
export async function httpFetch(url: string): Promise<Response> {
  if (!isTauri) return fetch(url);
  const { fetch: tauriFetch } = await import('@tauri-apps/plugin-http');
  return tauriFetch(url, { method: 'GET' });
}

export type DropEvent = { type: 'enter' | 'over' | 'leave' | 'drop'; paths: string[] };

/** Glisser-déposer natif (chemins des fichiers) ; renvoie la fonction de désinscription. */
export async function onNativeDrop(cb: (e: DropEvent) => void): Promise<() => void> {
  if (!isTauri) return () => {};
  const { getCurrentWebview } = await import('@tauri-apps/api/webview');
  return getCurrentWebview().onDragDropEvent((event) => {
    const p = event.payload as { type: string; paths?: string[] };
    cb({ type: p.type as DropEvent['type'], paths: p.paths ?? [] });
  });
}

export async function openSettingsWindow(title: string) {
  if (!isTauri) {
    window.open('?window=settings', 'fontaine-settings', 'width=760,height=800');
    return;
  }
  const { WebviewWindow } = await import('@tauri-apps/api/webviewWindow');
  const existing = await WebviewWindow.getByLabel('settings');
  if (existing) {
    await existing.setFocus();
    return;
  }
  new WebviewWindow('settings', {
    url: 'index.html?window=settings',
    title,
    width: 760,
    height: 800,
    minWidth: 520,
    minHeight: 560,
    resizable: true,
    center: true,
    titleBarStyle: 'overlay',
    hiddenTitle: true,
  });
}

export async function closeCurrentWindow() {
  if (!isTauri) {
    window.close();
    return;
  }
  const { getCurrentWindow } = await import('@tauri-apps/api/window');
  await getCurrentWindow().close();
}

export async function setWindowTitle(title: string) {
  document.title = title;
  if (!isTauri) return;
  const { getCurrentWindow } = await import('@tauri-apps/api/window');
  await getCurrentWindow().setTitle(title);
}

/** Diffusion d'un événement à toutes les fenêtres de l'application. */
export async function broadcast(name: string, payload: unknown) {
  if (isTauri) {
    const { emit } = await import('@tauri-apps/api/event');
    await emit(name, payload);
  } else {
    new BroadcastChannel('fontaine').postMessage({ name, payload });
  }
}

export async function listenAll(name: string, cb: (payload: unknown) => void): Promise<() => void> {
  if (isTauri) {
    const { listen } = await import('@tauri-apps/api/event');
    return listen(name, (e) => cb(e.payload));
  }
  const ch = new BroadcastChannel('fontaine');
  ch.onmessage = (e) => e.data?.name === name && cb(e.data.payload);
  return () => ch.close();
}

/** Mises à jour : false tant qu'aucune adresse n'est configurée (ou hors de l'application). */
export async function updatesEnabled(): Promise<boolean> {
  if (!isTauri) return false;
  return invoke<boolean>('update_enabled');
}

/** Version disponible, ou null si l'application est à jour. */
export async function checkUpdate(): Promise<string | null> {
  const r = await invoke<{ version: string } | null>('update_check');
  return r?.version ?? null;
}

/** Télécharge, vérifie, installe puis relance l'application. */
export async function installUpdate(): Promise<void> {
  await invoke('update_install');
}
