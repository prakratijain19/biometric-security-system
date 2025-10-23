import os
import cv2
import numpy as np
from flask import Flask, render_template, Response, request, jsonify
from io import BytesIO
import soundfile as sf

# Import your custom scripts
from scripts import face_recognition_module as face_module
from scripts import voice_encrypt as voice_module
from scripts import encryption_module

# --- App & Path Configuration ---
app = Flask(__name__)

# Define base directories
DATA_DIR = "data"
KEYS_DIR = os.path.join(DATA_DIR, "keys")
VOICE_SAMPLES_DIR = os.path.join(DATA_DIR, "voice_samples")
FACE_ENCODINGS_DIR = os.path.join(DATA_DIR, "face_encodings")

# Create directories if they don't exist
os.makedirs(KEYS_DIR, exist_ok=True)
os.makedirs(VOICE_SAMPLES_DIR, exist_ok=True)
os.makedirs(FACE_ENCODINGS_DIR, exist_ok=True)

# Define file paths
VOICE_ENC_FILE = os.path.join(VOICE_SAMPLES_DIR, "encrypted_voice.mfcc")
VOICE_KEY_FILE = os.path.join(KEYS_DIR, "voice_key.key")
FACE_ENC_FILE = os.path.join(FACE_ENCODINGS_DIR, "user_face.npy.enc")
FACE_KEY_FILE = os.path.join(KEYS_DIR, "secret.key")

# Initialize global video capture
video_capture = None

# --- Helper Functions ---


def get_video_capture():
    """Initializes and returns a global video capture object."""
    global video_capture
    if video_capture is None or not video_capture.isOpened():
        video_capture = cv2.VideoCapture(0)
    return video_capture

# --- Face Biometrics Logic (No changes needed here) ---


def stream_face_frames(mode='verify'):
    cap = get_video_capture()
    known_encoding = None
    if mode == 'verify':
        if os.path.exists(FACE_ENC_FILE):
            try:
                known_encoding = encryption_module.decrypt_npy_file_to_array(
                    FACE_ENC_FILE, FACE_KEY_FILE)
            except Exception as e:
                print(f"Error decrypting face encoding: {e}")
    frame_count = 0
    process_every_n_frames = 5
    last_known_locations = []
    last_known_labels = []
    while True:
        success, frame = cap.read()
        if not success:
            break
        if frame_count % process_every_n_frames == 0:
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            current_locations = face_module.face_recognition.face_locations(
                rgb_frame)
            current_encodings = face_module.face_recognition.face_encodings(
                rgb_frame, current_locations)
            last_known_locations = current_locations
            last_known_labels = []
            for face_encoding in current_encodings:
                label = "Detecting..."
                if mode == 'verify':
                    if known_encoding is not None:
                        matches = face_module.face_recognition.compare_faces(
                            [known_encoding], face_encoding)
                        label = "Valid Face" if True in matches else "Invalid Face"
                    else:
                        label = "Register First"
                elif mode == 'register':
                    label = "Face Detected"
                last_known_labels.append(label)
        for (top, right, bottom, left), label in zip(last_known_locations, last_known_labels):
            color = (0, 255, 0)
            if "Invalid" in label or "Register" in label:
                color = (0, 0, 255)
            elif "Detecting" in label:
                color = (255, 165, 0)
            cv2.rectangle(frame, (left, top), (right, bottom), color, 2)
            cv2.rectangle(frame, (left, bottom - 35),
                          (right, bottom), color, cv2.FILLED)
            cv2.putText(frame, label, (left + 6, bottom - 6),
                        cv2.FONT_HERSHEY_DUPLEX, 0.8, (255, 255, 255), 1)
        frame_count += 1
        ret, buffer = cv2.imencode('.jpg', frame)
        frame_bytes = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

# --- Voice Biometrics Logic (No changes needed here) ---


