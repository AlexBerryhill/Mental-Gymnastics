
import socket
import argparse
import sys

def get_socket() -> socket.socket:
    """
    Creates and returns a UDP socket bound to port 8889.
    
    Returns:
        socket.socket: A UDP socket bound to ('', 8889).
    """
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.bind(('', 8889))
    return s

def set_ap(ssid: str, password: str, address: tuple) -> None:
    """
    Sets the Tello drone to AP mode by sending the appropriate commands.
    
    Parameters:
        ssid (str): The SSID (name) of the Wi‑Fi network.
        password (str): The Wi‑Fi network password.
        address (tuple): A tuple of (Tello IP, Tello Port).
    """
    s = get_socket()

    # Step 1: Enter SDK command mode.
    cmd = "command"
    print(f"Sending command: {cmd}")
    s.sendto(cmd.encode('utf-8'), address)
    response, ip = s.recvfrom(1024)
    print(f"Received from {ip}: {response.decode('utf-8')}")
    
    # Step 2: Set the drone to AP mode with your SSID and password.
    cmd = f"ap {ssid} {password}"
    print(f"Sending command: {cmd}")
    s.sendto(cmd.encode('utf-8'), address)
    response, ip = s.recvfrom(1024)
    print(f"Received from {ip}: {response.decode('utf-8')}")

def parse_args(args: list) -> argparse.Namespace:
    """
    Parses command-line arguments.
    
    Parameters:
        args (list): List of command-line arguments.
        
    Returns:
        argparse.Namespace: Parsed command-line arguments.
    """
    parser = argparse.ArgumentParser(
        description="Set Tello Drone to AP Mode",
        epilog="Example: python set-ap-mode.py -s 'Walking BCD' -p 'Alexander'"
    )
    parser.add_argument('-s', '--ssid', help='SSID of the Wi‑Fi network', required=True)
    parser.add_argument('-p', '--pwd', help='Password of the Wi‑Fi network', required=True)
    parser.add_argument('--ip', help='Tello Drone IP address', default='192.168.10.1', required=False)
    parser.add_argument('--port', help='Tello Drone port', default=8889, type=int, required=False)
    parser.add_argument('--version', action='version', version='set-ap-mode.py v1.0')
    return parser.parse_args(args)

if __name__ == "__main__":
    args = parse_args(sys.argv[1:])
    ssid = args.ssid
    password = args.pwd
    tello_address = (args.ip, args.port)
    set_ap(ssid, password, tello_address)
