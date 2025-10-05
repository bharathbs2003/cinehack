# EduDub AI - Architecture Documentation

## System Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                          User Interface Layer                            │
│                                                                          │
│  ┌────────────────┐      ┌──────────────────┐      ┌─────────────────┐ │
│  │  Web Browser   │      │   REST Client    │      │   CLI Tool      │ │
│  │  (React App)   │      │   (curl/Postman) │      │   (Python)      │ │
│  └────────┬───────┘      └────────┬─────────┘      └────────┬────────┘ │
│           │                       │                         │          │
└───────────┼───────────────────────┼─────────────────────────┼──────────┘
            │                       │                         │
            └───────────────────────┴─────────────────────────┘
                                    │
                           HTTP/REST API
                                    │
┌───────────────────────────────────▼──────────────────────────────────────┐
│                         API Gateway Layer                                 │
│                                                                           │
│  ┌──────────────────────────────────────────────────────────────────┐   │
│  │                      FastAPI Application                          │   │
│  │  - CORS middleware                                                │   │
│  │  - Request validation                                             │   │
│  │  - Authentication (future)                                        │   │
│  │  - Rate limiting (future)                                         │   │
│  └──────────────────────────────────────────────────────────────────┘   │
│                                                                           │
│  Endpoints:                                                               │
│  • POST   /api/v2/dub          - Submit video for dubbing               │
│  • GET    /api/v2/status/{id}  - Check processing status                │
│  • GET    /api/v2/result/{id}  - Download dubbed video                  │
│  • GET    /api/v2/transcript/{id} - Download transcript                 │
│  • DELETE /api/v2/job/{id}     - Delete job                             │
└───────────────────────────────────┬───────────────────────────────────────┘
                                    │
                         Celery Task Queue
                                    │
┌───────────────────────────────────▼───────────────────────────────────────┐
│                        Task Processing Layer                               │
│                                                                            │
│  ┌─────────────┐      ┌─────────────┐      ┌─────────────┐              │
│  │  Worker 1   │      │  Worker 2   │      │  Worker N   │              │
│  │             │      │             │      │             │              │
│  │  ┌───────┐  │      │  ┌───────┐  │      │  ┌───────┐  │              │
│  │  │ Task  │  │      │  │ Task  │  │      │  │ Task  │  │              │
│  │  │ Queue │  │      │  │ Queue │  │      │  │ Queue │  │              │
│  │  └───────┘  │      │  └───────┘  │      │  └───────┘  │              │
│  └─────────────┘      └─────────────┘      └─────────────┘              │
│                                                                            │
│  Redis Broker: Task distribution & result storage                         │
└───────────────────────────────────┬────────────────────────────────────────┘
                                    │
                         Execute Pipeline
                                    │
