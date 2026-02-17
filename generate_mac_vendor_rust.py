import csv
from collections import defaultdict
import os

def generate_mac_vendor_rust_code(csv_file_path="oui.csv", output_dir="tauri-app/src-tauri/src/commands/"):
    """
    Generates Rust code for MAC address vendor lookup from an OUI CSV file.
    """

    vendor_name_mapping = {
        "APPLE": "Apple",
        "APPLE, INC.": "Apple",
        "SAMSUNG ELECTRONICS CO.,LTD": "Samsung",
        "GOOGLE, INC.": "Google",
        "GOOGLE": "Google",
        "AMAZON TECHNOLOGIES INC.": "Amazon",
        "AMAZON": "Amazon",
        "INTEL CORPORATION": "Intel",
        "INTEL": "Intel",
        "TP-LINK TECHNOLOGIES CO.,LTD.": "TP-Link",
        "TP-LINK": "TP-Link",
        "NETGEAR": "Netgear",
        "ASUSTEK COMPUTER INC.": "Asus",
        "ASUS": "Asus",
        "UBIQUITI NETWORKS": "Ubiquiti",
        "UBIQUITI INC.": "Ubiquiti",
        "CISCO SYSTEMS, INC.": "Cisco",
        "CISCO": "Cisco",
        "HEWLETT PACKARD": "HP",
        "HEWLETT PACKARD ENTERPRISE": "HP",
        "HP INC.": "HP",
        "HP": "HP",
        "DELL INC.": "Dell",
        "DELL": "Dell",
        "MICROSOFT CORPORATION": "Microsoft",
        "MICROSOFT": "Microsoft",
        "ROKU, INC.": "Roku",
        "ROKU": "Roku",
        "SONOS, INC.": "Sonos",
        "SONOS": "Sonos",
        "RASPBERRY PI (TRADING) LTD": "Raspberry Pi",
        "RASPBERRY PI FOUNDATION": "Raspberry Pi",
        "ESPRESSIF SYSTEMS (SHANGHAI) CO., LTD.": "Espressif",
        "ESPRESSIF SYSTEMS": "Espressif",
        "D-LINK CORPORATION": "D-Link",
        "D-LINK": "D-Link",
        "REALTEK SEMICONDUCTOR CORP.": "Realtek",
        "REALTEK": "Realtek",
        "BROADCOM CORPORATION": "Broadcom",
        "BROADCOM": "Broadcom",
        "HUAWEI TECHNOLOGIES CO.,LTD": "Huawei",
        "HUAWEI": "Huawei",
        "LG ELECTRONICS INC.": "LG",
        "LG": "LG",
        "SONY CORPORATION": "Sony",
        "SONY": "Sony",
        "RING LLC": "Ring", # Added Ring based on the previous file
    }

    raw_oui_data = []
    try:
        with open(csv_file_path, mode='r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                # Assuming 'Assignment' is the OUI and 'Organization Name' is the vendor
                assignment = row.get('Assignment')
                organization_name = row.get('Organization Name')

                if assignment and organization_name:
                    # Format to XX:XX:XX and uppercase
                    oui = assignment.replace('-', ':').upper()
                    raw_oui_data.append({'oui': oui, 'organization': organization_name.strip().upper()})
    except FileNotFoundError:
        print(f"Error: The file '{csv_file_path}' was not found.")
        return
    except Exception as e:
        print(f"Error reading CSV file: {e}")
        return

    # Group OUIs by normalized vendor
    grouped_ouis = defaultdict(list)
    for item in raw_oui_data:
        original_org = item['organization']
        # Use existing mapping for known vendors, otherwise use the original organization name
        normalized_org = vendor_name_mapping.get(original_org, original_org)
        grouped_ouis[normalized_org].append(item['oui'])

    # Sort OUIs within each group for consistent output
    for vendor, ouis in grouped_ouis.items():
        grouped_ouis[vendor] = sorted(list(set(ouis))) # Use set to remove duplicates

    # Generate Rust code
    rust_code_lines = []
    rust_code_lines.append("pub fn lookup_mac_vendor(prefix: &str) -> &str {")
    rust_code_lines.append("    match prefix {")

    # Get all unique normalized vendors and sort them for consistent output
    all_vendors = sorted(grouped_ouis.keys())

    for vendor_name in all_vendors:
        ouis = grouped_ouis[vendor_name]
        if ouis:
            # Join all OUIs for the current vendor into a single line
            # Each OUI needs to be quoted and separated by " | "
            # Example: "000000" | "000001" | "000002"
            formatted_ouis = ' | '.join([f'"{oui}"' for oui in ouis])
            formatted_vendor_name = vendor_name.replace('"', '\\"')
            rust_code_lines.append(f"        {formatted_ouis} => r#\"{formatted_vendor_name}\"#,")

    rust_code_lines.append("        _ => \"Unknown\",")
    rust_code_lines.append("    }")
    rust_code_lines.append("}")

    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)
    output_filename = os.path.join(output_dir, "mac_vendor_lookup.rs")
    try:
        with open(output_filename, 'w', encoding='utf-8') as outfile:
            outfile.write("\n".join(rust_code_lines))
        print(f"Generated Rust code written to {output_filename}")
    except Exception as e:
        print(f"Error writing Rust code to file: {e}")

if __name__ == "__main__":
    # Ensure oui.csv is in the same directory as this script, or provide the full path
    generate_mac_vendor_rust_code()
