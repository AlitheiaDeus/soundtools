import pyaudio
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.widgets import Slider, RadioButtons
import librosa

# --- Audio Parameters ---
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
CHUNK = 1024

# --- Waterfall Parameters ---
WINDOW_SIZE = 2048
HOP_LENGTH = WINDOW_SIZE // 4
N_FFT = WINDOW_SIZE
THRESHOLD_LOWER_DB = -80  # Initial value
THRESHOLD_UPPER_DB = 0    # Initial value
SCALE_FACTOR = 1.0
SPEED_FACTOR = 1.0
SCALE_TYPE = 'linear'
MAX_LINES = 50  # Number of history lines in the waterfall
FREQS = librosa.fft_frequencies(sr=RATE, n_fft=N_FFT)

# --- Initialize PyAudio ---
p = pyaudio.PyAudio()
stream = p.open(format=FORMAT,
                channels=CHANNELS,
                rate=RATE,
                input=True,
                frames_per_buffer=CHUNK)

# --- Initialize Plot ---
fig, ax = plt.subplots()
ax.set_ylim(THRESHOLD_LOWER_DB, THRESHOLD_UPPER_DB)
ax.set_xlim(0, RATE / 2)
ax.set_xlabel('Frequency (Hz)')
ax.set_ylabel('Amplitude (dB)')
ax.set_title('Live Waterfall Spectrogram')

# --- Initialize Data Buffer (Rolling Buffer) ---
data_buffer = np.zeros((MAX_LINES, len(FREQS)))

# --- Initialize Lines (Create Once, Update Later) ---
lines = []
for _ in range(MAX_LINES):
    l, = ax.plot(FREQS, np.zeros_like(FREQS), lw=1)  # Plot against FREQS
    lines.append(l)


# --- Scaling Function ---
def apply_scale(data, scale_factor, scale_type):
    if scale_type == 'linear':
        return data * scale_factor
    elif scale_type == 'logarithmic':
        return data + (20 * np.log10(scale_factor)) # dB scale
    elif scale_type == 'musical':
        return data * (2**(scale_factor))  # Probably not what's intended for dB
    else:
        return data  # Or raise an exception for invalid scale_type


# --- Update Function (Core Logic) ---
def update(frame):
    global data_buffer, THRESHOLD_LOWER_DB, THRESHOLD_UPPER_DB, SCALE_FACTOR, SPEED_FACTOR, CHUNK, SCALE_TYPE
    try:
        raw_data = stream.read(int(CHUNK * SPEED_FACTOR), exception_on_overflow=False)
        audio_data = np.frombuffer(raw_data, dtype=np.int16).astype(np.float32) / 32768.0
    except OSError as e:
        print(f"Error reading from stream: {e}")
        return lines  # Return existing lines without updating

    # Compute STFT and convert to dB
    spectrogram = librosa.stft(audio_data, n_fft=N_FFT, hop_length=HOP_LENGTH, window='hann')
    spectrogram_db = librosa.amplitude_to_db(np.abs(spectrogram), ref=np.max)

    # Get the first frame (column) of the spectrogram.  This is the *newest* data.
    if spectrogram_db.size > 0:
        new_data = spectrogram_db[:, 0]

        # Apply scaling and clipping
        new_data = apply_scale(new_data, SCALE_FACTOR, SCALE_TYPE)
        new_data = np.clip(new_data, THRESHOLD_LOWER_DB, THRESHOLD_UPPER_DB)

        # Update the rolling buffer: Shift data to the right, add new data at the beginning
        data_buffer = np.roll(data_buffer, 1, axis=0)
        data_buffer[0, :] = new_data

        # Update the lines
        for i, line in enumerate(lines):
            line.set_ydata(data_buffer[i, :])

    return lines
# --- Slider and Radio Button Axes ---
ax_lower = plt.axes([0.1, 0.01, 0.65, 0.03])
ax_upper = plt.axes([0.1, 0.05, 0.65, 0.03])
ax_scale = plt.axes([0.1, 0.09, 0.65, 0.03])
ax_speed = plt.axes([0.1, 0.13, 0.65, 0.03])
ax_radio = plt.axes([0.8, 0.01, 0.15, 0.15])

# --- Create Widgets ---
slider_lower = Slider(ax_lower, 'Lower Threshold (dB)', -100, 0, valinit=THRESHOLD_LOWER_DB)
slider_upper = Slider(ax_upper, 'Upper Threshold (dB)', -100, 0, valinit=THRESHOLD_UPPER_DB)
slider_scale = Slider(ax_scale, 'Scale Factor', 0.1, 10.0, valinit=SCALE_FACTOR)
slider_speed = Slider(ax_speed, 'Speed Factor', 0.1, 5.0, valinit=SPEED_FACTOR)
radio_scale = RadioButtons(ax_radio, ('linear', 'logarithmic', 'musical'), active=0)

# --- Callback Functions ---
def update_lower(val):
    global THRESHOLD_LOWER_DB
    THRESHOLD_LOWER_DB = val
    if THRESHOLD_LOWER_DB > THRESHOLD_UPPER_DB:
        slider_upper.set_val(THRESHOLD_LOWER_DB)
    ax.set_ylim(THRESHOLD_LOWER_DB, THRESHOLD_UPPER_DB)

def update_upper(val):
    global THRESHOLD_UPPER_DB
    THRESHOLD_UPPER_DB = val
    if THRESHOLD_UPPER_DB < THRESHOLD_LOWER_DB:
        slider_lower.set_val(THRESHOLD_UPPER_DB)
    ax.set_ylim(THRESHOLD_LOWER_DB, THRESHOLD_UPPER_DB)

def update_scale(val):
    global SCALE_FACTOR
    SCALE_FACTOR = val

def update_speed(val):
    global SPEED_FACTOR
    SPEED_FACTOR = val

def update_scale_type(label):
    global SCALE_TYPE
    SCALE_TYPE = label

# --- Connect Callbacks ---
slider_lower.on_changed(update_lower)
slider_upper.on_changed(update_upper)
slider_scale.on_changed(update_scale)
slider_speed.on_changed(update_speed)
radio_scale.on_clicked(update_scale_type)

# --- Animation ---
ani = animation.FuncAnimation(fig, update, blit=True, interval=30)  # blit=True for performance

plt.show()

# --- Clean Up ---
stream.stop_stream()
stream.close()
p.terminate()