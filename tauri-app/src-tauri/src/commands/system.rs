use std::process::Command;

#[tauri::command]
pub fn open_rdp(address: String) -> Result<(), String> {
    if address.is_empty() {
        return Err("No remote desktop address provided".to_string());
    }

    #[cfg(target_os = "windows")]
    {
        Command::new("mstsc")
            .arg(format!("/v:{}", address))
            .spawn()
            .map_err(|e| format!("Failed to open RDP: {}", e))?;
    }

    #[cfg(target_os = "macos")]
    {
        // Try Microsoft Remote Desktop on macOS
        Command::new("open")
            .args(["-a", "Microsoft Remote Desktop", &format!("rdp://full%20address=s:{}",address)])
            .spawn()
            .map_err(|e| format!("RDP not supported or not installed: {}", e))?;
    }

    #[cfg(target_os = "linux")]
    {
        Command::new("xfreerdp")
            .arg(format!("/v:{}", address))
            .spawn()
            .map_err(|e| format!("Failed to open RDP: {}", e))?;
    }

    Ok(())
}

#[tauri::command]
pub fn open_file_explorer(path: String) -> Result<(), String> {
    if path.is_empty() {
        return Err("No file path provided".to_string());
    }

    #[cfg(target_os = "windows")]
    {
        Command::new("explorer")
            .arg(&path)
            .spawn()
            .map_err(|e| format!("Failed to open explorer: {}", e))?;
    }

    #[cfg(target_os = "macos")]
    {
        Command::new("open")
            .arg(&path)
            .spawn()
            .map_err(|e| format!("Failed to open Finder: {}", e))?;
    }

    #[cfg(target_os = "linux")]
    {
        Command::new("xdg-open")
            .arg(&path)
            .spawn()
            .map_err(|e| format!("Failed to open file manager: {}", e))?;
    }

    Ok(())
}

#[tauri::command]
pub fn open_browser(url: String) -> Result<(), String> {
    if url.is_empty() {
        return Err("No URL provided".to_string());
    }

    // Ensure URL has a scheme
    let full_url = if url.starts_with("http://") || url.starts_with("https://") {
        url
    } else {
        format!("http://{}", url)
    };

    #[cfg(target_os = "windows")]
    {
        Command::new("cmd")
            .args(["/c", "start", &full_url])
            .spawn()
            .map_err(|e| format!("Failed to open browser: {}", e))?;
    }

    #[cfg(target_os = "macos")]
    {
        Command::new("open")
            .arg(&full_url)
            .spawn()
            .map_err(|e| format!("Failed to open browser: {}", e))?;
    }

    #[cfg(target_os = "linux")]
    {
        Command::new("xdg-open")
            .arg(&full_url)
            .spawn()
            .map_err(|e| format!("Failed to open browser: {}", e))?;
    }

    Ok(())
}

#[tauri::command]
pub fn execute_command(command: String) -> Result<(), String> {
    if command.is_empty() {
        return Err("No command provided".to_string());
    }

    #[cfg(target_os = "windows")]
    {
        Command::new("cmd")
            .args(["/c", "start", "cmd", "/k", &command])
            .spawn()
            .map_err(|e| format!("Failed to execute command: {}", e))?;
    }

    #[cfg(target_os = "macos")]
    {
        // Open Terminal.app and run the command
        let script = format!(
            r#"tell application "Terminal" to do script "{}""#,
            command.replace('"', r#"\""#)
        );
        Command::new("osascript")
            .args(["-e", &script])
            .spawn()
            .map_err(|e| format!("Failed to execute command: {}", e))?;
    }

    #[cfg(target_os = "linux")]
    {
        Command::new("x-terminal-emulator")
            .args(["-e", &command])
            .spawn()
            .map_err(|e| format!("Failed to execute command: {}", e))?;
    }

    Ok(())
}
