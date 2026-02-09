use serde::{Deserialize, Serialize};
use std::fs;
use std::path::PathBuf;

#[derive(Serialize, Deserialize, Default)]
pub struct AppSettings {
    #[serde(default)]
    pub hide_start_menu: bool,
    #[serde(default)]
    pub last_file_path: String,
    #[serde(default)]
    pub window_geometry: String,
}

fn settings_path() -> PathBuf {
    let config_dir = dirs::config_dir().unwrap_or_else(|| PathBuf::from("."));
    let app_dir = config_dir.join("NodeSailor");
    fs::create_dir_all(&app_dir).ok();
    app_dir.join("settings.json")
}

#[tauri::command]
pub fn save_settings(settings: serde_json::Value) -> Result<(), String> {
    let path = settings_path();

    // Load existing settings
    let mut current: serde_json::Value = if path.exists() {
        let content = fs::read_to_string(&path).unwrap_or_default();
        serde_json::from_str(&content).unwrap_or(serde_json::json!({}))
    } else {
        serde_json::json!({})
    };

    // Merge new settings
    if let (Some(current_obj), Some(new_obj)) = (current.as_object_mut(), settings.as_object()) {
        for (key, value) in new_obj {
            current_obj.insert(key.clone(), value.clone());
        }
    }

    let content = serde_json::to_string_pretty(&current)
        .map_err(|e| format!("Failed to serialize settings: {}", e))?;

    fs::write(&path, content)
        .map_err(|e| format!("Failed to write settings: {}", e))?;

    Ok(())
}

#[tauri::command]
pub fn load_settings() -> Result<serde_json::Value, String> {
    let path = settings_path();

    if !path.exists() {
        return Ok(serde_json::json!({}));
    }

    let content = fs::read_to_string(&path)
        .map_err(|e| format!("Failed to read settings: {}", e))?;

    serde_json::from_str(&content)
        .map_err(|e| format!("Failed to parse settings: {}", e))
}
