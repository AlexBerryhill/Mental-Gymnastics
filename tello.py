class Tello(object):
    """
    A wrapper class to interact with Tello.
    Communication with Tello is handled by TelloManager.
    """
    def __init__(self, tello_ip, tello_manager):
        """
        Ctor.
        :param tello_ip: Tello IP.
        :param tello_manager: Tello Manager.
        """
        self.tello_ip = tello_ip
        self.tello_manager = tello_manager

    def send_command(self, command):
        """
        Sends a command.
        :param command: Command.
        :return: None.
        """
        return self.tello_manager.send_command(command, self.tello_ip)

    def __repr__(self):
        return f'TELLO@{self.tello_ip}'