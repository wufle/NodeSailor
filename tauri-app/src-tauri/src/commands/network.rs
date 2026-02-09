use std::net::UdpSocket;

#[tauri::command]
pub fn get_local_ips() -> Vec<String> {
    let mut ips = Vec::new();

    // Get local IP by connecting to an external address (doesn't actually send data)
    if let Ok(socket) = UdpSocket::bind("0.0.0.0:0") {
        if socket.connect("8.8.8.8:80").is_ok() {
            if let Ok(addr) = socket.local_addr() {
                ips.push(addr.ip().to_string());
            }
        }
    }

    // Also try common interfaces via system commands
    #[cfg(any(target_os = "macos", target_os = "linux"))]
    {
        if let Ok(output) = std::process::Command::new("hostname")
            .arg("-I")
            .output()
        {
            let stdout = String::from_utf8_lossy(&output.stdout);
            for ip in stdout.split_whitespace() {
                let ip_str = ip.trim().to_string();
                if !ip_str.is_empty() && !ips.contains(&ip_str) {
                    ips.push(ip_str);
                }
            }
        }

        // macOS ifconfig
        if let Ok(output) = std::process::Command::new("ifconfig").output() {
            let stdout = String::from_utf8_lossy(&output.stdout);
            let re = regex::Regex::new(r"inet (\d+\.\d+\.\d+\.\d+)").unwrap();
            for cap in re.captures_iter(&stdout) {
                let ip = cap[1].to_string();
                if ip != "127.0.0.1" && !ips.contains(&ip) {
                    ips.push(ip);
                }
            }
        }
    }

    #[cfg(target_os = "windows")]
    {
        if let Ok(output) = std::process::Command::new("ipconfig").output() {
            let stdout = String::from_utf8_lossy(&output.stdout);
            let re = regex::Regex::new(r"IPv4.*?:\s*(\d+\.\d+\.\d+\.\d+)").unwrap();
            for cap in re.captures_iter(&stdout) {
                let ip = cap[1].to_string();
                if ip != "127.0.0.1" && !ips.contains(&ip) {
                    ips.push(ip);
                }
            }
        }
    }

    ips
}
