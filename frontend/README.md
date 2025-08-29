# 🎙 EduDub Live  

[![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-009688?logo=fastapi)](https://fastapi.tiangolo.com/)  
[![React](https://img.shields.io/badge/Frontend-React%20(Vite%20+%20Tailwind)-61DBFB?logo=react)](https://react.dev/)  
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)  
[![Python](https://img.shields.io/badge/Python-3.9+-3776AB?logo=python)](https://www.python.org/)  
[![Docker](https://img.shields.io/badge/Docker-ready-2496ED?logo=docker)](https://www.docker.com/)  

---

## 🌟 Overview  

**EduDub Live** is an **AI-powered real-time multilingual video dubbing platform** that helps creators, educators, and businesses **localize content instantly**.  

It takes any input video, automatically:  
1. **Transcribes** speech into text 📝  
2. **Translates** into 20+ supported languages 🌍  
3. **Detects speaker’s gender** for natural voice matching 🧑‍🤝‍🧑  
4. **Generates lifelike voices** using Murf/ElevenLabs 🎙  
5. **Merges dubbed audio with video** using FFmpeg 🎬  
6. Provides a **download-ready dubbed video** ⬇️  

⚡ Built for **global accessibility**, EduDub helps you **reach new audiences effortlessly**.  

---

## ❓ What is EduDub AI?  

EduDub AI is an **intelligent video dubbing assistant** designed to make global communication seamless.  
It eliminates language barriers by **automating transcription, translation, dubbing, and syncing**—all in one workflow.  

---

## 👥 Who is EduDub For?  

EduDub serves a wide range of users:  

- 🎓 **Educators & Trainers** – Deliver lectures and tutorials worldwide.  
- 🎬 **Content Creators** – Dub YouTube, Instagram, TikTok, and short videos.  
- 🏢 **Businesses & Enterprises** – Localize ads, onboarding, and training videos.  
- 🌍 **NGOs & Non-profits** – Spread awareness in multiple languages.  
- 🎮 **Gamers & Streamers** – Provide commentary for international fans.  

---

## 💡 What Can EduDub Do?  

- 🎥 **Upload any video** and generate a **dubbed version** in your chosen language.  
- 🌍 **Supports 20+ languages** (Hindi, Spanish, Japanese, Arabic, French, etc.).  
- 🧑‍🤝‍🧑 **Gender-aware dubbing** → Assigns male/female voices based on speaker.  
- 🗣 **Lip-sync ready** (Wav2Lip optional).  
- ⚡ **Fast & scalable backend** powered by FastAPI + WebSockets.  
- 🎨 **Modern UI** built with Tailwind + Framer Motion.  
- ⬇️ **Download final dubbed video** with a single click.  

---

## 🛠 Tech Stack  

**Frontend**  
- ⚛ React (Vite)  
- 🎨 TailwindCSS (responsive UI)  
- 🎬 Framer Motion (smooth animations)  
- 🌐 Axios (API calls)  

**Backend**  
- ⚡ FastAPI (Python, async-first)  
- 📝 OpenAI Whisper (speech-to-text)  
- 🌍 Google Translate / OpenAI Translation  
- 🎙 Murf / ElevenLabs (realistic TTS)  
- 🎬 FFmpeg (audio-video processing)  

**DevOps / Infra**  
- 🐳 Docker support for containerization  
- ☁️ Deployable on AWS / GCP / Azure / Render / Railway  

---

## 📦 Installation & Setup  

### 1️⃣ Clone Repository  
```bash
git clone https://github.com/your-username/edudub-live.git
cd edudub-live
```

### 2️⃣ Backend Setup (FastAPI)  
```bash
cd backend
python -m venv venv
source venv/bin/activate   # Windows: venv\Scriptsctivate
pip install -r requirements.txt
```

Run server:  
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### 3️⃣ Frontend Setup (React + Vite)  
```bash
cd frontend
npm install
npm run dev
```

Visit → [http://localhost:5173](http://localhost:5173)  

---

## 📂 Project Structure  

```
edudub-live/
├── backend/             # FastAPI backend
│   ├── app/
│   │   ├── main.py      # API endpoints
│   │   ├── murf_client.py
│   │   ├── transcribe_translate.py
│   │   ├── speaker_utils.py
│   │   ├── ffmpeg_utils.py
│   │   └── config.py
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/            # React + Tailwind + Framer Motion
│   ├── src/
│   │   ├── App.jsx
│   │   ├── index.css
│   │   └── main.jsx
│   ├── package.json
│   └── vite.config.js
└── README.md
```

---

## 🌍 Supported Languages  

EduDub currently supports **20+ languages**:  

Hindi  
Marathi  
Spanish  
French  
German  
Italian  
Portuguese  
Japanese  
Korean  
Chinese  
Arabic  
Turkish  
Russian  
Dutch  
Bengali  
Tamil  
Telugu  
Gujarati  
Malayalam  
Urdu  

---

## 🚀 Workflow  

1. Upload video 🎥  
2. Extract + transcribe speech 📝  
3. Translate text into selected language 🌍  
4. Detect speaker’s gender 🧑/👩  
5. Generate natural voice 🎙  
6. Merge audio + video 🎬  
7. Download dubbed video ⬇️  

---

## 🧩 Future Roadmap  

- 🔴 **Live WebRTC dubbing** → stream & dub in real-time.  
- 🎭 **Lip-sync integration** with Wav2Lip.  
- 🎤 **Multiple speakers detection** with different AI voices.  
- 🖼 **Auto subtitles** (with translations).  
- ☁️ **Cloud-native scaling** for enterprise.  

---

## 🤝 Contributing  

We welcome contributions! 🚀  
1. Fork this repo  
2. Create your feature branch (`git checkout -b feature/my-feature`)  
3. Commit changes (`git commit -m "Add new feature"`)  
4. Push to branch (`git push origin feature/my-feature`)  
5. Create a Pull Request  

---

## 📜 License  

MIT License © 2025 **EduDub Team**  
