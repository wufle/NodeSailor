use std::process::Command;
use regex::Regex;

fn ping_single(ip: &str) -> bool {
    let param = if cfg!(target_os = "windows") { "-n" } else { "-c" };

    let mut cmd = Command::new("ping");
    cmd.args([param, "1", ip]);

    // Hide the console window on Windows
    #[cfg(target_os = "windows")]
    {
        use std::os::windows::process::CommandExt;
        const CREATE_NO_WINDOW: u32 = 0x08000000;
        cmd.creation_flags(CREATE_NO_WINDOW);
    }

    let output = cmd.output();

    match output {
        Ok(result) => {
            let stdout = String::from_utf8_lossy(&result.stdout);
            // Case-insensitive TTL check (works on macOS, Linux, Windows)
            let re = Regex::new(r"(?i)ttl=").unwrap();
            re.is_match(&stdout)
        }
        Err(_) => false,
    }
}

#[tauri::command]
pub async fn ping_ips(ips: Vec<String>) -> Vec<bool> {
    let mut handles = Vec::new();

    for ip in ips {
        let ip_clone = ip.clone();
        handles.push(tokio::task::spawn_blocking(move || {
            ping_single(&ip_clone)
        }));
    }

    let mut results = Vec::new();
    for handle in handles {
        match handle.await {
            Ok(result) => results.push(result),
            Err(_) => results.push(false),
        }
    }

    results
}
