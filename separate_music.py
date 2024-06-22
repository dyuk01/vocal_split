import os
import subprocess
import tkinter as tk
from tkinter import filedialog, messagebox
import librosa
import numpy as np
import soundfile as sf

# Function to classify vocal pitch
def classify_pitch(y, sr):
    pitches, magnitudes = librosa.core.piptrack(y=y, sr=sr)
    pitch = []

    for t in range(pitches.shape[1]):
        index = magnitudes[:, t].argmax()
        pitch_val = pitches[index, t]
        if pitch_val > 0:
            pitch.append((t, pitch_val))

    pitch = np.array(pitch)

    falsetto = pitch[pitch[:, 1] > 1000]
    true_voice = pitch[(pitch[:, 1] > 300) & (pitch[:, 1] <= 1000)]
    high_pitch = pitch[(pitch[:, 1] > 200) & (pitch[:, 1] <= 300)]
    low_pitch = pitch[pitch[:, 1] <= 200]

    return falsetto, true_voice, high_pitch, low_pitch

# Function to segment and save classified pitch
def save_segments(y, sr, segments, output_path, label):
    segment_length = int(sr * 0.1)  # 100ms segments
    for i, (t, _) in enumerate(segments):
        start_sample = int(t)
        end_sample = int(start_sample + segment_length)
        print(start_sample, end_sample)
        if start_sample < len(y) and end_sample <= len(y):
            segment = y[start_sample:end_sample]
            filename = os.path.join(output_path, f'{label}_segment_{i}.wav')
            sf.write(filename, segment, sr)
        else:
            print(f"Skipping segment {i} for {label}: start_sample {start_sample} or end_sample {end_sample} out of bounds.")

# Function to separate music and classify pitches
def separate_and_classify(input_file):
    if not input_file or not os.path.exists(input_file):
        print("Error: Please provide a valid input file.")
        return

    # Output folder path
    desktop_path = os.path.join(os.path.expanduser('~'), 'Desktop')
    output_folder = os.path.join(desktop_path, 'VocalSplit_Output')

    # Create output folder if it does not exist
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # Run Demucs to separate the music file using the specified model
    command = f"demucs -n mdx_extra_q --out {output_folder} {input_file}"
    result = subprocess.run(command, shell=True, executable='/bin/bash')

    # Check the result
    if result.returncode != 0:
        print(f"Error: An error occurred during the separation process for {input_file}.")
        return

    # Find the vocal track file
    vocal_path = None
    for root, dirs, files in os.walk(output_folder):
        for file in files:
            if 'vocals.wav' in file:
                vocal_path = os.path.join(root, file)
                break

    if not vocal_path:
        print("Error: Vocal track not found.")
        return

    # Load the separated vocal track
    y, sr = librosa.load(vocal_path, sr=None)
    falsetto, true_voice, high_pitch, low_pitch = classify_pitch(y, sr)

    # Save the classified segments
    if len(falsetto) > 0:
        save_segments(y, sr, falsetto, output_folder, 'falsetto')
    if len(true_voice) > 0:
        save_segments(y, sr, true_voice, output_folder, 'true_voice')
    if len(high_pitch) > 0:
        save_segments(y, sr, high_pitch, output_folder, 'high_pitch')
    if len(low_pitch) > 0:
        save_segments(y, sr, low_pitch, output_folder, 'low_pitch')

    print(f"Separation and classification complete for {input_file}. Check the {output_folder} folder for results.")

# Function to process all MP3 files in a directory
def process_directory(directory):
    if not os.path.exists(directory):
        print(f"Error: Directory {directory} does not exist.")
        return

    # Find all mp3 files in the directory
    mp3_files = [os.path.join(directory, f) for f in os.listdir(directory) if f.endswith('.mp3')]

    if not mp3_files:
        print(f"No MP3 files found in directory {directory}.")
        return

    for mp3_file in mp3_files:
        separate_and_classify(mp3_file)

# Function to select directory
def select_directory():
    directory = filedialog.askdirectory(title="Select Directory with MP3 Files")
    if directory:
        process_directory(directory)

# Create the main window
root = tk.Tk()
root.title("Music Separator")

# Create and place the widgets
tk.Button(root, text="Select Directory", command=select_directory).pack(padx=20, pady=20)

# Run the application
root.mainloop()