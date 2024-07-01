import librosa
from pathlib import Path
import soundfile as sf
import psola
import numpy as np
import scipy.signal as sig

# Function to correct pitch to the nearest note in C minor scale
def correct(f0):
    if np.isnan(f0):
        return np.nan
    c_minor_degrees = librosa.key_to_degrees('C:min')  # Get degrees of C minor scale
    c_minor_degrees = np.concatenate((c_minor_degrees, [c_minor_degrees[0] + 12]))  # Extend scale by one octave

    midi_note = librosa.hz_to_midi(f0) 
    degree = midi_note % 12  # Get the pitch class
    closest_degree_id = np.argmin(np.abs(c_minor_degrees - degree))  # Find closest scale degree

    degree_difference = degree - c_minor_degrees[closest_degree_id]
    midi_note -= degree_difference  # Correct the MIDI note to the closest degree

    return librosa.midi_to_hz(midi_note)

# Function to correct an array of pitches
def correct_pitch(f0):
    corrected_f0 = np.array([correct(f) for f in f0])
    smoothed_corrected_f0 = sig.medfilt(corrected_f0, kernel_size=11)  # Apply median filter for smoothing
    
    smoothed_corrected_f0[np.isnan(smoothed_corrected_f0)] = corrected_f0[np.isnan(smoothed_corrected_f0)]  # Handle NaNs
    return smoothed_corrected_f0

# Function to apply auto-tune
def autotune(y, sr):
    # Track pitch
    frame_length = 2048
    hop_length = frame_length // 4
    fmin = librosa.note_to_hz('C2')
    fmax = librosa.note_to_hz('C7')
    
    # Estimate pitch using pyin
    f0, _, _ = librosa.pyin(y, frame_length=frame_length, hop_length=hop_length, sr=sr, fmin=fmin, fmax=fmax)
    
    # Correct the pitch
    corrected_f0 = correct_pitch(f0)

    # Apply pitch shifting using PSOLA
    return psola.vocode(y, sample_rate=int(sr), target_pitch=corrected_f0, fmin=fmin, fmax=fmax)

# Main function to load audio, process, and save output
def main():
    y, sr = librosa.load("vocals.wav", sr=None, mono=False)
    
    # Process first channel if stereo
    if y.ndim > 1:
        y = y[0, :]
    
    pitch_corrected_y = autotune(y, sr)
    
    filepath = Path("vocals.wav")
    output_filepath = filepath.parent / (filepath.stem + "_pitch_corrected" + filepath.suffix)
    sf.write(str(output_filepath), pitch_corrected_y, sr)

if __name__ == '__main__':
    main()