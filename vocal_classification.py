import os
import librosa
import soundfile as sf
import numpy as np
from pathlib import Path
import scipy.io.wavfile as wavfile

def segment_audio(file_path, segment_duration):
    y, sr = librosa.load(file_path, sr=None)
    segment_length = int(segment_duration * sr)
    total_length = len(y)
    num_segments = total_length // segment_length
    remainder = total_length % segment_length

    file_path = Path(file_path)
    output_dir = file_path.parent / (file_path.stem + "_segments")
    output_dir.mkdir(parents=True, exist_ok=True)

    for i in range(num_segments):
        start = i * segment_length
        end = start + segment_length
        segment = y[start:end]
        segment_filename = output_dir / f"{file_path.stem}_segment_{i+1}.wav"
        sf.write(segment_filename, segment, sr)
 
    if remainder != 0:
        start = num_segments * segment_length
        segment = y[start:]
        segment_filename = output_dir / f"{file_path.stem}_segment_{num_segments+1}.wav"
        sf.write(segment_filename, segment, sr)
    
    print(f"Segments saved in {output_dir}")

def delete_silent_files(directory_path, silence_threshold=0.001):
    for file_path in Path(directory_path).glob("*.wav"):
        y, sr = librosa.load(file_path, sr=None)
        if np.max(np.abs(y)) < silence_threshold:
            os.remove(file_path)
            print(f"Deleted silent file: {file_path}")

def get_frequency(file_path):
    sample_rate, data = wavfile.read(file_path)

    if len(data.shape) > 1:
        data = data[:, 0]

    n = len(data)
    frequencies = np.fft.fftfreq(n, 1/sample_rate)
    fft_values = np.fft.fft(data)

    amplitude = np.abs(fft_values)

    dominant_frequency = np.argmax(amplitude[:n // 2])
    dominant_frequency_in_hz = frequencies[dominant_frequency]

    print(f'The dominant frequency is {dominant_frequency_in_hz} Hz') 

    return dominant_frequency_in_hz

def categorize_frequency(frequency, gender):
    if gender == 'male':
        if frequency > 350:
            return 'falsetto'
        elif 180 < frequency <= 350:
            return 'high_pitch'
        elif 85 < frequency <= 180:
            return 'true_voice'
        elif frequency <= 85:
            return 'low_pitch'
        else:
            return 'unknown'
    else:
        if frequency > 1000:
            return 'falsetto'
        elif 500 < frequency <= 1000:
            return 'high_pitch'
        elif 255 < frequency <= 500:
            return 'true_voice'
        elif 165 < frequency <= 255:
            return 'low_pitch'
        else:
            return 'unknown'
        
def classify_and_rename_segments(segment_dir, gender, song_name):
    classification_counters = {
        'falsetto': 1,
        'true_voice': 1,
        'high_pitch': 1,
        'low_pitch': 1,
        'unknown': 1
    }
    
    for file_path in Path(segment_dir).glob("*.wav"):
        dominant_frequency = get_frequency(file_path)
        category = categorize_frequency(dominant_frequency, gender)
        gender_abbr = 'm' if gender == 'male' else 'f'
        
        new_filename = f"{gender_abbr}_{category}_{song_name}_{classification_counters[category]}.wav"
        
        new_directory = Path(f"vocal/classification/{category}")
        new_directory.mkdir(parents=True, exist_ok=True)
        
        new_file_path = new_directory / new_filename
        os.rename(file_path, new_file_path)
        print(f"Renamed {file_path} to {new_file_path}")
        
        classification_counters[category] += 1

def run(directory_path, segment_duration, gender):
    root_dir = Path(directory_path)
    for song_dir in root_dir.iterdir():
        if song_dir.is_dir():
            vocals_file = song_dir / "vocals.wav"
            if vocals_file.exists():
                song_name = song_dir.name
                segment_audio(vocals_file, segment_duration)
                delete_silent_files(vocals_file.parent / (vocals_file.stem + "_segments"))
                classify_and_rename_segments(vocals_file.parent / (vocals_file.stem + "_segments"), gender, song_name)

# Run the script
run("vocal/audio/mdx_extra_q", 1, 'male')  # Change 'male' to 'female' for female gender