┌───────────────────────────────────▼────────────────────────────────────────┐
│                       Processing Pipeline Layer                             │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐  │
│  │                    1. Input Processing                              │  │
│  │  - Video validation                                                 │  │
│  │  - Audio extraction (FFmpeg)                                        │  │
│  │  - Format conversion                                                │  │
│  └─────────────────────────────────────────────────────────────────────┘  │
│                                    ↓                                       │
│  ┌─────────────────────────────────────────────────────────────────────┐  │
│  │                    2. Transcription (WhisperX)                      │  │
│  │  - Speech-to-text conversion                                        │  │
│  │  - Word-level timestamps                                            │  │
│  │  - Language detection                                               │  │
│  └─────────────────────────────────────────────────────────────────────┘  │
│                                    ↓                                       │
│  ┌─────────────────────────────────────────────────────────────────────┐  │
│  │                    3. Speaker Diarization (pyannote)                │  │
│  │  - Speaker identification                                           │  │
│  │  - Speaker segmentation                                             │  │
│  │  - Label assignment                                                 │  │
│  └─────────────────────────────────────────────────────────────────────┘  │
│                                    ↓                                       │
│  ┌─────────────────────────────────────────────────────────────────────┐  │
│  │                    4. Emotion Detection (SpeechBrain)               │  │
│  │  - Per-segment emotion analysis                                     │  │
│  │  - 7 emotion categories                                             │  │
│  │  - Confidence scoring                                               │  │
│  └─────────────────────────────────────────────────────────────────────┘  │
│                                    ↓                                       │
│  ┌─────────────────────────────────────────────────────────────────────┐  │
│  │                    5. Translation (NLLB-200)                        │  │
│  │  - Neural machine translation                                       │  │
│  │  - Context preservation                                             │  │
│  │  - 200+ language pairs                                              │  │
│  └─────────────────────────────────────────────────────────────────────┘  │
│                                    ↓                                       │
│  ┌─────────────────────────────────────────────────────────────────────┐  │
│  │                    6. Voice Generation                              │  │
│  │                                                                      │  │
│  │  ┌─────────────────────┐    ┌─────────────────────┐                │  │
│  │  │  ElevenLabs TTS     │ or │  Murf TTS           │                │  │
│  │  │  - Emotion modulation│   │  - Gender detection │                │  │
│  │  │  - Voice cloning    │    │  - Voice selection  │                │  │
│  │  │  - Multi-speaker    │    │  - Batch processing │                │  │
│  │  └─────────────────────┘    └─────────────────────┘                │  │
│  └─────────────────────────────────────────────────────────────────────┘  │
│                                    ↓                                       │
│  ┌─────────────────────────────────────────────────────────────────────┐  │
│  │                    7. Audio Reconstruction                          │  │
│  │  - Segment timing alignment                                         │  │
│  │  - Volume normalization                                             │  │
│  │  - Track merging                                                    │  │
│  └─────────────────────────────────────────────────────────────────────┘  │
│                                    ↓                                       │
│  ┌─────────────────────────────────────────────────────────────────────┐  │
│  │                    8. Lip-Sync (Wav2Lip - Optional)                │  │
│  │  - Face detection                                                   │  │
│  │  - Lip movement synthesis                                           │  │
│  │  - Video-audio alignment                                            │  │
│  └─────────────────────────────────────────────────────────────────────┘  │
│                                    ↓                                       │
│  ┌─────────────────────────────────────────────────────────────────────┐  │
│  │                    9. Video Reconstruction (FFmpeg)                 │  │
│  │  - Audio track replacement                                          │  │
│  │  - Format conversion                                                │  │
│  │  - Quality optimization                                             │  │
│  └─────────────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                              Store Results
                                    │
┌───────────────────────────────────▼─────────────────────────────────────────┐
│                          Storage Layer                                       │
│                                                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐   │
│  │   Uploads    │  │   Output     │  │   Models     │  │   Logs       │   │
│  │   Directory  │  │   Directory  │  │   Cache      │  │   Files      │   │
│  │              │  │              │  │              │  │              │   │
│  │ - Original   │  │ - Final video│  │ - WhisperX   │  │ - Process    │   │
│  │   videos     │  │ - Dubbed     │  │ - NLLB       │  │   logs       │   │
│  │ - Temp files │  │   audio      │  │ - pyannote   │  │ - Errors     │   │
│  │              │  │ - Transcript │  │ - SpeechBrain│  │ - Metrics    │   │
│  └──────────────┘  └──────────────┘  └──────────────┘  └──────────────┘   │
└──────────────────────────────────────────────────────────────────────────────┘
```

## Data Flow

### Request Flow

```
User → Upload Video → FastAPI
                        ↓
                   Validate Input
                        ↓
                   Save to Disk
                        ↓
                 Create Celery Task
                        ↓
                   Return Job ID
                        ↓
                 Queue in Redis
```

### Processing Flow

```
Celery Worker picks task
        ↓
Initialize Pipeline
        ↓
Extract Audio (FFmpeg)
        ↓
Transcribe (WhisperX)
        ↓
Diarize Speakers (pyannote)
        ↓
Detect Emotions (SpeechBrain)
        ↓
Translate Text (NLLB)
        ↓
Generate Voices (ElevenLabs/Murf)
        ↓
Reconstruct Audio (pydub)
        ↓
Apply Lip-Sync (Wav2Lip - optional)
        ↓
Merge Video (FFmpeg)
        ↓
Save Results
        ↓
Update Status → Complete
```

### Status Polling Flow

```
Client polls status endpoint
        ↓
FastAPI queries Celery result
        ↓
Return current status/progress
        ↓
Client waits and retries
        ↓
