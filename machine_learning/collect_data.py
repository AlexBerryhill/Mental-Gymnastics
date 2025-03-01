import numpy as np
import pandas as pd
from pylsl import StreamInlet, resolve_streams, resolve_byprop
from eeg_helpers import resolve_stream
import time
from tqdm import tqdm


# Settings
CLASS_LABELS = {0: "Left", 1: "Right", 2: "Open"}  # Update with real classes
SAMPLE_DURATION = 30  # Duration to collect per class (seconds)
FS = 256  # Sampling rate (adjust based on your EEG device)

# Resolve EEG stream
print("Looking for EEG stream...")
streams = resolve_stream('type', 'EEG')
inlet = StreamInlet(streams[0])

data = []

def collect_data(label, duration):
    print(f"Collecting data for: {CLASS_LABELS[label]}")
    start_time = time.time()
    with tqdm(total=duration, desc=f"Recording {CLASS_LABELS[label]}", unit="s") as pbar:
        while time.time() - start_time < duration:
            sample, timestamp = inlet.pull_sample()
            data.append(sample + [label])  # Append EEG values with class label
            elapsed_time = time.time() - start_time
            pbar.update(int(elapsed_time - pbar.n))

for class_id in CLASS_LABELS:
    input(f"\nPress Enter to record {CLASS_LABELS[class_id]}...")
    collect_data(class_id, SAMPLE_DURATION)

# Save to CSV
df = pd.DataFrame(data)
df.to_csv("data/eeg_data.csv", index=False)
print("Data collection complete! Saved as eeg_data.csv.")
