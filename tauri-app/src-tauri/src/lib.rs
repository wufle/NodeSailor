mod commands;

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    tauri::Builder::default()
        .plugin(tauri_plugin_dialog::init())
        .plugin(tauri_plugin_shell::init())
        .plugin(tauri_plugin_fs::init())
        .setup(|app| {
            if cfg!(debug_assertions) {
                app.handle().plugin(
                    tauri_plugin_log::Builder::default()
                        .level(log::LevelFilter::Info)
                        .build(),
                )?;
            }
            Ok(())
        })
        .invoke_handler(tauri::generate_handler![
            commands::file_io::load_file,
            commands::file_io::save_file,
            commands::file_io::show_save_dialog,
            commands::ping::ping_ips,
            commands::system::open_rdp,
            commands::system::open_file_explorer,
            commands::system::open_browser,
            commands::system::execute_command,
            commands::network::get_local_ips,
            commands::settings::save_settings,
            commands::settings::load_settings,
        ])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
