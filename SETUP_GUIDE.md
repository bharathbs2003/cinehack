# EduDub AI - Complete Setup Guide

## Overview

EduDub AI is a production-ready multilingual video dubbing platform featuring:

- **WhisperX Transcription** - Word-level timestamps with high accuracy
- **Speaker Diarization** - Automatic speaker identification using pyannote
- **Emotion Detection** - Context-aware emotion recognition with SpeechBrain
- **Neural Translation** - High-quality translation with NLLB-200
- **Emotion-Aware TTS** - Natural voice generation with ElevenLabs or Murf
- **Lip-Sync** - Optional Wav2Lip integration for perfect lip synchronization
- **Async Processing** - Celery-based task queue for scalable processing

## Quick Start

### Prerequisites

- Python 3.10+
- FFmpeg installed and in PATH
- Redis server (for Celery)
- Node.js 18+ (for frontend)
- (Optional) CUDA-capable GPU for faster processing
- (Optional) Wav2Lip repository cloned

### 1. Clone Repository

```bash
git clone https://github.com/yourusername/EduDubAI.git
cd EduDubAI
```

### 2. Set Up Environment Variables

Copy the example environment file and fill in your API keys:

```bash
cp .env.example .env
```

Edit `.env` with your API keys:

```env
# Required
MURF_API_KEY=your_murf_api_key
OPENAI_API_KEY=your_openai_api_key

# Optional but recommended
ELEVENLABS_API_KEY=your_elevenlabs_key
HUGGINGFACE_TOKEN=your_hf_token
```

### 3. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Accept pyannote terms (required for speaker diarization)
# Visit: https://huggingface.co/pyannote/speaker-diarization
# And accept the user agreement, then set HUGGINGFACE_TOKEN in .env
```

### 4. Frontend Setup

```bash
cd ../frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

### 5. Start Redis (for Celery)

#### Option A: Using Docker
```bash
docker run -d -p 6379:6379 redis:7-alpine
```

#### Option B: Install locally
- Windows: Download from https://github.com/microsoftarchive/redis/releases
- Linux: `sudo apt-get install redis-server`
- Mac: `brew install redis`

### 6. Start Backend Services

In separate terminal windows:

#### Terminal 1 - FastAPI Server
```bash
cd backend
source venv/bin/activate  # or venv\Scripts\activate on Windows
python -m app.main_v2
```

#### Terminal 2 - Celery Worker
```bash
cd backend
source venv/bin/activate
celery -A app.celery_config:celery_app worker --loglevel=info --concurrency=2
```

#### Terminal 3 - Celery Beat (optional, for scheduled tasks)
```bash
cd backend
source venv/bin/activate
celery -A app.celery_config:celery_app beat --loglevel=info
```

## Docker Deployment

For production deployment, use Docker Compose:

```bash
# Build and start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### GPU Support in Docker

Edit `docker-compose.yml` and set `ENABLE_GPU: "true"` in build args, then uncomment the GPU deployment section.

## Configuration

### API Keys Required

1. **MURF_API_KEY** - Get from https://murf.ai/
2. **OPENAI_API_KEY** - Get from https://platform.openai.com/
3. **HUGGINGFACE_TOKEN** - Get from https://huggingface.co/settings/tokens
4. **ELEVENLABS_API_KEY** (Optional) - Get from https://elevenlabs.io/

### Pipeline Configuration

Edit `.env` to enable/disable features:

```env
USE_WHISPERX=true          # Use WhisperX (recommended)
USE_DIARIZATION=true       # Enable speaker diarization
USE_EMOTION_DETECTION=true # Enable emotion detection
USE_ELEVENLABS=false       # Use ElevenLabs TTS (requires API key)
USE_WAV2LIP=false          # Enable lip-sync (requires setup)
```

## Optional: Wav2Lip Setup

For lip-sync functionality:

1. Clone Wav2Lip repository:
```bash
git clone https://github.com/Rudrabha/Wav2Lip.git
```

2. Download pre-trained model:
```bash
cd Wav2Lip
mkdir -p models
# Download wav2lip_gan.pth from:
# https://github.com/Rudrabha/Wav2Lip
```

3. Update `.env`:
```env
USE_WAV2LIP=true
WAV2LIP_DIR=path/to/Wav2Lip
```

## API Usage

### Using the Web UI

1. Navigate to `http://localhost:5173`
2. Upload a video file
3. Select target language
4. Configure options (diarization, emotion, etc.)
5. Click "Generate Dub"
6. Download the result when complete

