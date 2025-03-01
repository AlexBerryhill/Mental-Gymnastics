from datetime import datetime

class Stats:
    """
    A class to track statistics for a drone command and response cycle.
    """

    def __init__(self, command, drone_id):
        """
        Initializes a Stats object.

        :param command: The command string sent to the drone.
        :param drone_id: An identifier for the drone (e.g., an integer or name).
        """
        self.command = command
        self.response = None
        self.id = drone_id

        self.start_time = datetime.now()
        self.end_time = None
        self.duration = None
        self.drone_ip = None

    def add_response(self, response, ip):
        """
        Records the drone's response and updates end_time, duration, and IP address.

        :param response: The response string from the drone.
        :param ip: The IP address of the responding drone.
        """
        if self.response is None:
            self.response = response
            self.end_time = datetime.now()
            self.duration = self.get_duration()
            self.drone_ip = ip

    def get_duration(self):
        """
        Calculates how many seconds passed between the start and end times.

        :return: The duration in seconds (float).
        """
        if self.end_time is None:
            return 0
        diff = self.end_time - self.start_time
        return diff.total_seconds()

    def print_stats(self):
        """
        Prints the statistics in dictionary form.
        """
        print(self.get_stats())

    def got_response(self):
        """
        Checks whether a response has been recorded.

        :return: True if a response is recorded; otherwise, False.
        """
        return self.response is not None

    def get_stats(self):
        """
        Returns the statistics as a dictionary.

        :return: A dictionary containing command, response, timing, etc.
        """
        return {
            'id': self.id,
            'command': self.command,
            'response': self.response,
            'start_time': self.start_time,
            'end_time': self.end_time,
            'duration': self.duration
        }

    def get_stats_delimited(self):
        """
        Returns the statistics as a comma-delimited string.

        :return: A string with keys and values for easy logging.
        """
        stats = self.get_stats()
        keys = ['id', 'command', 'response', 'start_time', 'end_time', 'duration']
        vals = [f'{k}={stats[k]}' for k in keys]
        return ', '.join(vals)

    def __repr__(self):
        """
        Defines the string representation of the Stats object.

        :return: A comma-delimited string of stats.
        """
        return self.get_stats_delimited()
