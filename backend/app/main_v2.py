"""
Updated FastAPI application with Celery integration and advanced pipeline.
"""
import os
import uuid
import shutil
from pathlib import Path
from fastapi import FastAPI, UploadFile, Form, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from celery.result import AsyncResult

from .config import settings
from .celery_config import celery_app
from .tasks import process_video_dubbing

app = FastAPI(
    title="EduDub AI - Advanced Video Dubbing Platform",
    description="Production-ready multilingual AI dubbing with emotion preservation and lip-sync",
    version="2.0.0"
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Ensure directories exist
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
os.makedirs(settings.OUTPUT_DIR, exist_ok=True)


@app.get("/")
async def root():
    """API root endpoint."""
    return {
        "message": "EduDub AI - Advanced Video Dubbing Platform",
        "version": "2.0.0",
        "features": [
            "WhisperX transcription with word-level timestamps",
            "Speaker diarization (pyannote)",
            "Emotion detection (SpeechBrain)",
            "High-quality translation (NLLB-200)",
            "Emotion-aware TTS (ElevenLabs/Murf)",
            "Lip-sync with Wav2Lip",
            "Async processing with Celery"
        ],
        "status": "ready"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "celery_active": celery_app.control.inspect().active() is not None
    }


@app.post("/api/v2/dub")
async def create_dubbing_job(
    file: UploadFile,
    target_language: str = Form("hi"),
    source_language: str = Form("en"),
    use_whisperx: bool = Form(True),
    use_diarization: bool = Form(True),
    use_emotion: bool = Form(True),
    use_elevenlabs: bool = Form(False),
    use_wav2lip: bool = Form(False),
    min_speakers: int = Form(None),
    max_speakers: int = Form(None)
):
    """
    Create a new video dubbing job.
    
    Args:
        file: Video file to dub
        target_language: Target language code (hi, es, fr, de, etc.)
        source_language: Source language code (default: en)
        use_whisperx: Use WhisperX for better transcription
        use_diarization: Enable speaker diarization
        use_emotion: Enable emotion detection
        use_elevenlabs: Use ElevenLabs TTS (requires API key)
        use_wav2lip: Enable lip-sync (requires Wav2Lip setup)
        min_speakers: Minimum speakers for diarization
        max_speakers: Maximum speakers for diarization
        
    Returns:
        Job ID and status
    """
    try:
        # Validate file
        if not file.content_type.startswith("video/"):
            raise HTTPException(status_code=400, detail="File must be a video")
            
        # Save uploaded file
        job_id = str(uuid.uuid4())
        upload_dir = os.path.join(settings.UPLOAD_DIR, job_id)
        os.makedirs(upload_dir, exist_ok=True)
        
        file_extension = Path(file.filename).suffix
        video_path = os.path.join(upload_dir, f"input{file_extension}")
        
        with open(video_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        # Create output directory
        output_dir = os.path.join(settings.OUTPUT_DIR, job_id)
        os.makedirs(output_dir, exist_ok=True)
        
        # Submit Celery task
        task = process_video_dubbing.apply_async(
            args=[],
            kwargs={
                "video_path": video_path,
                "target_language": target_language,
                "source_language": source_language,
                "output_dir": output_dir,
                "use_whisperx": use_whisperx,
                "use_diarization": use_diarization,
                "use_emotion": use_emotion,
                "use_elevenlabs": use_elevenlabs,
                "use_wav2lip": use_wav2lip,
                "min_speakers": min_speakers,
                "max_speakers": max_speakers
            }
        )
        
        return {
            "job_id": job_id,
            "task_id": task.id,
            "status": "queued",
            "message": "Video dubbing job created successfully"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating job: {str(e)}")


@app.get("/api/v2/status/{job_id}")
async def get_job_status(job_id: str, task_id: str = None):
    """
    Get status of a dubbing job.
    
    Args:
        job_id: Job identifier
        task_id: Optional Celery task ID
        
    Returns:
        Job status and progress
    """
    try:
        if not task_id:
            # Try to find task_id from job_id (simplified, in production use database)
            return {
                "job_id": job_id,
                "status": "unknown",
                "message": "task_id required for status check"
            }
            
        # Get Celery task result
        task_result = AsyncResult(task_id, app=celery_app)
        
        response = {
            "job_id": job_id,
            "task_id": task_id,
            "status": task_result.state.lower(),
        }
        
        if task_result.state == "PENDING":
            response["message"] = "Task is waiting to be processed"
        elif task_result.state == "PROCESSING":
            response["progress"] = task_result.info.get("progress", 0)
            response["stage"] = task_result.info.get("stage", "processing")
            response["message"] = task_result.info.get("message", "Processing...")
        elif task_result.state == "SUCCESS":
            response["message"] = "Dubbing completed successfully"
            response["result"] = task_result.result
        elif task_result.state == "FAILURE":
            response["message"] = "Dubbing failed"
            response["error"] = str(task_result.info)
            
        return response
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error checking status: {str(e)}")


@app.get("/api/v2/result/{job_id}")
async def get_job_result(job_id: str):
    """
    Get result files for a completed job.
    
    Args:
        job_id: Job identifier
        
    Returns:
        Final dubbed video file
    """
    try:
        output_dir = os.path.join(settings.OUTPUT_DIR, job_id)
        
        if not os.path.exists(output_dir):
            raise HTTPException(status_code=404, detail="Job not found")
            
        # Find final video
        video_files = list(Path(output_dir).glob("final_dubbed_*.mp4"))
        
        if not video_files:
            raise HTTPException(status_code=404, detail="Final video not found. Job may not be complete.")
            
        video_path = str(video_files[0])
        
        return FileResponse(
            video_path,
            media_type="video/mp4",
            filename=f"dubbed_{job_id}.mp4"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving result: {str(e)}")


@app.get("/api/v2/transcript/{job_id}")
async def get_transcript(job_id: str):
    """
    Get transcript JSON for a job.
    
    Args:
        job_id: Job identifier
        
    Returns:
        Transcript with timestamps, speakers, emotions, and translations
    """
    try:
        output_dir = os.path.join(settings.OUTPUT_DIR, job_id)
        transcript_path = os.path.join(output_dir, "transcript.json")
        
        if not os.path.exists(transcript_path):
            raise HTTPException(status_code=404, detail="Transcript not found")
            
        return FileResponse(
            transcript_path,
            media_type="application/json",
            filename=f"transcript_{job_id}.json"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving transcript: {str(e)}")


@app.delete("/api/v2/job/{job_id}")
async def delete_job(job_id: str):
    """
    Delete job files.
    
    Args:
        job_id: Job identifier
        
    Returns:
        Deletion status
    """
    try:
        upload_dir = os.path.join(settings.UPLOAD_DIR, job_id)
        output_dir = os.path.join(settings.OUTPUT_DIR, job_id)
        
        deleted_items = []
        
        if os.path.exists(upload_dir):
            shutil.rmtree(upload_dir)
            deleted_items.append("upload_dir")
            
        if os.path.exists(output_dir):
            shutil.rmtree(output_dir)
            deleted_items.append("output_dir")
            
        return {
            "job_id": job_id,
            "status": "deleted",
            "deleted_items": deleted_items
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting job: {str(e)}")


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


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.app.main_v2:app", host=settings.HOST, port=settings.PORT, reload=True)