def process_voice_registration(audio_bytes):
    return voice_module.register_voice_from_wav_bytes(audio_bytes, VOICE_ENC_FILE, VOICE_KEY_FILE)


def process_voice_verification(audio_bytes):
    if not (os.path.exists(VOICE_ENC_FILE) and os.path.exists(VOICE_KEY_FILE)):
        return {"success": False, "message": "No registered voice found."}
    verified, distance, threshold = voice_module.verify_voice_from_wav_bytes(
        audio_bytes, VOICE_ENC_FILE, VOICE_KEY_FILE)
    if distance is None:
        return {"success": False, "message": "Voice verification failed due to processing error."}
    return {"success": bool(verified), "distance": f"{distance:.2f}", "threshold": threshold}

# --- Flask Routes ---


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/video_feed/<mode>')
def video_feed(mode):
    return Response(stream_face_frames(mode), mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/register_face', methods=['POST'])
def register_face():
    # ... (function is unchanged)
    cap = get_video_capture()
    success, frame = cap.read()
    if not success:
        return jsonify({"success": False, "message": "Could not capture frame."})
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    face_locations = face_module.face_recognition.face_locations(rgb_frame)
    if not face_locations:
        return jsonify({"success": False, "message": "No face detected in the frame."})
    temp_npy_path = os.path.join(FACE_ENCODINGS_DIR, "temp_user_face.npy")
    face_encoding = face_module.face_recognition.face_encodings(
        rgb_frame, face_locations)[0]
    np.save(temp_npy_path, face_encoding)
    if not os.path.exists(FACE_KEY_FILE):
        encryption_module.generate_key(FACE_KEY_FILE)
    encryption_module.encrypt_npy_file(
        temp_npy_path, FACE_KEY_FILE, FACE_ENC_FILE)
    os.remove(temp_npy_path)
    return jsonify({"success": True, "message": "Face registered and encrypted successfully!"})


@app.route('/register_voice', methods=['POST'])
def register_voice():
    audio_file = request.files.get('audio_data')
    if not audio_file:
        return jsonify({"success": False, "message": "No audio data received."})
    if not (audio_file.filename.endswith('.wav') or audio_file.mimetype == 'audio/wav'):
        return jsonify({"success": False, "message": "Audio must be WAV format."})
    try:
        audio_bytes = audio_file.read()
        print(f"[DEBUG] Received audio bytes length: {len(audio_bytes)}")
        success = process_voice_registration(audio_bytes)
        if success:
            return jsonify({"success": True, "message": "Voice registered successfully!"})
        else:
            return jsonify({"success": False, "message": "Voice registration failed."})
    except Exception as e:
        import traceback
        tb = traceback.format_exc()
        print(f"[ERROR] Voice registration failed: {str(e)}\n{tb}")
        return jsonify({"success": False, "message": f"Error: {str(e)}", "trace": tb})


@app.route('/verify_voice', methods=['POST'])
def verify_voice():
    audio_file = request.files.get('audio_data')
    if not audio_file:
        return jsonify({"success": False, "message": "No audio data received."})
    if not (audio_file.filename.endswith('.wav') or audio_file.mimetype == 'audio/wav'):
        return jsonify({"success": False, "message": "Audio must be WAV format."})
    try:
        result = process_voice_verification(audio_file.read())
        return jsonify(result)
    except Exception as e:
        return jsonify({"success": False, "message": f"Error: {str(e)}"})

# --- ADD THIS NEW ROUTE ---


@app.route('/stop_video', methods=['POST'])
def stop_video():
    """Releases the global video capture object."""
    global video_capture
    if video_capture is not None and video_capture.isOpened():
        video_capture.release()
        video_capture = None
        print("Camera released by client.")
        return jsonify({"success": True, "message": "Camera released."})
    return jsonify({"success": False, "message": "Camera was not active."})


# --- Main Execution ---
if __name__ == '__main__':
    app.run(debug=True)
