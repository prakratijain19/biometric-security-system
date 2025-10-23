import cv2
import face_recognition
import os
import numpy as np

ENCODINGS_DIR = "data/face_encodings"
os.makedirs(ENCODINGS_DIR, exist_ok=True)


def register_face():
    video_capture = cv2.VideoCapture(0)
    print("Press 's' to save your face encoding, 'q' to quit.")

    while True:
        ret, frame = video_capture.read()
        if not ret:
            continue

        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        face_locations = face_recognition.face_locations(rgb_frame)

        for (top, right, bottom, left) in face_locations:
            cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)

        cv2.imshow("Register Face", frame)
        key = cv2.waitKey(1) & 0xFF

        if key == ord("s") and face_locations:
            face_encoding = face_recognition.face_encodings(
                rgb_frame, face_locations)[0]
            filename = os.path.join(ENCODINGS_DIR, "user_face.npy")
            np.save(filename, face_encoding)
            print(f"Face encoding saved at {filename}")
            break

        elif key == ord("q"):
            break

    video_capture.release()
    cv2.destroyAllWindows()


def verify_face(threshold=0.6):
    enc_file = os.path.join(ENCODINGS_DIR, "user_face.npy")
    if not os.path.exists(enc_file):
        print("No registered face found. Please register first.")
        return

    known_encoding = np.load(enc_file)
    video_capture = cv2.VideoCapture(0)
    print("Face verification started. Press 'q' to quit.")

    while True:
        ret, frame = video_capture.read()
        if not ret:
            continue

        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        face_locations = face_recognition.face_locations(rgb_frame)
        face_encodings = face_recognition.face_encodings(
            rgb_frame, face_locations)

        for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
            matches = face_recognition.compare_faces(
                [known_encoding], face_encoding, tolerance=threshold)

            label = "Invalid Face"
            color = (0, 0, 255)

            if True in matches:
                label = "Valid Face"
                color = (0, 255, 0)

            cv2.rectangle(frame, (left, top), (right, bottom), color, 2)
            cv2.rectangle(frame, (left, bottom - 35),
                          (right, bottom), color, cv2.FILLED)
            font = cv2.FONT_HERSHEY_DUPLEX
            cv2.putText(frame, label, (left + 6, bottom - 6),
                        font, 1.0, (255, 255, 255), 1)

        cv2.imshow('Face Verification', frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    video_capture.release()
    cv2.destroyAllWindows()
    print("Verification process ended.")


if __name__ == "__main__":
    choice = input(
        "Choose an option:\n1. Register face\n2. Verify face\nEnter choice (1 or 2): ")
    if choice == '1':
        register_face()
    elif choice == '2':
        verify_face()
    else:
        print("Invalid choice.")
