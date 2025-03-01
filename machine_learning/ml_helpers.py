from scipy.signal import welch
from scipy.stats import entropy
import numpy as np

def extract_features(eeg_window, fs):
    """
    Extracts features from a 256-sample window for each EEG channel.

    @param[in] eeg_window: (256, 5) array containing EEG data.
    @param[in] fs: Sampling frequency.
    @return Feature vector concatenated across all channels.
    """
    features = []
    
    for i in range(5):  # Loop through the 5 EEG sensor channels
        channel = eeg_window[:, i]        

        freqs, psd = welch(channel, fs=fs, nperseg=min(len(channel), fs))
        if np.sum(psd) == 0:
            psd = np.ones_like(psd)  # Prevent divide-by-zero

        power_features = [np.sum(psd[(freqs >= low) & (freqs < high)]) for low, high in [(0.5, 4), (4, 8), (8, 13), (13, 30)]]
        spectral_entropy = entropy(psd / np.sum(psd))

        channel_features = [
            np.mean(channel), np.std(channel), np.var(channel),
            *power_features, spectral_entropy
        ]
        features.extend(channel_features)

    # Replace NaN values with 0
    features = np.nan_to_num(features)

    return features