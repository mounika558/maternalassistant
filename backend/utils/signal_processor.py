"""
Signal Processor - Reads and processes .dat files
"""

import numpy as np
import wfdb
import os

def process_signal_file(filepath):
    """
    Process a .dat signal file and return the signal data
    
    Args:
        filepath: Path to the .dat file
        
    Returns:
        numpy array of signal data
    """
    try:
        # Get the base path without extension
        base_path = filepath.rsplit('.', 1)[0]
        
        # Check if .hea file exists
        hea_file = base_path + '.hea'
        if not os.path.exists(hea_file):
            # If .hea doesn't exist, try to read just the .dat file
            return read_dat_file_only(filepath)
        
        # Read using wfdb
        record = wfdb.rdrecord(base_path)
        
        # Get signal data
        signal_data = record.p_signal
        
        # If multiple channels, flatten or process as needed
        if len(signal_data.shape) > 1 and signal_data.shape[1] > 1:
            # For multiple channels, you might want to select specific channels
            # or process them differently based on your model
            signal_data = signal_data[:, 0]  # Take first channel for now
        
        return signal_data.flatten()
        
    except Exception as e:
        print(f"Error processing signal file: {e}")
        # Fallback to reading raw binary data
        return read_dat_file_only(filepath)

def read_dat_file_only(filepath):
    """
    Fallback method to read .dat file as raw binary data
    
    Args:
        filepath: Path to the .dat file
        
    Returns:
        numpy array of signal data
    """
    try:
        # Read as binary and convert to numpy array
        with open(filepath, 'rb') as f:
            data = np.fromfile(f, dtype=np.int16)
        
        # Normalize the data
        if len(data) > 0:
            data = (data - np.mean(data)) / (np.std(data) + 1e-8)
        
        return data
        
    except Exception as e:
        raise Exception(f"Failed to read .dat file: {e}")

def preprocess_signal(signal_data, target_length=None):
    """
    Preprocess signal data - normalize, filter, resample
    
    Args:
        signal_data: Raw signal data
        target_length: Target length for resampling (optional)
        
    Returns:
        Preprocessed signal data
    """
    # Remove NaN values
    signal_data = signal_data[~np.isnan(signal_data)]
    
    # Normalize
    signal_mean = np.mean(signal_data)
    signal_std = np.std(signal_data)
    if signal_std > 0:
        signal_data = (signal_data - signal_mean) / signal_std
    
    # Resample if target length is specified
    if target_length is not None and len(signal_data) != target_length:
        # Simple resampling using interpolation
        old_indices = np.linspace(0, len(signal_data) - 1, len(signal_data))
        new_indices = np.linspace(0, len(signal_data) - 1, target_length)
        signal_data = np.interp(new_indices, old_indices, signal_data)
    
    return signal_data

def segment_signal(signal_data, segment_length=1000, overlap=0.5):
    """
    Segment signal into overlapping windows
    
    Args:
        signal_data: Signal data array
        segment_length: Length of each segment
        overlap: Overlap ratio (0-1)
        
    Returns:
        List of signal segments
    """
    segments = []
    step = int(segment_length * (1 - overlap))
    
    for i in range(0, len(signal_data) - segment_length + 1, step):
        segment = signal_data[i:i + segment_length]
        segments.append(segment)
    
    return segments