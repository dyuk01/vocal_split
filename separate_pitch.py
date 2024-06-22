import os
import subprocess
import tkinter as tk
from tkinter import filedialog, messagebox
import librosa
import numpy as np
import soundfile as sf

# Function to select input file
def select_input_file():
    input_file = filedialog.askopenfilename(title="Select Input Music File",
                                            filetypes=(("MP3 files", "*.mp3"), ("All files", "*.*")))
    if input_file:
        input_file_entry.delete(0, tk.END)
        input_file_entry.insert(0, input_file)

# Function to classify vocal pitch
def classify_pitch(y, sr):
    pitches, magnitudes = librosa.core.piptrack(y=y, sr=sr)
    pitch = []

    for t in range(pitches.shape[1]):
        index = magnitudes[:, t].argmax()
        pitch_val = pitches[index, t]
        if pitch_val > 0:
            pitch.append(pitch_val)

    pitch = np.array(pitch)

    falsetto = pitch[pitch > 1000]
    true_voice = pitch[(pitch > 300) & (pitch <= 1000)]
    high_pitch = pitch[(pitch > 200) & (pitch <= 300)]
    low_pitch = pitch[pitch <= 200]

    return falsetto, true_voice, high_pitch, low_pitch

# Function to save classified segments
def save_segments(segments, sr, output_path, label):
    for i, segment in enumerate(segments):
        filename = os.path.join(output_path, f'{label}_segment_{i}.wav')
        sf.write(filename, segment, sr)

# Function to separate music
def separate_music():
    input_file = input_file_entry.get()

    if not input_file:
        messagebox.showerror("Error", "Please select an input file.")
        return

    # Output folder path
    desktop_path = os.path.join(os.path.expanduser('~'), 'Desktop')
    output_folder = os.path.join(desktop_path, 'VocalSplit_Output')

    # Create output folder if it does not exist
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # Run Demucs to separate the music file using the specified model
    command = f"demucs --out {output_folder} {input_file}"
    result = subprocess.run(command, shell=True, executable='/bin/bash')

    # Check the result
    if result.returncode != 0:
        messagebox.showerror("Error", "An error occurred during the separation process.")
        return

    # Find the vocal track file
    vocal_path = None
    for root, dirs, files in os.walk(output_folder):
        for file in files:
            if 'vocals.wav' in file:
                vocal_path = os.path.join(root, file)
                break

    if not vocal_path:
        messagebox.showerror("Error", "Vocal track not found.")
        return

    # Load the separated vocal track
    y, sr = librosa.load(vocal_path, sr=None)
    falsetto, true_voice, high_pitch, low_pitch = classify_pitch(y, sr)

    # Save the classified segments
    save_segments(falsetto, sr, output_folder, 'falsetto')
    save_segments(true_voice, sr, output_folder, 'true_voice')
    save_segments(high_pitch, sr, output_folder, 'high_pitch')
    save_segments(low_pitch, sr, output_folder, 'low_pitch')

    messagebox.showinfo("Success", f'Separation complete. Check the {output_folder} folder for results.')

# Create the main window
root = tk.Tk()
root.title("Music Separator")

# Create and place the widgets
tk.Label(root, text="Input Music File:").grid(row=0, column=0, padx=10, pady=10, sticky=tk.W)
input_file_entry = tk.Entry(root, width=50)
input_file_entry.grid(row=0, column=1, padx=10, pady=10)
tk.Button(root, text="Browse", command=select_input_file).grid(row=0, column=2, padx=10, pady=10)

tk.Button(root, text="Separate Music", command=separate_music).grid(row=1, column=0, columnspan=3, pady=20)

# Run the application
root.mainloop()