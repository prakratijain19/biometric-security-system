#  Aperture Biometrics: A Multi-Modal Security System 🔐

![Python Version](https://img.shields.io/badge/python-3.9+-blue.svg)
![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)

A secure, web-based authentication system built with Python and Flask that uses a combination of face and voice recognition to verify user identity. All sensitive biometric data is encrypted to ensure privacy and security.



***

## ✨ Features

* ✅ **Multi-Factor Biometric Login:** Combines facial geometry and voice patterns for robust security.
* ✅ **End-to-End Encryption:** Biometric templates are encrypted using symmetric-key cryptography (`Fernet`) before being stored.
* ✅ **User-Friendly Interface:** A clean, modern web interface for seamless user registration and verification.
* ✅ **Real-Time Processing:** Performs face and voice analysis in real-time with instant feedback.

***

## ⚙️ How It Works

The system follows a two-step process for registration and verification:

1.  **Face Biometrics**:
    * The `face_recognition` library captures the user's face via webcam.
    * It converts the facial features into a unique 128-dimension mathematical vector (an "encoding").
    * This encoding is then encrypted and stored as a local file.

2.  **Voice Biometrics**:
    * The user's voice is recorded for a few seconds.
    * `Librosa` processes the audio to extract its **Mel-Frequency Cepstral Coefficients (MFCCs)**, which represent the unique characteristics of a person's voice.
    * During verification, the **Dynamic Time Warping (DTW)** algorithm compares the new sample's MFCCs to the stored template to measure similarity.

***

## 🛠️ Tech Stack

* **Backend:** Python, Flask
* **Biometrics:** `face_recognition`, `librosa`, `dtw-python`, `OpenCV`
* **Security:** `cryptography`
* **Frontend:** HTML5, CSS3, JavaScript

***

## 🚀 Getting Started

Follow these instructions to get a copy of the project up and running on your local machine.

### Prerequisites

* Python 3.8+
* A C++ compiler (required by `dlib`, a dependency of `face_recognition`)
* A webcam and microphone

### Installation

1.  **Clone the repository:**
    ```bash
    git clone [https://github.com/prakratijain19/Multi-Modal-Biometric-Cryptography-.git](https://github.com/prakratijain19/Multi-Modal-Biometric-Cryptography-.git)
    cd Multi-Modal-Biometric-Cryptography-
    ```

2.  **Create and activate a virtual environment:**
    ```bash
    # Create the environment
    python -m venv venv

    # Activate on Windows
    .\venv\Scripts\activate

    # Activate on macOS/Linux
    source venv/bin/activate
    ```

3.  **Install the required packages:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Run the Flask application:**
    ```bash
    python app.py
    ```

5.  Open your web browser and navigate to **`https://127.0.0.1:5000`**. You may need to accept a security exception since it uses a self-signed SSL certificate for microphone access.

***

## 📂 Project Structure

├── app.py # Main Flask application file ├── voice_encrypt.py # Handles voice processing and encryption ├── encryption_module.py # General encryption/decryption utilities ├── templates/ │ └── index.html # Frontend HTML and JavaScript ├── data/ # Folder for storing encrypted biometric files ├── requirements.txt # Project dependencies └── README.md # You are here!


***

## ⚖️ License

This project is licensed under the MIT License.