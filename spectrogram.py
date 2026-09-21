"""
Audio Spectrogram Waterfall Plotter
==================================
Pure Python implementation using only pip-installable packages:
- numpy (numerical computing)
- matplotlib.pyplot (visualization)
- scipy.io.wavfile (audio file I/O)
- scipy.signal (STFT computation)

Run this file directly. It will prompt for an audio file path and display a waterfall plot.
"""

import numpy as np
from matplotlib import pyplot as plt
from scipy.io import wavfile
from scipy.signal import stft, get_window, resample

def plot_waterfall(audio_path: str):
    sr, data = wavfile.read(audio_path)
    
    if data.dtype == np.int16:
        data = data.astype(np.float32) / 32768.0
    elif data.dtype == np.float32 or data.dtype == np.float64:
        pass
    else:
        raise ValueError(f"Unsupported audio dtype: {data.dtype}")
        
    if len(data.shape) > 1:
        data = data.mean(axis=1)
    
    # Resample to 48 kHz for consistent bin width
    if sr != 48000:
        data = resample(data, int(len(data) * 48000 / sr))
        sr = 48000
        
    nperseg = 8192
    hop_length = int(sr * 0.01)   # 10 ms interval
    noverlap = nperseg - hop_length
    
    window = get_window('blackmanharris', nperseg)
    
    f, t, Zxx = stft(data, fs=sr, nperseg=nperseg, noverlap=noverlap, nfft=nperseg,
                     window=window, boundary='zeros', padded=True)
    
    spec = np.abs(Zxx) ** 2
    
    plt.figure(figsize=(14, 6))
    
    # Use pcolormesh for dynamic mapping to support logarithmic scaling
    plt.pcolormesh(f, t, spec.T, cmap='magma', shading='auto')
    plt.xscale('log')
    plt.xlim(20, f[-1])
    
    plt.xlabel('Frequency (Hz)')
    plt.ylabel('Time (s)')
    plt.title(f'Spectrogram Waterfall : {audio_path}')
    plt.colorbar(label='Magnitude squared')
    plt.tight_layout()
    return plt.gcf()

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2:
        print("Usage: python spectrogram_waterfall.py <path_to_audio.wav>")
        sys.exit(1)
        
    audio_file = sys.argv[1]
    plot_waterfall(audio_file)
    plt.show()