### Using the REST API

#### Create Dubbing Job

```bash
curl -X POST "http://localhost:8000/api/v2/dub" \
  -F "file=@video.mp4" \
  -F "target_language=hi" \
  -F "source_language=en" \
  -F "use_whisperx=true" \
  -F "use_diarization=true" \
  -F "use_emotion=true"
```

Response:
```json
{
  "job_id": "abc123",
  "task_id": "xyz789",
  "status": "queued"
}
```

#### Check Job Status

```bash
curl "http://localhost:8000/api/v2/status/abc123?task_id=xyz789"
```

Response:
```json
{
  "job_id": "abc123",
  "task_id": "xyz789",
  "status": "processing",
  "progress": 65,
  "stage": "voice_generation",
  "message": "Generating dubbed voices..."
}
```

#### Download Result

```bash
curl "http://localhost:8000/api/v2/result/abc123" -o dubbed_video.mp4
```

#### Get Transcript

```bash
curl "http://localhost:8000/api/v2/transcript/abc123" -o transcript.json
```

## Supported Languages

- English (en)
- Hindi (hi)
- Spanish (es)
- French (fr)
- German (de)
- Chinese (zh)
- Japanese (ja)
- Korean (ko)
- Arabic (ar)
- Portuguese (pt)
- Russian (ru)
- Italian (it)
- Marathi (mr)
- Bengali (bn)
- Tamil (ta)
- Telugu (te)

## Performance Optimization

### GPU Acceleration

Install CUDA-enabled PyTorch:

```bash
pip install torch==2.1.2 torchaudio==2.1.2 --index-url https://download.pytorch.org/whl/cu118
```

### Batch Processing

For multiple videos:

```python
from app.tasks import process_video_dubbing

jobs = []
for video_path in video_list:
    task = process_video_dubbing.delay(
        video_path=video_path,
        target_language="hi"
    )
    jobs.append(task.id)
```

### Caching

WhisperX and translation models are automatically cached in the `models/` directory.

## Troubleshooting

### Issue: "HUGGINGFACE_TOKEN required"

**Solution**: Get a token from https://huggingface.co/settings/tokens and add to `.env`

### Issue: "FFmpeg not found"

**Solution**: Install FFmpeg and add to system PATH
- Windows: https://ffmpeg.org/download.html
- Linux: `sudo apt-get install ffmpeg`
- Mac: `brew install ffmpeg`

### Issue: "Redis connection failed"

**Solution**: Ensure Redis server is running on port 6379

### Issue: Slow processing

**Solutions**:
- Enable GPU acceleration
- Disable emotion detection and/or diarization
- Reduce Celery concurrency
- Use lighter models (e.g., WhisperX "base" instead of "large")

### Issue: Out of memory

**Solutions**:
- Process shorter videos
- Disable GPU and use CPU
- Reduce batch sizes in models
- Increase system swap space

## Testing

Run validation tests:

```bash
cd backend
pytest tests/ -v
```

Test specific video:

```python
from app.validation import DubbingValidator

validator = DubbingValidator()
results = validator.validate_output(
    original_video_path="input.mp4",
    dubbed_video_path="output/final_dubbed.mp4",
    transcript_path="output/transcript.json"
)

print(results)
```

## Production Deployment

### Using Docker Compose

```bash
docker-compose -f docker-compose.prod.yml up -d
```

### Environment Variables for Production

- Set strong Redis password
- Use environment-specific API keys
- Configure CORS properly in `main_v2.py`
- Set up SSL/TLS certificates
- Use a reverse proxy (Nginx/Caddy)

### Scaling

Increase Celery workers:

```bash
celery -A app.celery_config:celery_app worker --concurrency=4
```

Or use multiple worker instances:

```bash
# Worker 1
celery -A app.celery_config:celery_app worker -n worker1@%h

# Worker 2
celery -A app.celery_config:celery_app worker -n worker2@%h
```

## License

[Your License Here]

## Support

For issues and questions:
- GitHub Issues: https://github.com/yourusername/EduDubAI/issues
- Email: support@edudub.ai

## Credits

Built with:
- WhisperX: https://github.com/m-bain/whisperX
- pyannote.audio: https://github.com/pyannote/pyannote-audio
- SpeechBrain: https://github.com/speechbrain/speechbrain
- NLLB: https://github.com/facebookresearch/fairseq/tree/nllb
- Wav2Lip: https://github.com/Rudrabha/Wav2Lip

