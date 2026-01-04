"""
Feature Extractor - Extracts features from EHG and CTG signals
"""

import numpy as np
from scipy import signal, stats
from scipy.fft import fft

def extract_ehg_features(signal_data):
    """
    Extract features from EHG (electrohysterogram) signal
    
    Features include:
    - Time domain: Mean, std, variance, RMS, peak-to-peak
    - Frequency domain: Spectral power in different bands
    - Statistical features: Skewness, kurtosis
    - Nonlinear features: Sample entropy
    
    Args:
        signal_data: EHG signal array
        
    Returns:
        List of extracted features
    """
    features = []
    
    # Time domain features
    features.append(np.mean(signal_data))  # Mean
    features.append(np.std(signal_data))   # Standard deviation
    features.append(np.var(signal_data))   # Variance
    features.append(np.sqrt(np.mean(signal_data**2)))  # RMS
    features.append(np.max(signal_data) - np.min(signal_data))  # Peak-to-peak
    features.append(np.median(signal_data))  # Median
    
    # Statistical features
    features.append(stats.skew(signal_data))  # Skewness
    features.append(stats.kurtosis(signal_data))  # Kurtosis
    
    # Frequency domain features
    fft_vals = np.abs(fft(signal_data))
    fft_freq = np.fft.fftfreq(len(signal_data))
    
    # Power in different frequency bands (EHG typically 0.2-4 Hz)
    low_freq_power = np.sum(fft_vals[(fft_freq >= 0.2) & (fft_freq < 0.5)])
    mid_freq_power = np.sum(fft_vals[(fft_freq >= 0.5) & (fft_freq < 1.0)])
    high_freq_power = np.sum(fft_vals[(fft_freq >= 1.0) & (fft_freq < 4.0)])
    
    features.append(low_freq_power)
    features.append(mid_freq_power)
    features.append(high_freq_power)
    
    # Dominant frequency
    dominant_freq_idx = np.argmax(fft_vals[1:len(fft_vals)//2]) + 1
    features.append(fft_freq[dominant_freq_idx])
    
    # Zero crossing rate
    zero_crossings = np.sum(np.diff(np.sign(signal_data)) != 0)
    features.append(zero_crossings / len(signal_data))
    
    # Energy
    features.append(np.sum(signal_data**2))
    
    # Autocorrelation features
    autocorr = np.correlate(signal_data, signal_data, mode='full')
    autocorr = autocorr[len(autocorr)//2:]
    features.append(autocorr[1] / autocorr[0] if autocorr[0] != 0 else 0)  # First autocorrelation
    
    # Sample entropy (simplified version)
    features.append(calculate_sample_entropy(signal_data))
    
    return features

def extract_ctg_features(signal_data):
    """
    Extract features from CTG (cardiotocography) signal
    
    Features typically include fetal heart rate (FHR) characteristics:
    - Baseline FHR
    - Variability measures
    - Acceleration/deceleration detection
    - Contraction patterns
    
    Args:
        signal_data: CTG signal array
        
    Returns:
        List of extracted features
    """
    features = []
    
    # Basic statistics
    features.append(np.mean(signal_data))  # Baseline FHR
    features.append(np.std(signal_data))   # Short-term variability
    features.append(np.var(signal_data))   # Variance
    
    # Calculate baseline (mode of the signal in normal FHR range)
    baseline = calculate_baseline_fhr(signal_data)
    features.append(baseline)
    
    # Variability measures
    # Short-term variability (beat-to-beat)
    if len(signal_data) > 1:
        short_term_var = np.mean(np.abs(np.diff(signal_data)))
        features.append(short_term_var)
    else:
        features.append(0)
    
    # Long-term variability (using rolling window)
    window_size = min(60, len(signal_data) // 10)
    if window_size > 1:
        rolling_std = []
        for i in range(len(signal_data) - window_size):
            rolling_std.append(np.std(signal_data[i:i+window_size]))
        long_term_var = np.mean(rolling_std) if rolling_std else 0
        features.append(long_term_var)
    else:
        features.append(0)
    
    # Acceleration detection (FHR increases > 15 bpm for > 15 seconds)
    accelerations = detect_accelerations(signal_data, baseline)
    features.append(accelerations)
    
    # Deceleration detection (FHR decreases)
    decelerations = detect_decelerations(signal_data, baseline)
    features.append(decelerations)
    
    # Peak-to-peak amplitude
    features.append(np.max(signal_data) - np.min(signal_data))
    
    # Frequency domain features
    fft_vals = np.abs(fft(signal_data))
    features.append(np.max(fft_vals))  # Maximum frequency component
    
    # Signal complexity
    features.append(calculate_sample_entropy(signal_data))
    
    # Percentage of time above/below baseline
    above_baseline = np.sum(signal_data > baseline) / len(signal_data)
    features.append(above_baseline)
    
    # Skewness and kurtosis
    features.append(stats.skew(signal_data))
    features.append(stats.kurtosis(signal_data))
    
    return features

def calculate_baseline_fhr(signal_data):
    """Calculate baseline fetal heart rate"""
    # Typically baseline is the mode in 110-160 bpm range
    # For processed signal, just use median of central tendency
    return np.median(signal_data)

def detect_accelerations(signal_data, baseline, threshold=15):
    """Detect number of accelerations in FHR"""
    accelerations = 0
    in_acceleration = False
    
    for val in signal_data:
        if val > baseline + threshold:
            if not in_acceleration:
                accelerations += 1
                in_acceleration = True
        else:
            in_acceleration = False
    
    return accelerations

def detect_decelerations(signal_data, baseline, threshold=15):
    """Detect number of decelerations in FHR"""
    decelerations = 0
    in_deceleration = False
    
    for val in signal_data:
        if val < baseline - threshold:
            if not in_deceleration:
                decelerations += 1
                in_deceleration = True
        else:
            in_deceleration = False
    
    return decelerations

def calculate_sample_entropy(signal_data, m=2, r=0.2):
    """
    Calculate sample entropy - measure of signal complexity
    
    Args:
        signal_data: Signal array
        m: Pattern length
        r: Tolerance (fraction of std)
        
    Returns:
        Sample entropy value
    """
    try:
        N = len(signal_data)
        if N < 10:
            return 0.0
        
        # Normalize
        signal_data = (signal_data - np.mean(signal_data)) / np.std(signal_data)
        
        r = r * np.std(signal_data)
        
        def _maxdist(xi, xj):
            return max([abs(ua - va) for ua, va in zip(xi, xj)])
        
        def _phi(m):
            x = [[signal_data[j] for j in range(i, i + m - 1 + 1)] 
                 for i in range(N - m + 1)]
            C = [len([1 for j in range(len(x)) if i != j and _maxdist(x[i], x[j]) <= r]) 
                 for i in range(len(x))]
            return sum(C)
        
        return -np.log(_phi(m+1) / _phi(m)) if _phi(m) > 0 and _phi(m+1) > 0 else 0.0
        
    except:
        return 0.0