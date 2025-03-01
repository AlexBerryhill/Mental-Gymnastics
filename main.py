import numpy as np
import joblib
from pylsl import StreamInlet
from machine_learning.eeg_helpers import resolve_stream
from machine_learning.ml_helpers import extract_features
from gyro.gyroscope import right_left_command
# from ui import telloFlip_l, telloFlip_r

# Load trained model & scaler
clf = joblib.load("model/svm_model.pkl")
scaler = joblib.load("model/scaler.pkl")

# Constants
FS = 256
WINDOW_SIZE = FS  # 1 second of EEG data

# Resolve EEG stream
print("Looking for an EEG stream...")
streams = resolve_stream('type', 'EEG')
inlet = StreamInlet(streams[0])

print("EEG stream connected.")

buffer = []  # Stores 256 samples
count_0 = 0
count_1 = 0
    

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
        sample, timestamp = inlet.pull_sample()
        
        right_left_command(gyro_inlet, accel_inlet, angle_x, angle_y, angle_z, previous_angle_x, previous_angle_z)

        if sample:
            buffer.append(sample)  # Collect EEG sample

            if len(buffer) >= WINDOW_SIZE:
                eeg_window = np.array(buffer[-WINDOW_SIZE:])  # Take last 256 samples
                feature_vector = extract_features(eeg_window, FS)
                features_scaled = scaler.transform([feature_vector])

                prediction = clf.predict(features_scaled)
                print(f"\rPredicted Class: {prediction[0]}", end="")

                # IF the model is sure about the prediction flip the drone
                if prediction[0] == 0:
                    count_0 += 1
                    count_1 = 0  # Reset count for the other class
                elif prediction[0] == 1:
                    count_1 += 1
                    count_0 = 0  # Reset count for the other class
                else:
                    count_0 = 0
                    count_1 = 0

                if count_0 == 200:
                    print("\nTriggering flip left...")
                    # telloFlip_l()
                    count_0 = 0  # Reset count after triggering

                if count_1 == 200:
                    print("\nTriggering flip right...")
                    # telloFlip_r()
                    count_1 = 0  # Reset count after triggering

                buffer.pop(0)  # Remove oldest sample (sliding window)
except KeyboardInterrupt:
    print("Closing EEG stream...")
