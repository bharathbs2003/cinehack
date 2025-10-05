"""
Celery tasks for asynchronous video dubbing pipeline.
"""
from celery import Task
from .celery_config import celery_app
from .pipeline import DubbingPipeline
import os
import traceback
import json


class CallbackTask(Task):
    """Base task with callbacks for progress tracking."""
    
    def on_success(self, retval, task_id, args, kwargs):
        """Called when task succeeds."""
        print(f"✅ Task {task_id} completed successfully")
        
    def on_failure(self, exc, task_id, args, kwargs, einfo):
        """Called when task fails."""
        print(f"❌ Task {task_id} failed: {exc}")
        
    def on_retry(self, exc, task_id, args, kwargs, einfo):
        """Called when task is retried."""
        print(f"🔄 Task {task_id} retrying: {exc}")


@celery_app.task(base=CallbackTask, bind=True, name="dubbing.process_video")
def process_video_dubbing(
    self,
    video_path: str,
    target_language: str,
    source_language: str = "en",
    output_dir: str = "output",
    use_whisperx: bool = True,
    use_diarization: bool = True,
    use_emotion: bool = True,
    use_elevenlabs: bool = False,
    use_wav2lip: bool = True,
    min_speakers: int = None,
    max_speakers: int = None
):
    """
    Process video dubbing with full pipeline.
    
    Args:
        video_path: Path to input video
        target_language: Target language code (e.g., 'hi', 'es', 'fr')
        source_language: Source language code (default: 'en')
        output_dir: Directory for output files
        use_whisperx: Use WhisperX for transcription
        use_diarization: Use speaker diarization
        use_emotion: Use emotion detection
        use_elevenlabs: Use ElevenLabs TTS (requires API key)
        use_wav2lip: Use Wav2Lip for lip-sync
        min_speakers: Minimum number of speakers for diarization
        max_speakers: Maximum number of speakers for diarization
        
    Returns:
        Dictionary with results and paths
    """
    try:
        # Update task state
        self.update_state(
            state="PROCESSING",
            meta={"stage": "initializing", "progress": 0}
        )
        
        # Initialize pipeline
        pipeline = DubbingPipeline(
            use_whisperx=use_whisperx,
            use_diarization=use_diarization,
            use_emotion=use_emotion,
            use_elevenlabs=use_elevenlabs,
            use_wav2lip=use_wav2lip
        )
        
        # Progress callback
        def progress_callback(stage: str, progress: int, message: str = ""):
            self.update_state(
                state="PROCESSING",
                meta={
                    "stage": stage,
                    "progress": progress,
                    "message": message
                }
            )
            
        # Run pipeline
        result = pipeline.process(
            video_path=video_path,
            target_language=target_language,
            source_language=source_language,
            output_dir=output_dir,
            min_speakers=min_speakers,
            max_speakers=max_speakers,
            progress_callback=progress_callback
        )
        
        # Save transcript JSON
        transcript_path = os.path.join(output_dir, "transcript.json")
        with open(transcript_path, "w", encoding="utf-8") as f:
            json.dump(result["transcript"], f, ensure_ascii=False, indent=2)
            
        result["transcript_path"] = transcript_path
        
        return result
        
    except Exception as e:
        error_msg = f"Pipeline error: {str(e)}\n{traceback.format_exc()}"
        print(f"❌ {error_msg}")
        
        self.update_state(
            state="FAILURE",
            meta={"error": str(e), "traceback": traceback.format_exc()}
        )
        
        raise


@celery_app.task(name="dubbing.cleanup_old_files")
def cleanup_old_files(directory: str, days_old: int = 7):
    """
    Clean up old temporary files.
    
    Args:
        directory: Directory to clean
        days_old: Delete files older than this many days
    """
    import time
    from pathlib import Path
    
    try:
        cutoff_time = time.time() - (days_old * 86400)
        deleted_count = 0
        
        for file_path in Path(directory).rglob("*"):
            if file_path.is_file():
                if file_path.stat().st_mtime < cutoff_time:
                    file_path.unlink()
                    deleted_count += 1
                    
        print(f"🧹 Cleaned up {deleted_count} old files from {directory}")
        
        return {"deleted_count": deleted_count}
        
    except Exception as e:
        print(f"⚠️ Cleanup error: {e}")
        return {"error": str(e)}

