import socket
import threading
import time

class Tello(object):
    """
    Wrapper class to interact with the Tello drone.
    Communication with Tello is handled by TelloManager.
    """
    def __init__(self, local_ip, local_port, imperial=False, 
                 command_timeout=0.3, 
                 tello_ip='192.168.10.1',
                 tello_port=8889):
        """
        Binds to the local IP/port and puts the Tello into command mode.

        :param local_ip: Local IP address to bind.
        :param local_port: Local port to bind.
        :param imperial: If True, speed is MPH and distance is feet. 
                         If False, speed is KPH and distance is meters.
        :param command_timeout: Number of seconds to wait for a response to a command.
        :param tello_ip: Tello IP.
        :param tello_port: Tello port.
        """
        self.abort_flag = False
        self.command_timeout = command_timeout
        self.imperial = imperial
        self.response = None
        self.last_height = 0

        # Create a UDP socket
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.tello_address = (tello_ip, tello_port)

        # If local_port is 8889 (used by Tello), override to 0 (OS picks an ephemeral port)
        if local_port == 8889:
            local_port = 0
        self.socket.bind((local_ip, local_port))

        # Thread for receiving command acknowledgments
        self.receive_thread = threading.Thread(target=self._receive_thread)
        self.receive_thread.daemon = True
        self.receive_thread.start()

        # Send initial "command" to enter SDK mode
        self.socket.sendto(b'command', self.tello_address)
        print('sent: command')

    def __del__(self):
        """
        Closes the local socket.
        """
        self.socket.close()

    def _receive_thread(self):
        """
        Listens to responses from the Tello.
        Runs as a thread, sets self.response to whatever the Tello last returned.
        """
        while True:
            try:
                self.response, _ = self.socket.recvfrom(3000)
            except socket.error as exc:
                print(f'Caught exception socket.error : {exc}')

    def send_command(self, command):
        """
        Sends a command to the Tello and waits for a response.
        """
        print(f'>> send cmd: {command}')
        self.abort_flag = False
        timer = threading.Timer(self.command_timeout, self.set_abort_flag)

        # Send command
        self.socket.sendto(command.encode('utf-8'), self.tello_address)

        # Start timer, wait for response
        timer.start()
        while self.response is None:
            if self.abort_flag:
                break
        timer.cancel()
        
        # Interpret response
        if self.response is None:
            response = 'none_response'
        else:
            response = self.response.decode('utf-8')

        self.response = None
        return response
    
    def set_abort_flag(self):
        """
        Sets self.abort_flag to True if the command times out.
        """
        self.abort_flag = True

    # ---------------------------
    # Basic Drone Control Methods
    # ---------------------------

    def takeoff(self):
        """Initiates take-off."""
        return self.send_command('takeoff')

    def land(self):
        """Initiates landing."""
        return self.send_command('land')

    def set_speed(self, speed):
        """
        Sets speed in either KPH (if imperial=False) or MPH (if imperial=True).
        """
        speed = float(speed)
        if self.imperial:
            speed = int(round(speed * 44.704))  # mph -> cm/s
        else:
            speed = int(round(speed * 27.7778)) # kph -> cm/s
        return self.send_command(f'speed {speed}')

    def rotate_cw(self, degrees):
        """Rotates clockwise by 'degrees'."""
        return self.send_command(f'cw {degrees}')

    def rotate_ccw(self, degrees):
        """Rotates counter-clockwise by 'degrees'."""
        return self.send_command(f'ccw {degrees}')

    def flip(self, direction):
        """Flips in the given direction ('l', 'r', 'f', 'b')."""
        return self.send_command(f'flip {direction}')

    # ---------------------------
    # Movement Methods
    # ---------------------------

    def move(self, direction, distance):
        """
        Generic move method. direction is one of 'up', 'down', 'left', 'right', 'forward', 'back'.
        Distance is in meters (if imperial=False) or feet (if imperial=True), 
        and is converted to centimeters before sending to the Tello.
        """
        distance = float(distance)
        if self.imperial:
            # feet -> centimeters
            distance = int(round(distance * 30.48))
        else:
            # meters -> centimeters
            distance = int(round(distance * 100))
        return self.send_command(f'{direction} {distance}')

    def move_forward(self, distance):
        """Moves forward by 'distance' (meters or feet)."""
        return self.move('forward', distance)

    def move_backward(self, distance):
        """Moves backward by 'distance' (meters or feet)."""
        return self.move('back', distance)

    def move_left(self, distance):
        """Moves left by 'distance' (meters or feet)."""
        return self.move('left', distance)

    def move_right(self, distance):
        """Moves right by 'distance' (meters or feet)."""
        return self.move('right', distance)

    def move_up(self, distance):
        """Moves up by 'distance' (meters or feet)."""
        return self.move('up', distance)

    def move_down(self, distance):
        """Moves down by 'distance' (meters or feet)."""
        return self.move('down', distance)

    # ---------------------------
    # Query Methods
    # ---------------------------

    def get_response(self):
        """Returns the most recent raw response from Tello."""
        return self.response

    def get_height(self):
        """
        Queries the Tello for its current height (in dm).
        Converts the result to an integer or reuses the last known height on failure.
        """
        height = self.send_command('height?')
        height_str = ''.join(filter(str.isdigit, str(height)))
        try:
            height_val = int(height_str)
            self.last_height = height_val
        except:
            height_val = self.last_height
        return height_val

    def get_battery(self):
        """Returns percent battery life remaining."""
        battery = self.send_command('battery?')
        try:
            battery = int(battery)
        except:
            pass
        return battery

    def get_flight_time(self):
        """Returns the number of seconds elapsed during flight."""
        flight_time = self.send_command('time?')
        try:
            flight_time = int(flight_time)
        except:
            pass
        return flight_time

    def get_speed(self):
        """Returns the current speed in KPH or MPH."""
        speed = self.send_command('speed?')
        try:
            speed_val = float(speed)
            if self.imperial:
                # Convert cm/s -> mph
                speed_val = round(speed_val / 44.704, 1)
            else:
                # Convert cm/s -> kph
                speed_val = round(speed_val / 27.7778, 1)
            return speed_val
        except:
            return speed  # fallback (string)
