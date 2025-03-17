import socket

def get_ip_by_prefix(prefix="10.0.1."):
    hostname = socket.gethostname()
    addresses = socket.getaddrinfo(hostname, None, socket.AF_INET)

    for addr in addresses:
        ip_address = addr[4][0]
        if ip_address.startswith(prefix):
            return ip_address
    return None  # Return None if no matching IP is found

ip_address = get_ip_by_prefix("10.0.1.")
print("IP Address:", ip_address if ip_address else "No matching IP found.")
