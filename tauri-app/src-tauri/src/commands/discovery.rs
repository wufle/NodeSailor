use regex::Regex;
use serde::{Deserialize, Serialize};
use std::collections::HashMap;
use std::process::Command;
use tauri::Emitter;

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct SubnetInfo {
    pub ip: String,
    pub subnet_mask: String,
    pub cidr: String,
    pub interface_name: String,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct DiscoveredDevice {
    pub ip: String,
    pub hostname: String,
    pub mac_address: String,
    pub vendor: String,
    pub open_ports: Vec<u16>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct DiscoveryProgress {
    pub phase: String,
    pub current: u32,
    pub total: u32,
    pub found_so_far: u32,
    pub message: String,
}

fn subnet_mask_to_prefix(mask: &str) -> u8 {
    mask.split('.')
        .filter_map(|o| o.parse::<u8>().ok())
        .map(|o| o.count_ones())
        .sum::<u32>() as u8
}

fn generate_scan_ips(ip: &str, mask: &str) -> Vec<String> {
    let ip_parts: Vec<u32> = ip.split('.').filter_map(|p| p.parse().ok()).collect();
    let mask_parts: Vec<u32> = mask.split('.').filter_map(|p| p.parse().ok()).collect();

    if ip_parts.len() != 4 || mask_parts.len() != 4 {
        return vec![];
    }

    let ip_u32 =
        (ip_parts[0] << 24) | (ip_parts[1] << 16) | (ip_parts[2] << 8) | ip_parts[3];
    let mask_u32 =
        (mask_parts[0] << 24) | (mask_parts[1] << 16) | (mask_parts[2] << 8) | mask_parts[3];

    let network = ip_u32 & mask_u32;
    let broadcast = network | !mask_u32;
    let host_count = broadcast - network;

    if host_count > 4094 || host_count == 0 {
        return vec![];
    }

    ((network + 1)..broadcast)
        .map(|addr| {
            format!(
                "{}.{}.{}.{}",
                (addr >> 24) & 0xFF,
                (addr >> 16) & 0xFF,
                (addr >> 8) & 0xFF,
                addr & 0xFF
            )
        })
        .collect()
}

fn ping_single(ip: &str) -> bool {
    let param = if cfg!(target_os = "windows") { "-n" } else { "-c" };
    let timeout_param = if cfg!(target_os = "windows") {
        vec!["-w", "1000"]
    } else {
        vec!["-W", "1"]
    };

    let mut cmd = Command::new("ping");
    cmd.args([param, "1"]);
    cmd.args(&timeout_param);
    cmd.arg(ip);

    #[cfg(target_os = "windows")]
    {
        use std::os::windows::process::CommandExt;
        const CREATE_NO_WINDOW: u32 = 0x08000000;
        cmd.creation_flags(CREATE_NO_WINDOW);
    }

    match cmd.output() {
        Ok(result) => {
            let stdout = String::from_utf8_lossy(&result.stdout);
            let re = Regex::new(r"(?i)ttl=").unwrap();
            re.is_match(&stdout)
        }
        Err(_) => false,
    }
}

fn read_arp_table() -> HashMap<String, String> {
    let mut map = HashMap::new();

    let mut cmd = Command::new("arp");
    cmd.arg("-a");

    #[cfg(target_os = "windows")]
    {
        use std::os::windows::process::CommandExt;
        const CREATE_NO_WINDOW: u32 = 0x08000000;
        cmd.creation_flags(CREATE_NO_WINDOW);
    }

    if let Ok(output) = cmd.output() {
        let stdout = String::from_utf8_lossy(&output.stdout);
        let re = Regex::new(r"(\d+\.\d+\.\d+\.\d+)\s+([0-9a-fA-F]{2}[:-][0-9a-fA-F]{2}[:-][0-9a-fA-F]{2}[:-][0-9a-fA-F]{2}[:-][0-9a-fA-F]{2}[:-][0-9a-fA-F]{2})")
            .unwrap();
        for cap in re.captures_iter(&stdout) {
            let ip = cap[1].to_string();
            let mac = cap[2].to_string().to_uppercase();
            map.insert(ip, mac);
        }
    }

    map
}

fn resolve_hostname(ip: &str) -> String {
    #[cfg(target_os = "windows")]
    {
        use std::os::windows::process::CommandExt;
        const CREATE_NO_WINDOW: u32 = 0x08000000;

        let mut cmd = Command::new("ping");
        cmd.args(["-a", "-n", "1", "-w", "1000", ip]);
        cmd.creation_flags(CREATE_NO_WINDOW);

        if let Ok(output) = cmd.output() {
            let stdout = String::from_utf8_lossy(&output.stdout);
            let re = Regex::new(r"Pinging\s+(\S+)\s+\[").unwrap();
            if let Some(cap) = re.captures(&stdout) {
                let name = cap[1].to_string();
                if name != ip {
                    return name;
                }
            }
        }
    }

    let mut cmd = Command::new("nslookup");
    cmd.arg(ip);

    #[cfg(target_os = "windows")]
    {
        use std::os::windows::process::CommandExt;
        const CREATE_NO_WINDOW: u32 = 0x08000000;
        cmd.creation_flags(CREATE_NO_WINDOW);
    }

    if let Ok(output) = cmd.output() {
        let stdout = String::from_utf8_lossy(&output.stdout);
        let re = Regex::new(r"(?i)Name:\s+(\S+)").unwrap();
        let matches: Vec<_> = re.captures_iter(&stdout).collect();
        if matches.len() >= 2 {
            return matches[1][1].to_string();
        } else if matches.len() == 1 {
            return matches[0][1].to_string();
        }
    }

    String::new()
}

fn check_port(ip: &str, port: u16) -> bool {
    use std::net::{SocketAddr, TcpStream};
    use std::time::Duration;

    let addr: SocketAddr = format!("{}:{}", ip, port).parse().unwrap();
    TcpStream::connect_timeout(&addr, Duration::from_millis(500)).is_ok()
}

/// Parse a single CSV line, handling quoted fields that may contain commas.
fn parse_csv_line(line: &str) -> Vec<String> {
    let mut fields = Vec::new();
    let mut current = String::new();
    let mut in_quotes = false;

    for ch in line.chars() {
        if ch == '"' {
            in_quotes = !in_quotes;
        } else if ch == ',' && !in_quotes {
            fields.push(current.clone());
            current.clear();
        } else {
            current.push(ch);
        }
    }
    fields.push(current);
    fields
}

/// Load the IEEE OUI database from the bundled oui.csv resource.
fn load_oui_table(app_handle: &tauri::AppHandle) -> HashMap<String, String> {
    use tauri::Manager;

    let resource_path = app_handle
        .path()
        .resource_dir()
        .unwrap_or_default()
        .join("oui.csv");

    let mut map = HashMap::new();
    let content = match std::fs::read_to_string(&resource_path) {
        Ok(c) => c,
        Err(_) => return map,
    };

    for line in content.lines().skip(1) {
        let parts = parse_csv_line(line);
        if parts.len() >= 3 {
            let prefix = parts[1].trim().to_uppercase();
            let org = parts[2].trim().to_string();
            if prefix.len() == 6 && prefix.chars().all(|c| c.is_ascii_hexdigit()) {
                map.insert(prefix, org);
            }
        }
    }

    map
}

/// Look up the vendor name for a MAC address using the OUI table.
fn lookup_mac_vendor(mac: &str, oui_table: &HashMap<String, String>) -> String {
    let cleaned: String = mac.chars().filter(|c| c.is_ascii_hexdigit()).collect();
    if cleaned.len() < 6 {
        return String::new();
    }
    let prefix = cleaned[..6].to_uppercase();
    oui_table.get(&prefix).cloned().unwrap_or_default()
}

#[tauri::command]
pub fn get_subnets() -> Result<Vec<SubnetInfo>, String> {
    let mut subnets = Vec::new();

    #[cfg(target_os = "windows")]
    {
        let mut cmd = Command::new("ipconfig");
        cmd.arg("/all");

        use std::os::windows::process::CommandExt;
        const CREATE_NO_WINDOW: u32 = 0x08000000;
        cmd.creation_flags(CREATE_NO_WINDOW);

        let output = cmd.output().map_err(|e| e.to_string())?;
        let stdout = String::from_utf8_lossy(&output.stdout).to_string();

        let mut current_iface = String::new();

        for line in stdout.lines() {
            if !line.starts_with(' ') && line.ends_with(':') {
                current_iface = line.trim_end_matches(':').to_string();
                if let Some(pos) = current_iface.find("adapter ") {
                    current_iface = current_iface[(pos + 8)..].to_string();
                }
            }

            let trimmed = line.trim();

            if let Some(ip_match) = Regex::new(r"IPv4.*?:\s*(\d+\.\d+\.\d+\.\d+)")
                .unwrap()
                .captures(trimmed)
            {
                let ip = ip_match[1].to_string();
                if ip.starts_with("127.") || ip.starts_with("169.254.") {
                    continue;
                }
                subnets.push(SubnetInfo {
                    ip,
                    subnet_mask: String::new(),
                    cidr: String::new(),
                    interface_name: current_iface.clone(),
                });
            }

            if let Some(mask_match) = Regex::new(r"Subnet Mask.*?:\s*(\d+\.\d+\.\d+\.\d+)")
                .unwrap()
                .captures(trimmed)
            {
                if let Some(last) = subnets.last_mut() {
                    if last.subnet_mask.is_empty() {
                        let mask = mask_match[1].to_string();
                        let prefix = subnet_mask_to_prefix(&mask);
                        let ip_parts: Vec<u32> = last
                            .ip
                            .split('.')
                            .filter_map(|p| p.parse().ok())
                            .collect();
                        let mask_parts: Vec<u32> =
                            mask.split('.').filter_map(|p| p.parse().ok()).collect();
                        if ip_parts.len() == 4 && mask_parts.len() == 4 {
                            let network = format!(
                                "{}.{}.{}.{}",
                                ip_parts[0] & mask_parts[0],
                                ip_parts[1] & mask_parts[1],
                                ip_parts[2] & mask_parts[2],
                                ip_parts[3] & mask_parts[3]
                            );
                            last.cidr = format!("{}/{}", network, prefix);
                        }
                        last.subnet_mask = mask;
                    }
                }
            }
        }
    }

    #[cfg(not(target_os = "windows"))]
    {
        if let Ok(output) = Command::new("ip").args(["addr", "show"]).output() {
            let stdout = String::from_utf8_lossy(&output.stdout).to_string();
            let iface_re = Regex::new(r"^\d+:\s+(\S+):").unwrap();
            let inet_re = Regex::new(r"inet (\d+\.\d+\.\d+\.\d+)/(\d+)").unwrap();

            let mut current_iface = String::new();
            for line in stdout.lines() {
                if let Some(cap) = iface_re.captures(line) {
                    current_iface = cap[1].to_string();
                }
                if let Some(cap) = inet_re.captures(line) {
                    let ip = cap[1].to_string();
                    let prefix: u8 = cap[2].parse().unwrap_or(24);
                    if ip.starts_with("127.") {
                        continue;
                    }
                    let mask_u32: u32 = if prefix == 0 {
                        0
                    } else {
                        !0u32 << (32 - prefix)
                    };
                    let mask = format!(
                        "{}.{}.{}.{}",
                        (mask_u32 >> 24) & 0xFF,
                        (mask_u32 >> 16) & 0xFF,
                        (mask_u32 >> 8) & 0xFF,
                        mask_u32 & 0xFF
                    );
                    let ip_parts: Vec<u32> =
                        ip.split('.').filter_map(|p| p.parse().ok()).collect();
                    let network = format!(
                        "{}.{}.{}.{}",
                        ip_parts[0] & ((mask_u32 >> 24) & 0xFF),
                        ip_parts[1] & ((mask_u32 >> 16) & 0xFF),
                        ip_parts[2] & ((mask_u32 >> 8) & 0xFF),
                        ip_parts[3] & (mask_u32 & 0xFF)
                    );
                    subnets.push(SubnetInfo {
                        ip,
                        subnet_mask: mask,
                        cidr: format!("{}/{}", network, prefix),
                        interface_name: current_iface.clone(),
                    });
                }
            }
        }
    }

    subnets.retain(|s| !s.subnet_mask.is_empty());
    Ok(subnets)
}

#[tauri::command]
pub async fn discover_network(
    app_handle: tauri::AppHandle,
    subnet_ip: String,
    subnet_mask: String,
    scan_depth: String,
) -> Result<Vec<DiscoveredDevice>, String> {
    let scan_ips = generate_scan_ips(&subnet_ip, &subnet_mask);
    if scan_ips.is_empty() {
        return Err("Could not generate IP range from subnet. The subnet may be too large (max /20) or invalid.".to_string());
    }

    let total = scan_ips.len() as u32;
    let mut live_ips: Vec<String> = Vec::new();

    // Phase 1: Ping sweep
    let _ = app_handle.emit(
        "discovery-progress",
        DiscoveryProgress {
            phase: "ping_sweep".to_string(),
            current: 0,
            total,
            found_so_far: 0,
            message: format!("Scanning {} addresses...", total),
        },
    );

    let batch_size = 30;
    for (batch_idx, chunk) in scan_ips.chunks(batch_size).enumerate() {
        let mut handles = Vec::new();
        for ip in chunk {
            let ip_clone = ip.clone();
            handles.push(tokio::task::spawn_blocking(move || {
                let alive = ping_single(&ip_clone);
                (ip_clone, alive)
            }));
        }

        for handle in handles {
            if let Ok((ip, alive)) = handle.await {
                if alive {
                    live_ips.push(ip);
                }
            }
        }

        let scanned = ((batch_idx + 1) * batch_size).min(total as usize) as u32;
        let _ = app_handle.emit(
            "discovery-progress",
            DiscoveryProgress {
                phase: "ping_sweep".to_string(),
                current: scanned,
                total,
                found_so_far: live_ips.len() as u32,
                message: format!(
                    "Pinged {}/{} — found {} devices",
                    scanned, total, live_ips.len()
                ),
            },
        );
    }

    if live_ips.is_empty() {
        return Ok(vec![]);
    }

    let found_count = live_ips.len() as u32;

    let mut devices: Vec<DiscoveredDevice> = live_ips
        .iter()
        .map(|ip| DiscoveredDevice {
            ip: ip.clone(),
            hostname: String::new(),
            mac_address: String::new(),
            vendor: String::new(),
            open_ports: vec![],
        })
        .collect();

    // Phase 2: ARP + Vendor + Hostname (for "basic" and "ports" depth)
    if scan_depth == "basic" || scan_depth == "ports" {
        let _ = app_handle.emit(
            "discovery-progress",
            DiscoveryProgress {
                phase: "arp_lookup".to_string(),
                current: 0,
                total: found_count,
                found_so_far: found_count,
                message: "Reading ARP table...".to_string(),
            },
        );

        let arp_table = tokio::task::spawn_blocking(read_arp_table)
            .await
            .unwrap_or_default();

        for device in &mut devices {
            if let Some(mac) = arp_table.get(&device.ip) {
                device.mac_address = mac.clone();
            }
        }

        // Load OUI table from bundled CSV and resolve vendors
        let oui_table = load_oui_table(&app_handle);
        for device in &mut devices {
            if !device.mac_address.is_empty() {
                device.vendor = lookup_mac_vendor(&device.mac_address, &oui_table);
            }
        }

        // Hostname resolution (batched)
        let _ = app_handle.emit(
            "discovery-progress",
            DiscoveryProgress {
                phase: "hostname_resolution".to_string(),
                current: 0,
                total: found_count,
                found_so_far: found_count,
                message: "Resolving hostnames...".to_string(),
            },
        );

        let hostname_batch_size = 10;
        for (batch_idx, chunk) in devices.chunks_mut(hostname_batch_size).enumerate() {
            let ips: Vec<String> = chunk.iter().map(|d| d.ip.clone()).collect();
            let mut handles = Vec::new();

            for ip in ips {
                handles.push(tokio::task::spawn_blocking(move || {
                    let hostname = resolve_hostname(&ip);
                    (ip, hostname)
                }));
            }

            let mut results: HashMap<String, String> = HashMap::new();
            for handle in handles {
                if let Ok((ip, hostname)) = handle.await {
                    results.insert(ip, hostname);
                }
            }

            for device in chunk.iter_mut() {
                if let Some(hostname) = results.get(&device.ip) {
                    device.hostname = hostname.clone();
                }
            }

            let resolved =
                ((batch_idx + 1) * hostname_batch_size).min(found_count as usize) as u32;
            let _ = app_handle.emit(
                "discovery-progress",
                DiscoveryProgress {
                    phase: "hostname_resolution".to_string(),
                    current: resolved,
                    total: found_count,
                    found_so_far: found_count,
                    message: format!("Resolved {}/{} hostnames", resolved, found_count),
                },
            );
        }
    }

    // Phase 3: Port scan (for "ports" depth only)
    if scan_depth == "ports" {
        let ports_to_check: Vec<u16> = vec![80, 443, 3389, 22, 631, 9100, 5353, 8080];
        let port_total = (found_count as usize * ports_to_check.len()) as u32;

        let _ = app_handle.emit(
            "discovery-progress",
            DiscoveryProgress {
                phase: "port_scan".to_string(),
                current: 0,
                total: port_total,
                found_so_far: found_count,
                message: "Scanning ports...".to_string(),
            },
        );

        let port_batch_size = 20;
        let mut all_port_tasks: Vec<(usize, String, u16)> = Vec::new();
        for (idx, device) in devices.iter().enumerate() {
            for &port in &ports_to_check {
                all_port_tasks.push((idx, device.ip.clone(), port));
            }
        }

        for (batch_idx, chunk) in all_port_tasks.chunks(port_batch_size).enumerate() {
            let mut handles = Vec::new();
            for (idx, ip, port) in chunk {
                let ip_clone = ip.clone();
                let port_val = *port;
                let device_idx = *idx;
                handles.push(tokio::task::spawn_blocking(move || {
                    let open = check_port(&ip_clone, port_val);
                    (device_idx, port_val, open)
                }));
            }

            for handle in handles {
                if let Ok((device_idx, port, open)) = handle.await {
                    if open {
                        devices[device_idx].open_ports.push(port);
                    }
                }
            }

            let checked =
                ((batch_idx + 1) * port_batch_size).min(all_port_tasks.len()) as u32;
            let _ = app_handle.emit(
                "discovery-progress",
                DiscoveryProgress {
                    phase: "port_scan".to_string(),
                    current: checked,
                    total: port_total,
                    found_so_far: found_count,
                    message: format!("Checked {}/{} port combinations", checked, port_total),
                },
            );
        }

        for device in &mut devices {
            device.open_ports.sort();
            device.open_ports.dedup();
        }
    }

    // Sort by IP
    devices.sort_by(|a, b| {
        let parse_ip = |ip: &str| -> u32 {
            ip.split('.')
                .filter_map(|p| p.parse::<u32>().ok())
                .enumerate()
                .fold(0u32, |acc, (i, p)| acc | (p << (24 - i * 8)))
        };
        parse_ip(&a.ip).cmp(&parse_ip(&b.ip))
    });

    let _ = app_handle.emit(
        "discovery-progress",
        DiscoveryProgress {
            phase: "complete".to_string(),
            current: found_count,
            total: found_count,
            found_so_far: found_count,
            message: format!("Discovery complete — found {} devices", found_count),
        },
    );

    Ok(devices)
}
