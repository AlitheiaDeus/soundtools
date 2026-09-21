# Sound Tools (`soundtools`)

Audio digital signal processing (DSP), real-time STFT computation, and waterfall spectrogram visualizers in Python.

---

## Tools

### 1. `waterfall.py` — Real-Time Live Waterfall Spectrogram
An interactive real-time audio waterfall visualizer reading from your microphone/input device via **PyAudio** and computing FFT bins with **Librosa** and **NumPy**.
- **Interactive UI**: Includes live Matplotlib sliders for lower/upper dB thresholds, speed, and gain scale factors.
- **Scale Modes**: Supports linear, logarithmic (dB), and musical scaling.
- **Rolling Buffer**: Smooth multi-line waterfall animation history.

### 2. `spectrogram.py` — File-Based Waterfall Plotter
A lightweight, pure-Python script that prompts for an audio file path (`.wav`) and generates a static waterfall spectrogram.
- Automatically handles mono/stereo averaging and resamples to 48 kHz.
- Uses **Blackman-Harris** windowed Short-Time Fourier Transform (STFT) via `scipy.signal`.

### 3. `converter_pro.py` — Multithreaded/Multiprocess FLAC to MP3 Converter
A high-throughput batch converter from `.flac` to 320 kbps `.mp3` with tag preservation.
- Scans current directory for `.flac` files and skips existing converted tracks.
- Uses `pydub.utils.mediainfo` to preserve metadata tags (Title, Artist, Album, Track).
- Converts songs in parallel across all CPU cores via `ProcessPoolExecutor`.
- Displays real-time progress using `tqdm`.

---

## Requirements

```bash
pip install numpy matplotlib scipy pyaudio librosa pydub tqdm
```
*(On Windows, ensure `ffmpeg` is installed or on your PATH for `pydub` conversions).*
