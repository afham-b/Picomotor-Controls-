import ipaddress

def calculate_broadcast_address(ip: str, mask: str) -> str:
    # Create an IPv4Network object using the given IP and subnet mask
    network = ipaddress.IPv4Network(f"{ip}/{mask}", strict=False)
    # Return the broadcast address
    return str(network.broadcast_address)

# Example usage
ip_address = '169.254.103.211'
subnet_mask = '255.255.0.0'

broadcast_address = calculate_broadcast_address(ip_address, subnet_mask)
print(f"The broadcast address for IP {ip_address} with subnet mask {subnet_mask} is: {broadcast_address}")
