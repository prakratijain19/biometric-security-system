from scripts import face_recognition_module as face_encrypt
import scripts.voice_encrypt as voice_encrypt
import os


def main():
    # --- File and Folder Paths ---
    keys_folder = os.path.join("data", "keys")
    voice_samples_folder = os.path.join("data", "voice_samples")
    face_encodings_folder = os.path.join(
        "data", "face_encodings")  # Path for face data

    os.makedirs(keys_folder, exist_ok=True)
    os.makedirs(voice_samples_folder, exist_ok=True)
    # Ensure face folder exists
    os.makedirs(face_encodings_folder, exist_ok=True)

    # Voice file paths
    encrypted_file = os.path.join(voice_samples_folder, "encrypted_voice.mfcc")
    wav_debug = os.path.join(voice_samples_folder, "last_record.wav")
    key_file = os.path.join(keys_folder, "voice_key.key")

    # Face file path (as defined in your face_recognition_module)
    face_encoding_file = os.path.join(face_encodings_folder, "user_face.npy")

    while True:
        print("\n=== Voice and Face Biometrics Cryptography ===")
        print("1. Register Face")
        print("2. Register Voice")
        print("3. Verify Face")
        print("4. Verify Voice")
        print("5. Exit")

        choice = input("Enter your choice: ")

        if choice == '1':
            face_encrypt.register_face()
        elif choice == '2':
            voice_encrypt.register_voice(
                out_enc_path=encrypted_file,
                key_path=key_file,
                save_wav_path=wav_debug
            )
        elif choice == '3':
            # --- ADDED CHECK FOR CONSISTENCY ---
            if os.path.exists(face_encoding_file):
                face_encrypt.verify_face()
            else:
                print("⚠️ No registered face found. Please register a face first.")
            # ------------------------------------
        elif choice == '4':
            if os.path.exists(encrypted_file) and os.path.exists(key_file):
                voice_encrypt.verify_voice(encrypted_file, key_file)
            else:
                print("⚠️ No registered voice found. Please register your voice first.")
        elif choice == '5':
            print("Exiting...")
            break
        else:
            print("❌ Invalid choice. Try again.")


if __name__ == "__main__":
    main()
