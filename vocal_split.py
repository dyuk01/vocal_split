import os
import subprocess
import tkinter as tk
from tkinter import filedialog, messagebox

# Function to select input file
def select_input_file():
    input_file = filedialog.askopenfilename(title="Select Input Music File",
                                            filetypes=(("MP3 files", "*.mp3"), ("All files", "*.*")))
    if input_file:
        input_file_entry.delete(0, tk.END)
        input_file_entry.insert(0, input_file)

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
    if result.returncode == 0:
        messagebox.showinfo("Success", f'Separation complete. Check the {output_folder} folder for results.')
    else:
        messagebox.showerror("Error", "An error occurred during the separation process.")

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
