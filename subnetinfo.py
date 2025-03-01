from netaddr import IPNetwork
import itertools

class SubnetInfo:
    """
    Subnet information.
    """

    def __init__(self, ip, network, netmask):
        """
        Constructor.
        :param ip: IP address of the local interface.
        :param network: Network portion of the subnet.
        :param netmask: Subnet mask.
        """
        self.ip = ip
        self.network = network
        self.netmask = netmask

    def __repr__(self):
        return f'{self.network} | {self.netmask} | {self.ip}'

    def get_ips(self):
        """
        Gets all possible IP addresses in the subnet, excluding
        addresses ending with .0 and .255, and excluding the IP
        that matches self.ip.

        :return: List of IP strings.
        """
        def get_quad(ip_address):
            """
            Extracts the last octet from an IP string.
            :param ip_address: IP address string.
            :return: The last octet (e.g., '100' in '192.168.1.100').
            """
            quads = str(ip_address).split('.')
            return quads[3]
        
        def is_valid(ip_address):
            """
            Checks if an IP address is valid for usage in scanning.
            Specifically excludes .0, .255, and self.ip.
            :param ip_address: IP address string.
            :return: Boolean indicating if IP is valid.
            """
            quad = get_quad(ip_address)
            result = (quad not in ['0', '255'])
            if result and str(ip_address) == self.ip:
                result = False
            return result

        ip_network = IPNetwork(f'{self.network}/{self.netmask}')

        return [str(ip_address) for ip_address in ip_network if is_valid(ip_address)]

    @staticmethod
    def flatten(infos):
        """
        Flattens a list of lists into a single list.
        :param infos: List of lists of IP addresses.
        :return: A single list containing all IP addresses.
        """
        return list(itertools.chain.from_iterable(infos))
 