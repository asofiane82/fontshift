//! Fontaine — côté natif volontairement minimal : lecture et écriture des fichiers choisis
//! par l'utilisateur, dossier de sortie par défaut. La conversion elle-même tourne dans
//! l'interface (fontTools via Pyodide), identique sur macOS, Windows et Linux.

use std::fs;
use std::path::{Path, PathBuf};

use tauri::ipc::{InvokeBody, Request, Response};
use tauri::Manager;

/// Lit un fichier de police déposé ou choisi par l'utilisateur et renvoie ses octets bruts.
#[tauri::command]
fn read_file(path: String) -> Result<Response, String> {
    let meta = fs::metadata(&path).map_err(|e| e.to_string())?;
    if !meta.is_file() {
        return Err("not-a-file".into());
    }
    // Garde-fou : une police dépasse rarement quelques dizaines de mégaoctets.
    if meta.len() > 256 * 1024 * 1024 {
        return Err("too-large".into());
    }
    fs::read(&path).map(Response::new).map_err(|e| e.to_string())
}

fn percent_decode(input: &str) -> Result<String, String> {
    let bytes = input.as_bytes();
    let mut out = Vec::with_capacity(bytes.len());
    let mut i = 0;
    while i < bytes.len() {
        if bytes[i] == b'%' && i + 2 < bytes.len() {
            let hex = std::str::from_utf8(&bytes[i + 1..i + 3]).map_err(|e| e.to_string())?;
            out.push(u8::from_str_radix(hex, 16).map_err(|e| e.to_string())?);
            i += 3;
        } else {
            out.push(bytes[i]);
            i += 1;
        }
    }
    String::from_utf8(out).map_err(|e| e.to_string())
}

/// Nom de fichier sans séparateur ni composant relatif.
fn sanitize_name(name: &str) -> Result<String, String> {
    let clean: String = name
        .chars()
        .map(|c| if matches!(c, '/' | '\\' | ':' | '*' | '?' | '"' | '<' | '>' | '|') || c.is_control() { '_' } else { c })
        .collect();
    let clean = clean.trim().trim_matches('.').to_string();
    if clean.is_empty() {
        return Err("invalid-name".into());
    }
    Ok(clean)
}

/// Premier chemin libre : « Nom.woff2 », puis « Nom (2).woff2 »…
fn unique_path(dir: &Path, name: &str) -> PathBuf {
    let candidate = dir.join(name);
    if !candidate.exists() {
        return candidate;
    }
    let (stem, ext) = match name.rfind('.') {
        Some(i) if i > 0 => (&name[..i], &name[i..]),
        _ => (name, ""),
    };
    (2..)
        .map(|n| dir.join(format!("{stem} ({n}){ext}")))
        .find(|p| !p.exists())
        .expect("chemin libre")
}

/// Écrit un fichier converti. Corps brut = octets ; en-têtes x-dir et x-name (encodés URI).
#[tauri::command]
fn write_file(request: Request<'_>) -> Result<String, String> {
    let header = |key: &str| -> Result<String, String> {
        let raw = request
            .headers()
            .get(key)
            .ok_or_else(|| format!("missing-{key}"))?
            .to_str()
            .map_err(|e| e.to_string())?;
        percent_decode(raw)
    };
    let dir = PathBuf::from(header("x-dir")?);
    let name = sanitize_name(&header("x-name")?)?;
    let InvokeBody::Raw(data) = request.body() else {
        return Err("expected-raw-body".into());
    };
    fs::create_dir_all(&dir).map_err(|e| e.to_string())?;
    let target = unique_path(&dir, &name);
    fs::write(&target, data).map_err(|e| e.to_string())?;
    Ok(target.to_string_lossy().into_owned())
}

/// Dossier de sortie proposé par défaut : Bureau/Fontaine (ou Documents, ou le dossier personnel).
#[tauri::command]
fn default_output_dir(app: tauri::AppHandle) -> Result<String, String> {
    let paths = app.path();
    let base = paths
        .desktop_dir()
        .or_else(|_| paths.document_dir())
        .or_else(|_| paths.home_dir())
        .map_err(|e| e.to_string())?;
    Ok(base.join("Fontaine").to_string_lossy().into_owned())
}

#[tauri::command]
fn home_dir(app: tauri::AppHandle) -> Result<String, String> {
    app.path().home_dir().map(|p| p.to_string_lossy().into_owned()).map_err(|e| e.to_string())
}

/// Langues préférées du système (les vues web ne les exposent pas de façon fiable partout).
#[tauri::command]
fn system_locales() -> Vec<String> {
    sys_locale::get_locales().collect()
}

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    tauri::Builder::default()
        .plugin(tauri_plugin_dialog::init())
        .plugin(tauri_plugin_http::init())
        .plugin(tauri_plugin_opener::init())
        .invoke_handler(tauri::generate_handler![read_file, write_file, default_output_dir, home_dir, system_locales])
        .run(tauri::generate_context!())
        .expect("erreur au lancement de Fontaine");
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn decodes_accented_paths() {
        assert_eq!(percent_decode("Bureau%2FPolices%20%C3%A9t%C3%A9").unwrap(), "Bureau/Polices été");
    }

    #[test]
    fn sanitizes_names() {
        assert_eq!(sanitize_name("../Inter[wght].woff2").unwrap(), "_Inter[wght].woff2");
        assert!(sanitize_name("..").is_err());
    }

    #[test]
    fn finds_free_name() {
        let dir = std::env::temp_dir().join("fontaine-test-unique");
        let _ = fs::remove_dir_all(&dir);
        fs::create_dir_all(&dir).unwrap();
        fs::write(dir.join("A.woff2"), b"x").unwrap();
        assert_eq!(unique_path(&dir, "A.woff2"), dir.join("A (2).woff2"));
        let _ = fs::remove_dir_all(&dir);
    }
}
