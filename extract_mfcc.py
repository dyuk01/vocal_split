import os
import librosa
import numpy as np

def extract_features(audio_file):
    y, sr = librosa.load(audio_file, sr=None)
    mfccs = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13)
    chroma = librosa.feature.chroma_stft(y=y, sr=sr)
    mel = librosa.feature.melspectrogram(y=y, sr=sr)
    contrast = librosa.feature.spectral_contrast(y=y, sr=sr)
    tonnetz = librosa.feature.tonnetz(y=librosa.effects.harmonic(y), sr=sr)
    features = np.concatenate((np.mean(mfccs, axis=1), np.mean(chroma, axis=1), np.mean(mel, axis=1), np.mean(contrast, axis=1), np.mean(tonnetz, axis=1)))
    return features

# Example of extracting features from all combined segments
output_folder = os.path.join(os.path.expanduser('~'), 'Desktop', 'VocalSplit_Output')
for label in ['falsetto', 'true_voice', 'high_pitch', 'low_pitch']:
    label_folder = os.path.join(output_folder, label)
    feature_list = []
    for audio_file in os.listdir(label_folder):
        if audio_file.endswith('.wav'):
            file_path = os.path.join(label_folder, audio_file)
            features = extract_features(file_path)
            feature_list.append(features)
    np.save(os.path.join(output_folder, f'{label}_features.npy'), feature_list)