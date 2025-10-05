# EduDub AI - Advanced Video Dubbing Platform

**One-liner:** Production-ready multilingual AI dubbing system that transforms videos into fully dubbed versions while preserving emotion, speaker identity, and lip-sync accuracy.

## Team Members

**Chirtram Team:**
- **Bharat BS** - Backend Development
- **Rohit R Nair** - Backend Development  
- **Ananthu RB** - Frontend Development
- **Akash SL** - Model Training and Selection

## Elevator Pitch

EduDub AI breaks down language barriers by automatically dubbing videos into 16+ languages while preserving the original speaker's emotion, voice characteristics, and lip-sync accuracy. Our system uses state-of-the-art AI models including WhisperX for transcription, pyannote for speaker diarization, SpeechBrain for emotion detection, and NLLB-200 for translation to create professional-quality dubbed content.

## 🚀 Features

### Core Pipeline

1. **WhisperX Transcription** - Word-level timestamps with industry-leading accuracy
2. **Speaker Diarization** - Automatic speaker identification using pyannote
3. **Emotion Detection** - Real-time emotion recognition with SpeechBrain
4. **Neural Translation** - State-of-the-art NLLB-200 multilingual translation
5. **Emotion-Aware TTS** - Natural voice synthesis with ElevenLabs or Murf
6. **Wav2Lip Lip-Sync** - AI-powered lip synchronization
7. **Async Processing** - Scalable Celery-based task queue

### Supported Languages

🌍 **16+ Languages**: English, Hindi, Spanish, French, German, Chinese, Japanese, Korean, Arabic, Portuguese, Russian, Italian, Marathi, Bengali, Tamil, Telugu

### Technology Stack

**Backend:**
- FastAPI for high-performance API
- Celery + Redis for async processing
- WhisperX for transcription
- pyannote.audio for diarization
- SpeechBrain for emotion detection
- NLLB-200 for translation
- ElevenLabs/Murf for TTS
- Wav2Lip for lip-sync

**Frontend:**
- React 19 with Vite
- Framer Motion for animations
- Modern responsive UI

**Infrastructure:**
- Docker & Docker Compose
- GPU acceleration support
- Scalable worker architecture

## Live Demo

**URL / IP:** `http://localhost:5173` (when running locally)
**Endpoints:** see `deployment/ENDPOINTS.md`

## Quick Start (Local)

1. **Clone repo:**
   ```bash
   git clone https://github.com/bharathbs2003/EduDubAI.git
   cd EduDubAI
   ```

2. **Create `.env` from `.env.example`** and set required variables:
   ```bash
   cp .env.example .env
   # Edit .env with your API keys:
   # MURF_API_KEY=your_murf_key
   # OPENAI_API_KEY=your_openai_key
   # HUGGINGFACE_TOKEN=your_hf_token
   ```

3. **Backend Setup:**
   ```bash
   cd backend
   python -m venv venv
   # Windows:
   venv\Scripts\activate
   # Linux/Mac:
   source venv/bin/activate
   pip install -r requirements.txt
   ```

4. **Frontend Setup:**
   ```bash
   cd ../frontend
   npm install
   ```

5. **Start Services:**
   ```bash
   # Terminal 1 - Backend (from backend directory):
   python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
   
   # Terminal 2 - Frontend (from frontend directory):
   npm run dev
   ```

6. **Open `http://localhost:5173`**

## Tests

```bash
# Backend tests (from backend directory):
cd backend
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac
pip install -r requirements.txt
pytest tests/ -v

# Frontend tests (from frontend directory):
cd frontend
npm install
npm test
```

## Environment Variables

- `MURF_API_KEY` — Murf AI API key for text-to-speech
- `OPENAI_API_KEY` — OpenAI API key for Whisper transcription
- `HUGGINGFACE_TOKEN` — HuggingFace token for speaker diarization models
- `ELEVENLABS_API_KEY` — ElevenLabs API key (optional, for premium TTS)
- `PORT` — Port the server listens on (default: 8000)

## Known Limitations

- Feature X is incomplete; performance may degrade under heavy load.
- Wav2Lip lip-sync requires GPU acceleration for optimal performance.
- Processing time scales with video length (approximately 2-5x real-time).
- Some languages may have limited voice options in TTS providers.

