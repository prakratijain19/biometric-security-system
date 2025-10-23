from cryptography.fernet import Fernet
import os
import numpy as np
from io import BytesIO

DEFAULT_KEY_PATH = "secret.key"


def generate_key(key_path: str = DEFAULT_KEY_PATH) -> bytes:
    key = Fernet.generate_key()
    with open(key_path, "wb") as f:
        f.write(key)
    return key


def load_key(key_path: str = DEFAULT_KEY_PATH) -> bytes:
    with open(key_path, "rb") as f:
        key = f.read()
    return key


def encrypt_npy_file(npy_path: str, key_path: str = DEFAULT_KEY_PATH, out_path: str = None) -> str:
    if out_path is None:
        out_path = npy_path+".enc"
    key = load_key(key_path)
    fernet = Fernet(key)

    with open(npy_path, "rb") as f:
        plain_bytes = f.read()

    encrypted_bytes = fernet.encrypt(plain_bytes)

    with open(out_path, "wb") as f:
        f.write(encrypted_bytes)

    return out_path


def decrypt_npy_file_to_npy(enc_path: str, key_path: str = DEFAULT_KEY_PATH, out_npy_path: str = None) -> str:
    if enc_path.endswith(".enc"):
        out_npy_path = enc_path[:-4]
    else:
        out_npy_path = enc_path + ".dec.npy"

    key = load_key(key_path)
    fernet = Fernet(key)

    with open(enc_path, "rb") as f:
        encrypted_bytes = f.read()

    plain_bytes = fernet.decrypt(encrypted_bytes)

    with open(out_npy_path, "wb") as f:
        f.write(plain_bytes)

    return out_npy_path


def decrypt_npy_file_to_array(enc_path: str, key_path: str = DEFAULT_KEY_PATH) -> np.ndarray:
    key = load_key(key_path)
    fernet = Fernet(key)

    with open(enc_path, "rb") as f:
        encrypted_bytes = f.read()
    plain_bytes = fernet.decrypt(encrypted_bytes)

    bio = BytesIO(plain_bytes)
    arr = np.load(bio, allow_pickle=False)
    return arr


if __name__ == "__main__":
    # Example usage
    key_file = "data/keys/secret.key"
    input_file = "data/face_encodings/user_face.npy"
    encrypted_file = input_file + ".enc"
    decrypted_file = input_file.replace(".npy", "_decrypted.npy")

    os.makedirs(os.path.dirname(key_file), exist_ok=True)

    if not os.path.exists(key_file):
        generate_key(key_file)
        print(f"Key generated and saved to {key_file}")

    encrypt_npy_file(input_file, key_file, encrypted_file)
    print(f"File encrypted and saved to {encrypted_file}")

    decrypt_npy_file_to_npy(encrypted_file, key_file, decrypted_file)
    print(f"File decrypted and saved to {decrypted_file}")
