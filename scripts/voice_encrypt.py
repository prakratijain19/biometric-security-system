import io
import os
import numpy as np
import soundfile as sf
import librosa
from cryptography.fernet import Fernet
from dtw import dtw

###########################
# WAV Audio Processing (Backend)
###########################


def read_wav_bytes(audio_bytes):
    """Read WAV bytes and return audio data and sample rate."""
    try:
        audio_data, sr = sf.read(io.BytesIO(audio_bytes))
        if audio_data.ndim > 1:
            audio_data = audio_data.mean(axis=1)  # Convert to mono
        return audio_data.astype(np.float32), sr
    except Exception as e:
        print(f"[ERROR] Could not read WAV bytes: {e}")
        raise


def extract_mfcc(audio, sr=16000, n_mfcc=13):
    """Extract MFCC features from audio."""
    try:
        mfcc = librosa.feature.mfcc(y=audio, sr=sr, n_mfcc=n_mfcc)
        # Normalization is crucial for consistent feature comparison
        mfcc = (mfcc - np.mean(mfcc)) / (np.std(mfcc) + 1e-6)
        return mfcc
    except Exception as e:
        print(f"[ERROR] MFCC extraction failed: {e}")
        raise


def numpy_to_bytes(arr):
    """Convert a NumPy array to bytes."""
    bio = io.BytesIO()
    np.save(bio, arr, allow_pickle=False)
    bio.seek(0)
    return bio.read()


def bytes_to_numpy(b):
    """Convert bytes back to a NumPy array."""
    bio = io.BytesIO(b)
    bio.seek(0)
    return np.load(bio, allow_pickle=False)


###########################
# Encryption Utilities
###########################

def generate_key():
    return Fernet.generate_key()


def save_key(path, key):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'wb') as f:
        f.write(key)


def load_key(path):
    with open(path, 'rb') as f:
        return f.read()


def encrypt_bytes(data, key):
    f = Fernet(key)
    return f.encrypt(data)


def decrypt_bytes(token, key):
    f = Fernet(key)
    return f.decrypt(token)


def save_encrypted(path, token):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'wb') as f:
        f.write(token)


def load_encrypted(path):
    with open(path, 'rb') as f:
        return f.read()


# ---------- Voice Register & Verify ----------

def register_voice_from_wav_bytes(audio_bytes, out_enc_path, key_path, n_mfcc=13):
    """Register voice from uploaded WAV bytes."""
    try:
        audio, sr = read_wav_bytes(audio_bytes)
        print(
            f"[DEBUG] Registration audio shape: {audio.shape}, sample rate: {sr}")
        if audio is None or audio.size == 0:
            print("[ERROR] Audio is empty during registration.")
            return False
        mfcc = extract_mfcc(audio, sr, n_mfcc)
        print(
            f"[DEBUG] Registration MFCC shape: {mfcc.shape}, mean: {np.mean(mfcc):.4f}, std: {np.std(mfcc):.4f}")
        if mfcc is None or mfcc.size == 0:
            print("[ERROR] MFCC extraction failed or empty.")
            return False
        key = generate_key()
        token = encrypt_bytes(numpy_to_bytes(mfcc), key)
        save_encrypted(out_enc_path, token)
        save_key(key_path, key)
        print("Voice registered successfully.")
        return True
    except Exception as e:
        print(f"[ERROR] Voice registration failed: {e}")
        return False


def verify_voice_from_wav_bytes(audio_bytes, enc_path, key_path, n_mfcc=13, threshold=100):
    """Verify voice from uploaded WAV bytes."""
    try:
        audio, sr = read_wav_bytes(audio_bytes)
        mfcc_new = extract_mfcc(audio, sr, n_mfcc)
        token = load_encrypted(enc_path)
        key = load_key(key_path)
        mfcc_saved = bytes_to_numpy(decrypt_bytes(token, key))
        alignment = dtw(mfcc_new.T, mfcc_saved.T,
                        dist_method=lambda x, y: np.linalg.norm(x - y))
        distance = alignment.distance
        print(f"DTW distance: {distance:.4f}")
        return distance < threshold, distance, threshold
    except Exception as e:
        print(f"[ERROR] Voice verification failed: {e}")
        return False, None, threshold