## 📖 Usage

### Web Interface

1. Navigate to `http://localhost:5173`
2. Upload a video file (MP4, AVI, MOV supported)
3. Select source and target languages
4. Configure advanced options (diarization, emotion, lip-sync)
5. Click "Generate Dub"
6. Monitor progress in real-time
7. Download the result when complete!

### File Structure

```
EduDubAI/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI application
│   │   ├── main_v2.py           # Advanced API version
│   │   ├── pipeline.py          # Main processing pipeline
│   │   ├── whisperx_transcriber.py
│   │   ├── diarization.py
│   │   ├── emotion_detector.py
│   │   ├── nllb_translator.py
│   │   ├── elevenlabs_tts.py
│   │   ├── murf_client.py
│   │   ├── wav2lip_sync.py
│   │   ├── audio_reconstruction.py
│   │   ├── celery_config.py
│   │   ├── tasks.py
│   │   ├── config.py
│   │   └── validation.py
│   ├── requirements.txt
│   ├── Dockerfile
│   └── venv/
├── frontend/
│   ├── src/
│   │   ├── pages/
│   │   │   ├── Home.jsx
│   │   │   ├── Upload.jsx
│   │   │   └── UploadV2.jsx
│   │   ├── components/
│   │   │   ├── Navbar.jsx
│   │   │   ├── UploadNavbar.jsx
│   │   │   ├── VoiceWave.jsx
│   │   │   └── Footer.jsx
│   │   ├── App.jsx
│   │   └── main.jsx
│   ├── package.json
│   └── Dockerfile
├── deployment/
│   └── ENDPOINTS.md
├── tmp_uploads/                 # Temporary upload directory
├── output/                      # Final output directory
├── docker-compose.yml
├── start_backend.bat           # Windows startup script
├── start_backend.sh            # Linux/Mac startup script
├── start_frontend.ps1          # PowerShell frontend script
└── README.md
```

### REST API

```bash
# Create dubbing job
curl -X POST "http://localhost:8000/api/v2/dub" \
  -F "file=@video.mp4" \
  -F "target_language=hi" \
  -F "source_language=en"

# Check status
curl "http://localhost:8000/api/v2/status/{job_id}?task_id={task_id}"

# Download result
curl "http://localhost:8000/api/v2/result/{job_id}" -o dubbed.mp4

# Get transcript
curl "http://localhost:8000/api/v2/transcript/{job_id}" -o transcript.json

# Interactive API documentation
# Visit: http://localhost:8000/docs
```

### Command Line

```bash
# From backend directory with virtual environment activated:
cd backend
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

python -m app.cli \
  --input video.mp4 \
  --lang hi \
  --output output/ \
  --whisperx \
  --diarization \
  --emotion
```

## 🔧 Configuration

### Environment Variables

```env
# Required API Keys
MURF_API_KEY=your_murf_key
OPENAI_API_KEY=your_openai_key

# Optional
ELEVENLABS_API_KEY=your_elevenlabs_key
HUGGINGFACE_TOKEN=your_hf_token

# Pipeline Settings
USE_WHISPERX=true
USE_DIARIZATION=true
USE_EMOTION_DETECTION=true
USE_ELEVENLABS=false
USE_WAV2LIP=false
```

### API Keys

1. **Murf API** - https://murf.ai/
2. **OpenAI** - https://platform.openai.com/
3. **ElevenLabs** - https://elevenlabs.io/
4. **HuggingFace** - https://huggingface.co/settings/tokens

## 📊 Performance

- **Processing Speed**: ~2-5x real-time (with GPU)
- **Accuracy**: >95% transcription, >90% emotion detection
- **Supported Video Length**: Up to 2 hours
- **Concurrent Jobs**: Scalable with multiple workers

## 🧪 Testing

```bash
cd backend
pytest tests/ -v
```

### Validation

```python
from app.validation import DubbingValidator

validator = DubbingValidator()
results = validator.validate_output(
    original_video_path="input.mp4",
    dubbed_video_path="output/final.mp4",
    transcript_path="output/transcript.json"
)
```

## 📚 Documentation

