# Description: This script is used to test the ability to control two Tello drones at the same time.
# It has not been completed yet, but the single functinality is feature complete

from ESP_32_Controller.lib.ESPTelloCLI.ESPSwarm.swarm import TelloSwarm
import time
import serial

swarm = TelloSwarm.fromSerialSSID([
    ["COM18", "TELLO-303331"],
    ["COM19", "TELLO-D231E0"]
])

swarm.connect()
swarm.get_battery()
swarm.takeoff()
swarm.rotate_clockwise(90)
time.sleep(1)
swarm.rotate_counter_clockwise(180)
time.sleep(1)
swarm.rotate_clockwise(90)
time.sleep(1)
swarm.land()