# Vocal Split

A python-based program that takes an mp3 file and turns it into 4 seperate audio files consisted of bass, melody, drum, and vocal.

## Description

This is a Python script that uses `demucs` to separate vocals and instrumental tracks from an input MP3 file. The script provides a simple GUI for selecting the input file and specifying the output folder.

## Getting Started

### Dependencies

- Python 3.8+
- `demucs`
- `tkinter` (usually included with Python)

### Installation

1. **Install Python**

   Ensure you have Python 3.8 or later installed. You can download it from [python.org](https://www.python.org/downloads/).

2. **Install Demucs**

   Install `demucs` using `pip`. It's recommended to do this in a virtual environment to avoid conflicts with other packages.

    ```bash
    # Open a terminal
    # Create and activate a virtual environment (optional but recommended)
    python -m venv demucs-env
    source demucs-env/bin/activate  # On Windows, use `demucs-env\Scripts\activate`

    # Install demucs
    pip install demucs
    ```
3. **Clone the Repository or Download the Script**
    ```bash
    git clone https://github.com/dyuk01/vocal_split.git
    cd vocal_split
    ```
    Alternatively, you can directly download the music_separator.py file.

### Executing program

1. **Open a Terminal**
Open a terminal and navigate to the directory containing music_separator.py.

2. **Activate the Virtual Environment**
If you are using a virtual environment, ensure it is activated:
```bash
source demucs-env/bin/activate  # On Windows, use `demucs-env\Scripts\activate`
```

3. **Run the Script**
Run the script using Python:
```bash
python music_separator.py
```

## Authors
Name and contact info

Dokyung(Peter) Yuk
- [GitHub](https://github.com/dyuk01)
- [LinkedIn](https://www.linkedin.com/in/dokyung-yuk-a3aba3254/)
