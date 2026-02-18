use std::fs;
use base64::{Engine as _, engine::general_purpose};
use tauri::AppHandle;

#[tauri::command]
pub fn load_file(path: String) -> Result<String, String> {
    fs::read_to_string(&path).map_err(|e| format!("Failed to read file: {}", e))
}

#[tauri::command]
pub fn save_file(path: String, content: String) -> Result<(), String> {
    fs::write(&path, &content).map_err(|e| format!("Failed to write file: {}", e))
}

#[tauri::command]
pub async fn show_save_dialog(app_handle: AppHandle, current_path: String) -> Result<String, String> {
    use tauri::async_runtime::spawn;

    let result = spawn(async move {
        // Extract filename from path
        let filename = std::path::Path::new(&current_path)
            .file_name()
            .and_then(|n| n.to_str())
            .unwrap_or("file");

        // Use tauri's message dialog
        use tauri_plugin_dialog::{DialogExt, MessageDialogButtons, MessageDialogKind};

        let answer = app_handle
            .dialog()
            .message(format!(
                "Save changes to '{}'?\n\nOverwrite: Save to existing file\nSave As: Choose new location\nCancel: Don't save",
                filename
            ))
            .title("Save File")
            .kind(MessageDialogKind::Info)
            .buttons(MessageDialogButtons::OkCancelCustom("Overwrite".to_string(), "Save As".to_string()))
            .blocking_show();

        match answer {
            true => Ok("overwrite".to_string()),   // OK button (Overwrite)
            false => Ok("new".to_string()),        // Custom button (Save As)
        }
    })
    .await
    .map_err(|e| format!("Dialog error: {}", e))?;

    result
}

#[tauri::command]
pub fn read_image_as_base64(path: String) -> Result<String, String> {
    let data = fs::read(&path)
        .map_err(|e| format!("Failed to read image: {}", e))?;

    let ext = std::path::Path::new(&path)
        .extension()
        .and_then(|e| e.to_str())
        .unwrap_or("png")
        .to_lowercase();

    let mime = match ext.as_str() {
        "jpg" | "jpeg" => "image/jpeg",
        "gif" => "image/gif",
        "svg" => "image/svg+xml",
        "webp" => "image/webp",
        "bmp" => "image/bmp",
        _ => "image/png",
    };

    let b64 = general_purpose::STANDARD.encode(&data);
    Ok(format!("data:{};base64,{}", mime, b64))
}
