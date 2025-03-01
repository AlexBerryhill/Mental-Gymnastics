import numpy as np
import pandas as pd
from scipy.signal import welch
from scipy.stats import entropy
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC
import joblib
from ml_helpers import extract_features

# Constants
FS = 256  # Sampling frequency
WINDOW_SIZE = FS  # 1 second of EEG data (256 samples)

# Load EEG dataset
df = pd.read_csv("data/eeg_data.csv")

# Convert raw data into 256-sample windows
X, y = [], []

for i in range(0, len(df) - WINDOW_SIZE, WINDOW_SIZE):  # Slide 256 samples per step
    eeg_window = df.iloc[i:i+WINDOW_SIZE, :5].values  # (256, 5) -> EEG Data
    label = df.iloc[i+WINDOW_SIZE-1, 5]  # Use the last sample's label

    X.append(extract_features(eeg_window, FS))
    y.append(label)

X = np.array(X)
y = np.array(y)

# Scale Features
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# Train Model
clf = SVC()
clf.fit(X_scaled, y)

# Save Model and Scaler
joblib.dump(scaler, 'model/scaler.pkl')
joblib.dump(clf, 'model/svm_model.pkl')

print("Training complete. Model saved.")
