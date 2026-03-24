# 🎬 MoodFlick – Emotion-Aware Movie Recommendation Website

> **MCA Project** | Sant Gadge Baba Amravati University, Amravati | 2025–2026

An AI-powered web application that detects your **facial emotion in real-time** using your webcam and instantly recommends movies matching your current mood.

---

## 🚀 Features

| Feature | Description |
|---|---|
| 🎭 Real-time Emotion Detection | Webcam captures face → ML model classifies emotion |
| 🍿 1000+ Movie Library | Integrated IMDb Top 1000 dataset for high-quality variety |
| 🎞️ High-Res Posters | Automated URL cleaning for stunning HD movie visuals |
| ✨ Premium Custom Cursor | Interactive, glowing cursor follower with hover effects |
| 👤 User Authentication | Register / Login / Logout with password hashing |
| 📜 History Tracking | View past emotion detections and recommendations |
| 📊 Mood Profile | Statistics showing your most frequent emotions |
| 🎨 Premium Dark UI | Glassmorphism design with neon emotion-specific colors |

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python 3.11+, Flask 3.x |
| ML / CV | FER (Facial Expression Recognition), OpenCV, TensorFlow |
| Database | SQLite (via Python `sqlite3`) |
| Frontend | HTML5, CSS3 (Glassmorphism), Vanilla JavaScript |
| Fonts | Google Fonts – Inter + Outfit |

---

## 📁 Project Structure

```
EmotionMovies/
├── app.py                  # Flask application + all routes
├── emotion_detector.py     # ML emotion detection (FER + OpenCV fallback)
├── movies_db.py            # Logic to serve 12 randomized picks
├── movies_extended.json    # IMDb Top 1000 dataset (Processed)
├── imdb_importer.py        # Automated HD data importer & cleaning script
├── database.py             # SQLite schema + helpers
├── requirements.txt        # Python dependencies
├── emotions.db             # Auto-created SQLite database
├── templates/
│   ├── base.html           # Shared layout + navbar
│   ├── index.html          # Home + webcam detector
│   ├── recommend.html      # Movie grid
│   ├── history.html        # Timeline of past sessions
│   ├── login.html
│   └── register.html
└── static/
    ├── css/style.css       # Full design system
    └── js/
        ├── camera.js       # Webcam capture + API
        └── app.js          # UI interactions
```

---

## ⚙️ Installation & Setup

### 1. Navigate to the project folder
```bash
cd "Anti Gravity Code/EmotionMovies"
```

### 2. (Recommended) Create a virtual environment
```bash
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # macOS / Linux
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```
> ⏳ This installs TensorFlow (CPU). First run may take a few minutes to download ML model weights (~30 MB).

### 4. Run the application
```bash
python app.py
```

### 5. Open in browser
```
http://127.0.0.1:5000
```

---

## 🧠 Emotion Detection

The system uses the **FER (Facial Expression Recognition)** library:
- **Primary**: Keras mini-Xception model trained on FER2013 dataset
- **Fallback**: OpenCV Haarcascade + heuristic when FER is unavailable or no face is detected

**Supported Emotions**: 😄 Happy · 😢 Sad · 😠 Angry · 😨 Fearful · 😐 Neutral · 🤢 Disgusted · 😮 Surprised

---

## 🎬 Movie Categories

Each emotion pulls from the **IMDb Top 1000** dataset, serving **12 randomized picks** with HD posters:

- **Happy** → Feel-good & Adventure (Toy Story, Coco, The Intouchables…)
- **Sad** → Emotional Dramas (Schindler's List, The Green Mile…)
- **Angry** → Crime & Intensity (The Godfather, Pulp Fiction…)
- **Fear** → Thrillers & Horror (The Silence of the Lambs, Psycho…)
- **Neutral** → Grounded Dramas (12 Angry Men, Citizen Kane…)
- **Disgust** → Dark Realism (Joker, Requiem for a Dream…)
- **Surprise** → Mind-blowing Twists (Inception, The Prestige, Interstellar…)

---

## 🔒 Privacy

Your camera feed **never leaves your browser** in a stream. Only a single JPEG snapshot is sent to the server for analysis, and the camera is immediately stopped after capture.

---

## 🔮 Future Scope

- Mobile app integration (React Native / Flutter)
- OTT platform deep links (Netflix, Prime)
- Voice emotion detection (tone analysis)
- Improved ML model accuracy (custom training)
- Movie trailer embedding

---

## 📱 Accessing from Other Devices (Network Access)

Since the app is configured to run on `0.0.0.0`, you can access it from your phone, tablet, or another computer on the same Wi-Fi network:

1.  **Find your Local IP Address**:
    - Open Command Prompt and type `ipconfig`.
    - Look for "IPv4 Address" (e.g., `192.168.1.10`).
2.  **Open the URL on your device**:
    - Open the browser on your phone/tablet.
    - Go to `http://192.168.1.10:5000`.
3.  **Windows Firewall Note**:
    - If it doesn't load, you may need to allow Python through your Windows Firewall or temporarily disable it for the private network.
4.  **Camera Permissions**:
    - Most mobile browsers require **HTTPS** for camera access. For local development, you might need to use a tool like `ngrok` or a local tunnel if you want to test the camera from a phone without setting up a self-signed certificate.

---

- FER Library – https://github.com/justinshenk/fer
- TensorFlow / Keras – https://www.tensorflow.org
- OpenCV – https://opencv.org
- Flask – https://flask.palletsprojects.com
- TMDB – https://www.themoviedb.org