- [Complete Setup Guide](SETUP_GUIDE.md)
- [API Documentation](http://localhost:8000/docs) (when running)
- [Architecture Overview](docs/ARCHITECTURE.md)
- [Troubleshooting](docs/TROUBLESHOOTING.md)

## 🤝 Contributing

Contributions welcome! Please read [CONTRIBUTING.md](CONTRIBUTING.md) first.

## 📝 Example Output

### Transcript JSON

```json
[
  {
    "start": 0.0,
    "end": 2.5,
    "text": "Hello, how are you?",
    "translated_text": "नमस्ते, आप कैसे हैं?",
    "speaker": "SPEAKER_00",
    "emotion": "neutral",
    "audio_path": "output/segment_0001.mp3"
  }
]
```

## 🎬 Example Workflow

```
Input Video (English)
    ↓
[Extract Audio] → audio.wav
    ↓
[WhisperX Transcription] → segments with timestamps
    ↓
[Speaker Diarization] → speaker labels
    ↓
[Emotion Detection] → emotion tags
    ↓
[NLLB Translation] → Hindi text
    ↓
[ElevenLabs TTS] → Hindi audio segments
    ↓
[Audio Reconstruction] → complete dubbed audio
    ↓
[Wav2Lip Lip-Sync] → final video
    ↓
Output: Dubbed Video (Hindi) + Transcript JSON
```

## ⚡ Performance Optimization

### GPU Acceleration

```bash
# Install CUDA-enabled PyTorch
pip install torch==2.1.2 torchaudio==2.1.2 --index-url https://download.pytorch.org/whl/cu118
```

### Scaling Workers

```bash
# Multiple workers
celery -A app.celery_config:celery_app worker --concurrency=4

# Distributed workers
celery -A app.celery_config:celery_app worker -n worker1@%h
celery -A app.celery_config:celery_app worker -n worker2@%h
```

## 🐛 Troubleshooting

**Issue: "ModuleNotFoundError: No module named 'pydantic_settings'"**
```bash
cd backend
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac
pip install pydantic-settings
```

**Issue: "HUGGINGFACE_TOKEN required"**
- Get token from https://huggingface.co/settings/tokens
- Accept pyannote model agreement
- Add to `.env` file: `HUGGINGFACE_TOKEN=your_token_here`

**Issue: "FFmpeg not found"**
- Install FFmpeg: https://ffmpeg.org/download.html
- Add FFmpeg to system PATH

**Issue: "Redis connection failed"**
- Install Redis: https://redis.io/download
- Or use Docker: `docker run -d -p 6379:6379 redis:7-alpine`

**Issue: Backend not starting**
```bash
# Ensure you're in the correct directory:
cd backend
venv\Scripts\activate  # Windows
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

**Issue: Frontend not starting**
```bash
# Ensure you're in the frontend directory:
cd frontend
npm install
npm run dev
```

**Issue: Slow processing**
- Enable GPU acceleration
- Reduce model sizes
- Disable optional features

See [SETUP_GUIDE.md](SETUP_GUIDE.md) for more troubleshooting.

## License

MIT

## Consent Statement

By submitting this project, we consent to event organizers and judges accessing the listed local endpoints while connected to the event Wi-Fi for evaluation purposes. We understand that organizers will not access private customer data and will only use provided credentials.

## 🙏 Acknowledgments

**Chirtram Team Development:**
- **Bharat BS** & **Rohit R Nair** - Backend architecture and API development
- **Ananthu RB** - Frontend UI/UX and React implementation
- **Akash SL** - AI model integration and optimization

**Open Source Libraries:**
- [WhisperX](https://github.com/m-bain/whisperX)
- [pyannote.audio](https://github.com/pyannote/pyannote-audio)
- [SpeechBrain](https://github.com/speechbrain/speechbrain)
- [NLLB](https://github.com/facebookresearch/fairseq/tree/nllb)
- [Wav2Lip](https://github.com/Rudrabha/Wav2Lip)

## 📧 Support

- GitHub Issues: [Create Issue](https://github.com/bharathbs2003/EduDubAI/issues)
- Email: support@edudub.ai
- Discord: [Join Server](https://discord.gg/edudub)

---

<div align="center">

**Built with ❤️ by the Chirtram Team**

[Website](https://edudub.ai) • [Documentation](https://docs.edudub.ai) • [Demo](https://demo.edudub.ai)

</div>
