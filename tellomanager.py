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
        self.local_port = 8889
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.bind((self.local_ip, self.local_port))

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

    def find_avaliable_tello(self, num):
        """
        Searches for 'num' Tello drones by sending 'command' to possible IP addresses.

        :param num: Number of Tello drones to find.
        :return: None
        """
        possible_ips = self.get_possible_ips()
        print(f'[SEARCHING] Searching for {num} from {len(possible_ips)} possible IP addresses')

        iters = 0

        while len(self.tello_ip_list) < num:
            print(f'[SEARCHING] Trying to find Tellos, number of tries = {iters + 1}')

            # Remove already found Tello IPs from the scan list
            for tello_ip in self.tello_ip_list:
                if tello_ip in possible_ips:
                    possible_ips.remove(tello_ip)

            # Send the 'command' to each possible IP
            for ip in possible_ips:
                cmd_id = len(self.log[ip])
                self.log[ip].append(Stats('command', cmd_id))
                try:
                    self.socket.sendto(b'command', (ip, 8889))
                except Exception as ex:
                    print(f'{iters}: ERROR sending to {ip}:8889 -> {ex}')
                    pass

            iters += 1
            time.sleep(5)

        # Filter out non-tello addresses in the log
        temp = defaultdict(list)
        for ip in self.tello_ip_list:
            temp[ip] = self.log[ip]
        self.log = temp

    def get_possible_ips(self):
        """
        Retrieves all possible IP addresses for subnets that the computer is a part of.
        Filters them to include only addresses starting with '192.168.3.'.

        :return: A list of IP addresses as strings.
        """
        infos = self.get_subnets()
        ips = SubnetInfo.flatten([info.get_ips() for info in infos])
        ips = list(filter(lambda ip: ip.startswith('192.168.2.'), ips))
        return ips

    def get_subnets(self):
        """
        Gets all subnet information for the system's network interfaces.

        :return: A list of SubnetInfo objects.
        """
        infos = []
        for iface in netifaces.interfaces():
            addrs = netifaces.ifaddresses(iface)
            if socket.AF_INET not in addrs:
                continue

            # Extract IPv4 info
            ipinfo = addrs[socket.AF_INET][0]
            address, netmask = ipinfo['addr'], ipinfo['netmask']

            # Only consider /24 subnets (255.255.255.0)
            if netmask != '255.255.255.0':
                continue

            # Create IPNetwork object
            cidr = netaddr.IPNetwork(f'{address}/{netmask}')
            network = cidr.network

            info = SubnetInfo(address, network, netmask)
            infos.append(info)

        return infos

    def get_tello_list(self):
        """
        Returns the list of Tello objects found.
        """
        return self.tello_list

    def send_command(self, command, ip):
        """
        Sends a command to a Tello at the specified IP address. Waits until a response is received or
        until the COMMAND_TIME_OUT is exceeded.

        :param command: The command to send (string).
        :param ip: The IP address of the target Tello.
        :return: None.
        """
        command_sof_1 = ord(command[0])
        command_sof_2 = ord(command[1])

        # Check if this is a "multi command" based on start-of-frame bytes
        if command_sof_1 == 0x52 and command_sof_2 == 0x65:
            multi_cmd_send_flag = True
        else:
            multi_cmd_send_flag = False

        if multi_cmd_send_flag:
            self.str_cmd_index[ip] = self.str_cmd_index[ip] + 1
            for num in range(1, 5):
                str_cmd_index_h = self.str_cmd_index[ip] / 128 + 1
                str_cmd_index_l = self.str_cmd_index[ip] % 128
                if str_cmd_index_l == 0:
                    str_cmd_index_l += 2
                cmd_sof = [0x52, 0x65, str_cmd_index_h, str_cmd_index_l, 0x01, num + 1, 0x20]
                cmd_sof_str = str(bytearray(cmd_sof))
                cmd = cmd_sof_str + command[3:]
                self.socket.sendto(cmd.encode('utf-8'), (ip, 8889))

            print(f'[MULTI_COMMAND], IP={ip}, COMMAND={command[3:]}')
            real_command = command[3:]
        else:
            self.socket.sendto(command.encode('utf-8'), (ip, 8889))
            print(f'[SINGLE_COMMAND] IP={ip}, COMMAND={command}')
            real_command = command

        # Log the command
        self.log[ip].append(Stats(real_command, len(self.log[ip])))

        start = time.time()
        # Wait for response
        while not self.log[ip][-1].got_response():
            now = time.time()
            diff = now - start
            if diff > self.COMMAND_TIME_OUT:
                print(f'[NO_RESPONSE] Max timeout exceeded for command: {real_command}')
                return

    def _receive_thread(self):
        """
        Listens to responses from the Tello drones on a separate thread.
        Updates self.response and the log accordingly.
        """
        while True:
            try:
                response, ip = self.socket.recvfrom(1024)
                response = response.decode('utf-8')
                self.response = response

                # ip is returned as a tuple (ip_string, port)
                ip_str = str(ip[0])

                # If we receive "OK" from a new IP, record it as a new Tello
                if response.upper() == 'OK' and ip_str not in self.tello_ip_list:
                    self.tello_ip_list.append(ip_str)
                    self.last_response_index[ip_str] = 100
                    self.tello_list.append(Tello(ip_str, self))
                    self.str_cmd_index[ip_str] = 1

                # Check for multi-response frames
                response_sof_part1 = ord(response[0])
                response_sof_part2 = ord(response[1])

                if response_sof_part1 == 0x52 and response_sof_part2 == 0x65:
                    response_index = ord(response[3])
                    if response_index != self.last_response_index[ip_str]:
                        print(f'[MULTI_RESPONSE], IP={ip_str}, RESPONSE={response[7:]}')
                        self.log[ip_str][-1].add_response(response[7:], ip_str)
                    self.last_response_index[ip_str] = response_index
                else:
                    # Single response
                    self.log[ip_str][-1].add_response(response, ip_str)

            except socket.error:
                # Ignore socket errors
                pass

    def get_log(self):
        """
        Returns the dictionary containing logs for each Tello IP.
        """
        return self.log

    def get_last_logs(self):
        """
        Returns the last log entry from each Tello's log list.
        """
        return [log[-1] for log in self.log.values()]
