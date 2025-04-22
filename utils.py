import socket

def get_ip_addresses():
    ip_addresses = []
    hostname = socket.gethostname()
    try:
        ip_address = socket.gethostbyname(hostname)
        ip_addresses.append(ip_address)
    except socket.gaierror:
        pass
    return ip_addresses