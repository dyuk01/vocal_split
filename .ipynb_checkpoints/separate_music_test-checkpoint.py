import os
import subprocess
import tkinter as tk
from tkinter import filedialog
import librosa
import numpy as np
import soundfile as sf

def separate_vocals(input_file, output_folder):
    if not input_file or not os.path.exists(input_file):
        print("Error: Please provide a valid input file.")
        return False

    # Run Demucs to separate the music file using the specified model
    command = f"demucs -n mdx_extra_q --out {output_folder} {input_file}"
    result = subprocess.run(command, shell=True, executable='/bin/bash')

    # Check the result
    if result.returncode != 0:
        print(f"Error: An error occurred during the separation process for {input_file}.")
        return False

    return True

def find_vocal_track(output_folder):
    vocal_path = None
    for root, dirs, files in os.walk(output_folder):
        for file in files:
            if 'vocals.wav' in file:
                vocal_path = os.path.join(root, file)
                break
    return vocal_path

def divide_and_extract_mfcc(vocal_path, segment_length_sec=3):
    y, sr = librosa.load(vocal_path, sr=None)
    print(f"Loaded vocal track: {vocal_path}, sample rate: {sr}")

    # Ensure the vocal track is audible
    if len(y) == 0 or np.max(np.abs(y)) == 0:
        print("Error: Loaded vocal track is silent.")
        return None, None

    segment_length = int(sr * segment_length_sec)
    num_segments = len(y) // segment_length

    segments = []
    for i in range(num_segments):
        start_sample = i * segment_length
        end_sample = start_sample + segment_length
        segment = y[start_sample:end_sample]
        mfcc = librosa.feature.mfcc(y=segment, sr=sr, n_mfcc=13)
        segments.append((segment, mfcc, start_sample, end_sample))

    return segments, sr

def classify_segment_mfcc(mfcc, gender='male'):
    mean_mfcc = np.mean(mfcc, axis=1)
    # Example threshold-based classification (Adjust thresholds based on analysis)
    if gender == 'male':
        if np.mean(mean_mfcc) > 50:
            return 'falsetto'
        elif np.mean(mean_mfcc) > 30:
            return 'true_voice'
        elif np.mean(mean_mfcc) > 10:
            return 'high_pitch'
        else:
            return 'low_pitch'
    else:
        if np.mean(mean_mfcc) > 60:
            return 'falsetto'
        elif np.mean(mean_mfcc) > 40:
            return 'true_voice'
        elif np.mean(mean_mfcc) > 20:
            return 'high_pitch'
        else:
            return 'low_pitch'

def save_segment(y, sr, start_sample, end_sample, output_folder, label, index):
    label_folder = os.path.join(output_folder, label)
    os.makedirs(label_folder, exist_ok=True)

    segment = y[start_sample:end_sample]
    filename = os.path.join(label_folder, f'{label}_segment_{index}.wav')
    sf.write(filename, segment, sr)
    print(f"Saved segment {index} for {label}: start_sample {start_sample}, end_sample {end_sample}")

def process_file(input_file, gender='male'):
    desktop_path = os.path.join(os.path.expanduser('~'), 'Desktop')
    output_folder = os.path.join(desktop_path, 'VocalSplit_Output')

    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    if not separate_vocals(input_file, output_folder):
        return

    vocal_path = find_vocal_track(output_folder)
    if not vocal_path:
        print("Error: Vocal track not found.")
        return

    segments, sr = divide_and_extract_mfcc(vocal_path)
    if segments is None:
        return

    for i, (segment, mfcc, start_sample, end_sample) in enumerate(segments):
        label = classify_segment_mfcc(mfcc, gender)
        save_segment(segment, sr, start_sample, end_sample, output_folder, label, i)

    print(f"Processing complete for {input_file}. Check the {output_folder} folder for results.")

def process_directory(directory, gender='male'):
    if not os.path.exists(directory):
        print(f"Error: Directory {directory} does not exist.")
        return

    mp3_files = [os.path.join(directory, f) for f in os.listdir(directory) if f.endswith('.mp3')]
    if not mp3_files:
        print(f"No MP3 files found in directory {directory}.")
        return

    for mp3_file in mp3_files:
        process_file(mp3_file, gender)

def select_directory_and_gender():
    gender = tk.StringVar(value='male')

    def process_selection():
        directory = filedialog.askdirectory(title="Select Directory with MP3 Files")
        selected_gender = gender.get()
        if directory:
            process_directory(directory, selected_gender)

    gender_window = tk.Toplevel(root)
    gender_window.title("Select Gender")

    tk.Label(gender_window, text="Select Gender:").pack(padx=20, pady=5)
    tk.Radiobutton(gender_window, text="Male", variable=gender, value='male').pack(anchor=tk.W, padx=20)
    tk.Radiobutton(gender_window, text="Female", variable=gender, value='female').pack(anchor=tk.W, padx=20)
    tk.Button(gender_window, text="Select Directory", command=process_selection).pack(pady=20)

root = tk.Tk()
root.title("Music Separator")
tk.Button(root, text="Select Directory and Gender", command=select_directory_and_gender).pack(padx=20, pady=20)
root.mainloop()