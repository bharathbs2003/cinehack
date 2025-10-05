"""
Simplified EduDub AI FastAPI application - No Celery/Redis required
Perfect for local testing with API-based services
"""
import os
import uuid
import shutil
import threading
from pathlib import Path
from fastapi import FastAPI, UploadFile, Form, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from .config import settings
from .simple_processor import process_video_simple
from .advanced_processor import process_video_advanced

# Create FastAPI app
app = FastAPI(
    title="EduDub AI - Local Version",
    description="Simple video dubbing with OpenAI + ElevenLabs/Murf",
    version="2.0.0-local"
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Ensure directories exist
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
os.makedirs(settings.OUTPUT_DIR, exist_ok=True)

# Simple in-memory job storage
JOBS = {}


@app.get("/")
async def root():
    """API root endpoint."""
    return {
        "message": "EduDub AI - Local Version",
        "version": "2.0.0-local",
        "status": "ready",
        "features": [
            "Video upload",
            "OpenAI Transcription",
            "OpenAI Translation",
            "Murf/ElevenLabs TTS",
            "16+ Languages"
        ],
        "note": "Using API-based services (no local ML models)"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "mode": "local"}


@app.post("/api/v1/dub")
@app.post("/api/v2/dub")
async def create_simple_dub(
    file: UploadFile,
    target_language: str = Form("hi"),
    source_language: str = Form("en"),
    use_whisperx: bool = Form(True),
    use_diarization: bool = Form(True),
    use_emotion: bool = Form(True),
    use_elevenlabs: bool = Form(False),
    use_wav2lip: bool = Form(False),
    advanced_mode: bool = Form(True)  # NEW: Use advanced processing by default
):
    """
    Video dubbing endpoint with simple and advanced modes.
    Advanced mode (default): Proper timing, speaker handling, background audio.
    Simple mode: Fast but basic dubbing.
    """
    try:
        # Save uploaded file
        job_id = str(uuid.uuid4())[:8]
        upload_dir = os.path.join(settings.UPLOAD_DIR, job_id)
        os.makedirs(upload_dir, exist_ok=True)
        
        file_extension = Path(file.filename).suffix
        video_path = os.path.join(upload_dir, f"input{file_extension}")
        
        with open(video_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Store job info
        JOBS[job_id] = {
            "status": "queued",
            "progress": 0,
            "stage": "queued",
            "video_path": video_path,
            "target_language": target_language,
            "source_language": source_language,
            "message": "Video uploaded successfully. Processing will start shortly.",
            "options": {
                "use_whisperx": use_whisperx,
                "use_diarization": use_diarization,
                "use_emotion": use_emotion,
                "use_elevenlabs": use_elevenlabs,
                "use_wav2lip": use_wav2lip
            }
        }
        
        # Start processing in background thread
        if advanced_mode:
            print(f"[{job_id}] Starting ADVANCED background processing...")
            print(f"[{job_id}]   Features: Proper timing, multi-speaker, background audio")
            processing_func = process_video_advanced
        else:
            print(f"[{job_id}] Starting SIMPLE background processing...")
            processing_func = process_video_simple
        
        processing_thread = threading.Thread(
            target=processing_func,
            args=(job_id, video_path, target_language, source_language, JOBS),
            daemon=True
        )
        processing_thread.start()
        
        return {
            "job_id": job_id,
            "task_id": job_id,
            "status": "queued",
            "message": "Video uploaded successfully! Processing started."
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload error: {str(e)}")


@app.get("/api/v1/status/{job_id}")
@app.get("/api/v2/status/{job_id}")
async def get_job_status(job_id: str, task_id: str = None):
    """Get job status (v1 and v2 compatible)."""
    if job_id not in JOBS:
        raise HTTPException(status_code=404, detail="Job not found")
    
    job_data = JOBS[job_id]
    
    # Map status to frontend expected values
    status = job_data.get("status", "unknown")
    if status == "done":
        status = "success"  # Frontend expects "success" for completed jobs
    
    # Return v2-compatible response
    return {
        "job_id": job_id,
        "task_id": task_id or job_id,
        "status": status,
        "progress": job_data.get("progress", 0),
        "stage": job_data.get("stage", "queued"),
        "message": job_data.get("message", "Processing..."),
        "result": job_data.get("result_path") if status == "success" else None
    }


@app.get("/api/v2/result/{job_id}")
async def get_job_result(job_id: str):
    """Get job result (download video)."""
    if job_id not in JOBS:
        raise HTTPException(status_code=404, detail="Job not found")
    
    job_data = JOBS[job_id]
    
    if job_data.get("status") != "done":
        raise HTTPException(
            status_code=400, 
            detail=f"Job not complete yet. Current status: {job_data.get('status')}"
        )
    
    # Return the result file if it exists
    result_path = job_data.get("result_path")
    if result_path and os.path.exists(result_path):
        return FileResponse(
            result_path,
            media_type="video/mp4",
            filename=f"dubbed_{job_id}.mp4"
        )
    else:
        raise HTTPException(status_code=404, detail="Result file not found")


@app.get("/api/v2/transcript/{job_id}")
async def get_job_transcript(job_id: str):
    """Get job transcript JSON."""
    if job_id not in JOBS:
        raise HTTPException(status_code=404, detail="Job not found")
    
    # For now, return a placeholder
    return {
        "job_id": job_id,
        "segments": [],
        "message": "Transcript generation will be available once processing is implemented"
    }


@app.get("/api/languages")
async def get_supported_languages():
    """Get list of supported languages."""
    return {
        "languages": [
            {"code": "en", "name": "English"},
            {"code": "hi", "name": "Hindi"},
            {"code": "es", "name": "Spanish"},
            {"code": "fr", "name": "French"},
            {"code": "de", "name": "German"},
            {"code": "zh", "name": "Chinese"},
            {"code": "ja", "name": "Japanese"},
            {"code": "ko", "name": "Korean"},
            {"code": "ar", "name": "Arabic"},
            {"code": "pt", "name": "Portuguese"},
            {"code": "ru", "name": "Russian"},
            {"code": "it", "name": "Italian"},
            {"code": "mr", "name": "Marathi"},
            {"code": "bn", "name": "Bengali"},
            {"code": "ta", "name": "Tamil"},
            {"code": "te", "name": "Telugu"}
        ]
    }


@app.get("/api/test")
async def test_api_keys():
    """Test if API keys are configured."""
    keys_status = {
        "MURF_API_KEY": "✅ Configured" if settings.MURF_API_KEY else "❌ Missing",
        "OPENAI_API_KEY": "✅ Configured" if settings.OPENAI_API_KEY else "❌ Missing",
        "ELEVENLABS_API_KEY": "✅ Configured" if settings.ELEVENLABS_API_KEY else "❌ Missing",
        "HUGGINGFACE_TOKEN": "✅ Configured" if settings.HUGGINGFACE_TOKEN else "❌ Missing"
    }
    
    return {
        "api_keys": keys_status,
        "all_ready": all("✅" in v for v in keys_status.values()),
        "note": "All keys configured!" if all("✅" in v for v in keys_status.values()) else "Some keys are missing"
    }


if __name__ == "__main__":
    import uvicorn
    print("=" * 60)
    print("Starting EduDub AI - Local Version")
    print("=" * 60)
    print(f"Backend API: http://{settings.HOST}:{settings.PORT}")
    print(f"API Docs: http://{settings.HOST}:{settings.PORT}/docs")
    print("=" * 60)
    uvicorn.run(app, host=settings.HOST, port=settings.PORT)

