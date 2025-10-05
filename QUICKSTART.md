# 🚀 EduDub AI - Quick Start Guide

Get up and running in 5 minutes!

## Prerequisites Check

Before starting, ensure you have:

- [ ] Python 3.10 or higher
- [ ] Node.js 18 or higher
- [ ] FFmpeg installed
- [ ] Git installed
- [ ] At least 8GB RAM
- [ ] API keys ready (Murf, OpenAI)

## Step 1: Get API Keys

### Required Keys

1. **Murf API Key** 🎤
   - Sign up at https://murf.ai/
   - Get API key from dashboard
   - Copy for later

2. **OpenAI API Key** 🤖
   - Sign up at https://platform.openai.com/
   - Create API key
   - Copy for later

### Optional Keys (Advanced Features)

3. **HuggingFace Token** 🤗
   - Sign up at https://huggingface.co/
   - Go to Settings → Access Tokens
   - Create token with read access
   - Accept pyannote model terms: https://huggingface.co/pyannote/speaker-diarization

4. **ElevenLabs API Key** 🗣️
   - Sign up at https://elevenlabs.io/
   - Get API key from profile

## Step 2: Clone & Setup

```bash
# Clone repository
git clone https://github.com/yourusername/EduDubAI.git
cd EduDubAI

# Create .env file
cp .env.example .env

# Edit .env with your API keys (use any text editor)
# Windows: notepad .env
# Mac/Linux: nano .env
```

### Edit .env File

```env
MURF_API_KEY=your_murf_key_here
OPENAI_API_KEY=your_openai_key_here
HUGGINGFACE_TOKEN=your_hf_token_here
```

## Step 3: Install Backend

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate it
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# Install dependencies (this may take 5-10 minutes)
pip install -r requirements.txt

cd ..
```

## Step 4: Install Frontend

```bash
cd frontend

# Install dependencies
npm install

cd ..
```

## Step 5: Start Redis

### Option A: Docker (Recommended)

```bash
docker run -d -p 6379:6379 --name edudub-redis redis:7-alpine
```

### Option B: Install Locally

**Windows:**
1. Download from https://github.com/microsoftarchive/redis/releases
2. Extract and run `redis-server.exe`

**Mac:**
```bash
brew install redis
brew services start redis
```

**Linux:**
```bash
sudo apt-get install redis-server
sudo systemctl start redis
```

## Step 6: Start Services

### Easy Way (Automated Scripts)

**Windows:**
```bash
# Double-click start_backend.bat
# Or run:
start_backend.bat
```

**Mac/Linux:**
```bash
chmod +x start_backend.sh
./start_backend.sh
```

### Manual Way (Separate Terminals)

**Terminal 1 - Backend API:**
```bash
cd backend
source venv/bin/activate  # or venv\Scripts\activate on Windows
python -m app.main_v2
```

**Terminal 2 - Celery Worker:**
```bash
cd backend
source venv/bin/activate
celery -A app.celery_config:celery_app worker --loglevel=info
```

**Terminal 3 - Frontend:**
```bash
cd frontend
npm run dev
```

## Step 7: Test It!

1. Open browser: http://localhost:5173
2. Upload a short test video (< 1 minute recommended for first test)
3. Select target language (e.g., Hindi)
4. Click "Generate Dub"
5. Wait for processing (2-5 minutes depending on video length)
6. Download result!

## Troubleshooting

### "Module not found" errors
```bash
cd backend
source venv/bin/activate
pip install -r requirements.txt
```

### "Redis connection refused"
- Check Redis is running: `redis-cli ping` should return "PONG"
- Restart Redis or use Docker command from Step 5

### "FFmpeg not found"
- **Windows**: Download from https://ffmpeg.org/download.html, add to PATH
- **Mac**: `brew install ffmpeg`
- **Linux**: `sudo apt-get install ffmpeg`

### Frontend won't start
```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
npm run dev
```

### API key errors
- Check `.env` file has correct keys
- No quotes needed: `MURF_API_KEY=abc123`
- Restart backend after changing `.env`

## Next Steps

### Test CLI
```bash
cd backend
source venv/bin/activate
python -m app.cli --input sample.mp4 --lang hi --whisperx --diarization
```

### Enable Advanced Features

Edit `.env`:
```env
USE_WHISPERX=true           # Better transcription
USE_DIARIZATION=true        # Speaker identification
USE_EMOTION_DETECTION=true  # Emotion recognition
USE_ELEVENLABS=true         # Better TTS (requires API key)
USE_WAV2LIP=false           # Lip sync (requires setup)
```

### Production Deployment

See [SETUP_GUIDE.md](SETUP_GUIDE.md) for:
- Docker deployment
- GPU acceleration
- Scaling workers
- Security best practices

## Getting Help

- 📚 Full Documentation: [SETUP_GUIDE.md](SETUP_GUIDE.md)
- 🐛 Report Issues: [GitHub Issues](https://github.com/yourusername/EduDubAI/issues)
- 💬 Community: [Discord](https://discord.gg/edudub)
- 📧 Email: support@edudub.ai

## System Requirements

### Minimum
- CPU: 4 cores
- RAM: 8GB
- Storage: 20GB
- Network: Stable internet for API calls

### Recommended
- CPU: 8+ cores
- RAM: 16GB+
- GPU: NVIDIA GPU with 6GB+ VRAM (for faster processing)
- Storage: 50GB+ SSD
- Network: High-speed internet

## Supported Video Formats

- MP4, MKV, AVI, MOV, WEBM
- Max duration: 2 hours
- Max size: 2GB

## Supported Languages

English, Hindi, Spanish, French, German, Chinese, Japanese, Korean, Arabic, Portuguese, Russian, Italian, Marathi, Bengali, Tamil, Telugu

---

**Happy Dubbing! 🎬🎙️**

