from machine_learning.eeg_helpers import resolve_stream
from pylsl import StreamInlet
import time
import numpy as np
from tello import Tello

# Constants
ALPHA = 0.98  # Complementary filter coefficient (higher = trust gyro more)
DT = 0.1  # Time step in seconds (adjust based on your data rate)
MOVEMENT_THRESHOLD = 5  # Minimum angle change to detect movement

# Create an instance of the Tello class
tello = Tello(local_ip='0.0.0.0', local_port=9000)
last_descision = 'none'
cumulative_angle = 0

def right_left_command(gyro_inlet, accel_inlet,angle_x, angle_y, angle_z, previous_angle_x, previous_angle_z):
    global last_descision, cumulative_angle
    # Get gyroscope and accelerometer readings
    gyro_sample, _ = gyro_inlet.pull_sample()
    accel_sample, _ = accel_inlet.pull_sample()

    gx, gy, gz = gyro_sample  # Gyroscope readings (deg/s)
    ax, ay, az = accel_sample  # Accelerometer readings

    # Integrate gyro readings to estimate angles
    angle_x += gx * DT
    angle_y += gy * DT
    angle_z += gz * DT  # Yaw (left/right turning)

    # Compute accelerometer-based angles
    accel_angle_x = np.arctan2(ay, az) * (180 / np.pi)
    accel_angle_y = np.arctan2(ax, np.sqrt(ay**2 + az**2)) * (180 / np.pi)

    # Apply complementary filter
    angle_x = ALPHA * (angle_x) + (1 - ALPHA) * accel_angle_x
    angle_y = ALPHA * (angle_y) + (1 - ALPHA) * accel_angle_y

    # Compare with previous angle to determine movement
    angle_change = angle_x - previous_angle_x
    angle_change_z = angle_z - previous_angle_z

    # if angle_change > MOVEMENT_THRESHOLD:
    #     print("\rMove down!  
    #                                                            \n", end = "")

    if last_descision == 'right' and angle_change_z >= (-MOVEMENT_THRESHOLD * 0.5):
        print("\rTurning Right!                                                           \n", end = "")
        tello.rotate_cw(abs(int(cumulative_angle)))  # Rotate clockwise
        cumulative_angle = 0
        last_descision = 'none'
    elif last_descision == 'left' and angle_change_z <= (MOVEMENT_THRESHOLD * 0.5):
        print("\rTurning left!                                                            \n", end = "")
        tello.rotate_ccw(abs(int(cumulative_angle)))  # Rotate counter-clockwise
        cumulative_angle = 0
        last_descision = 'none'

    if angle_change_z < (-MOVEMENT_THRESHOLD * 0.5):
        cumulative_angle += angle_change_z
        last_descision = 'right'
    elif angle_change_z > (MOVEMENT_THRESHOLD * 0.5):
        cumulative_angle += angle_change_z
        last_descision = 'left'

    # if angle_change > (MOVEMENT_THRESHOLD / 1.1):
    #     print("\rTurn Left!                                                                \n", end = "")
    # elif angle_change < -MOVEMENT_THRESHOLD:
    #     print("\rMoved up!                                                                 \n", end = "")

    previous_angle_x = angle_x  # Update previous angle
    previous_angle_z = angle_z

    # print(f"\rAngle X (Roll): {angle_x:.2f}, Angle Y (Pitch): {angle_y:.2f}, Angle Z (Yaw): {angle_z:.2f}",end = "")

                                                                  

   
