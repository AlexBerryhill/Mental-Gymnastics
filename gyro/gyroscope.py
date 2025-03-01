from eeg_helpers import resolve_stream
from pylsl import StreamInlet
import time
import numpy as np


# Constants
ALPHA = 0.98  # Complementary filter coefficient (higher = trust gyro more)
DT = 0.1  # Time step in seconds (adjust based on your data rate)
MOVEMENT_THRESHOLD = 15  # Minimum angle change to detect movement

# Resolve gyroscope and accelerometer streams
gyro_stream = resolve_stream('type', 'Gyroscope')
accel_stream = resolve_stream('type', 'Accelerometer')

gyro_inlet = StreamInlet(gyro_stream[0])
accel_inlet = StreamInlet(accel_stream[0])

# Initialize angles
angle_x, angle_y, angle_z = 0.0, 0.0, 0.0  # Roll, Pitch, Yaw

# Get initial accelerometer readings for a baseline
accel_sample, _ = accel_inlet.pull_sample()
ax, ay, az = accel_sample

# Convert accelerometer data to initial angles
angle_x = np.arctan2(ay, az) * (180 / np.pi)
angle_y = np.arctan2(ax, np.sqrt(ay**2 + az**2)) * (180 / np.pi)

print("Starting angles: X (Roll):", angle_x, "Y (Pitch):", angle_y, "Z (Yaw):", angle_z)

previous_angle_x = angle_x  # Store initial angle for comparison
previous_angle_z = angle_z  # Store initial yaw angle for movement detection
try:
    while True:
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
        #     print("\rMove down!                                                             \n", end = "")
        if angle_change_z < (-MOVEMENT_THRESHOLD*1):
            print("\rTurning Right!                                                           \n", end = "")

        if angle_change_z > (MOVEMENT_THRESHOLD*1):
            print("\rTurning left!                                                            \n", end = "")
        # if angle_change > (MOVEMENT_THRESHOLD / 1.1):
        #     print("\rTurn Left!                                                                \n", end = "")
        # elif angle_change < -MOVEMENT_THRESHOLD:
        #     print("\rMoved up!                                                                 \n", end = "")

        previous_angle_x = angle_x  # Update previous angle
        previous_angle_z = angle_z

        print(f"\rAngle X (Roll): {angle_x:.2f}, Angle Y (Pitch): {angle_y:.2f}, Angle Z (Yaw): {angle_z:.2f}",end = "")

except KeyboardInterrupt:
    print("\rExited by user.                                                                      \n")

   
