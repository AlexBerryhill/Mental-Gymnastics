import socket
import threading
import time
from collections import defaultdict
import netifaces
import netaddr

from stats import Stats        # Assuming Stats is defined in stats.py
from subnetinfo import SubnetInfo  # Assuming SubnetInfo is defined in subnetinfo.py
from tello import Tello       # Assuming Tello is defined in tello.py

class TelloManager:
    """
    Tello Manager.
    """
    def __init__(self):
        """
        Constructor.
        """
        self.local_ip = ''
        # Instead of a fixed port, use an ephemeral port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.bind((self.local_ip, 0))  # OS assigns an available port

        # thread for receiving command acknowledgments
        self.receive_thread = threading.Thread(target=self._receive_thread)
        self.receive_thread.daemon = True
        self.receive_thread.start()

        self.tello_ip_list = []
        self.tello_list = []
        self.log = defaultdict(list)
        self.COMMAND_TIME_OUT = 20.0
        self.last_response_index = {}
        self.str_cmd_index = {}

    # ... rest of your TelloManager code remains unchanged ...
