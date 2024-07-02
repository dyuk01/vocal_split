import os
import librosa
import soundfile as sf
import numpy as np
from pathlib import Path

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

def process_directory(directory_path, segment_duration):
    audio_files = [f for f in os.listdir(directory_path) if f.endswith('.wav')]
    for audio_file in audio_files:
        file_path = Path(directory_path) / audio_file
        segment_audio(file_path, segment_duration)
        delete_silent_files(file_path.parent / (file_path.stem + "_segments"))

# Example usage
process_directory("vocal/", 1)