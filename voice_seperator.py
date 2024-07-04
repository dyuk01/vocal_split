import subprocess
from pathlib import Path
from pydub import AudioSegment

def convert_mp3_to_wav(input_path, output_path):
    """Convert mp3 file to wav format."""
    audio = AudioSegment.from_mp3(input_path)
    audio.export(output_path, format="wav")

def separate_vocals(input_file, output_dir):
    """Separate vocals from the input file using Demucs."""
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    command = [
        "demucs",
        "-n", "mdx_extra_q",  # model name, you can choose different models here
        "-o", str(output_dir),
        str(input_file)
    ]

    subprocess.run(command)

def process_directory(input_dir, output_dir):
    """Process all mp3 files in the input directory."""
    input_dir = Path(input_dir)
    output_dir = Path(output_dir)

    for mp3_file in input_dir.glob("*.mp3"):
        print(f"Processing {mp3_file}...")

        # Convert MP3 to WAV
        wav_file = mp3_file.with_suffix('.wav')
        convert_mp3_to_wav(mp3_file, wav_file)

        # Separate vocals using Demucs
        separate_vocals(wav_file, output_dir)

        # Remove the temporary WAV file if desired
        wav_file.unlink()

        print(f"Finished processing {mp3_file}.")

# Example usage
input_dir = 'audio'
output_dir = 'vocal/audio'
process_directory(input_dir, output_dir)