On completion → Download result
```

## Component Dependencies

```
FastAPI Application
  ├─ Celery (task queue)
  │   └─ Redis (broker)
  │
  ├─ Pipeline Orchestrator
  │   ├─ WhisperX Transcriber
  │   │   └─ PyTorch, WhisperX
  │   │
  │   ├─ Speaker Diarizer
  │   │   └─ pyannote.audio, PyTorch
  │   │
  │   ├─ Emotion Detector
  │   │   └─ SpeechBrain, PyTorch
  │   │
  │   ├─ NLLB Translator
  │   │   └─ Transformers, PyTorch
  │   │
  │   ├─ TTS Clients
  │   │   ├─ ElevenLabs API
  │   │   └─ Murf API
  │   │
  │   ├─ Wav2Lip Syncer
  │   │   └─ Wav2Lip, PyTorch, OpenCV
  │   │
  │   └─ Audio Reconstructor
  │       └─ pydub, FFmpeg
  │
  └─ Validation Tools
      └─ OpenCV, pydub
```

## Deployment Architecture

### Local Development

```
┌────────────────┐
│   Developer    │
│   Machine      │
│                │
│  ┌──────────┐  │
│  │ Backend  │  │
│  │  :8000   │  │
│  └──────────┘  │
│  ┌──────────┐  │
│  │ Celery   │  │
│  │  Worker  │  │
│  └──────────┘  │
│  ┌──────────┐  │
│  │ Frontend │  │
│  │  :5173   │  │
│  └──────────┘  │
│  ┌──────────┐  │
│  │  Redis   │  │
│  │  :6379   │  │
│  └──────────┘  │
└────────────────┘
```

### Docker Compose

```
┌─────────────────────────────────────────┐
│          Docker Network                  │
│                                         │
│  ┌─────────┐  ┌─────────┐             │
│  │ Backend │  │ Celery  │             │
│  │ :8000   │  │ Worker  │             │
│  └────┬────┘  └────┬────┘             │
│       │            │                   │
│  ┌────▼────────────▼────┐             │
│  │      Redis           │             │
│  │      :6379           │             │
│  └─────────────────────┘             │
│                                         │
│  ┌─────────┐                          │
│  │Frontend │                          │
│  │ :5173   │                          │
│  └─────────┘                          │
└─────────────────────────────────────────┘
```

### Production (Kubernetes)

```
┌──────────────────────────────────────────────────────────┐
│                    Load Balancer                         │
└────────────────────────┬─────────────────────────────────┘
                         │
         ┌───────────────┴───────────────┐
         ▼                               ▼
┌─────────────────┐            ┌─────────────────┐
│  Backend Pod 1  │            │  Backend Pod 2  │
│  (FastAPI)      │            │  (FastAPI)      │
└─────────────────┘            └─────────────────┘
         │                               │
         └───────────────┬───────────────┘
                         ▼
              ┌────────────────────┐
              │   Redis Cluster    │
              └────────────────────┘
                         │
         ┌───────────────┴───────────────┐
         ▼                               ▼
┌─────────────────┐            ┌─────────────────┐
│  Celery Worker  │            │  Celery Worker  │
│  Pod 1          │            │  Pod 2          │
└─────────────────┘            └─────────────────┘
```

## Security Architecture

```
User Request
     ↓
[API Gateway]
     ↓
[Authentication] (Future)
     ↓
[Rate Limiting] (Future)
     ↓
[Input Validation]
     ↓
[CORS Policy]
     ↓
[File Validation]
     ↓
Process Request
```

## Monitoring & Logging

```
Application
     ↓
[Log Collection]
     ├─ FastAPI logs
     ├─ Celery logs
     └─ Pipeline logs
     ↓
[Log Aggregation] (Future)
     ├─ ELK Stack
     └─ CloudWatch
     ↓
[Alerting] (Future)
     ├─ Slack
     └─ Email
```

## Scalability Strategy

### Horizontal Scaling

- Add more Celery workers
- Add more API instances
- Distributed Redis cluster

### Vertical Scaling

- Increase worker concurrency
- Larger instance types
- GPU acceleration

### Performance Optimization

- Model caching
- Result caching
- CDN for static assets
- Database for job metadata (future)

---

**Last Updated:** October 5, 2025

