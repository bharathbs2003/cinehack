"""
Simple video dubbing processor using API services.
Uses Groq for transcription (FREE), OpenAI for translation, and Murf for TTS.
"""
import os
import subprocess
import openai
import requests
from pathlib import Path
from groq import Groq
from .config import settings

# Initialize APIs
openai.api_key = settings.OPENAI_API_KEY
groq_client = Groq(api_key=settings.GROQ_API_KEY) if settings.GROQ_API_KEY else None

# Murf API constants
MURF_API_BASE = "https://api.murf.ai/v1/speech"
MURF_API_KEY = settings.MURF_API_KEY


def update_job_status(jobs_dict, job_id, status, progress, stage, message):
    """Update job status in the jobs dictionary."""
    if job_id in jobs_dict:
        jobs_dict[job_id].update({
            "status": status,
            "progress": progress,
            "stage": stage,
            "message": message
        })


def extract_audio(video_path, output_path):
    """Extract audio from video using FFmpeg."""
    try:
        print(f"Extracting audio from: {video_path}")
        print(f"Output audio to: {output_path}")
        
        cmd = [
            "ffmpeg",
            "-y",
            "-i", video_path,
            "-vn",
            "-acodec", "pcm_s16le",
            "-ar", "16000",
            "-ac", "1",
            output_path
        ]
        
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        
        # Verify output file was created
        if os.path.exists(output_path):
            file_size = os.path.getsize(output_path)
            print(f"Audio extracted successfully. Size: {file_size / 1024:.2f} KB")
            return True
        else:
            print(f"ERROR: Audio file was not created")
            return False
            
    except subprocess.CalledProcessError as e:
        print(f"FFmpeg error: {e}")
        print(f"FFmpeg stderr: {e.stderr}")
        return False
    except Exception as e:
        print(f"Audio extraction error: {type(e).__name__}: {e}")
        return False


def transcribe_audio(audio_path):
    """Transcribe audio using Groq Whisper API (FREE and FAST)."""
    try:
        # Check if file exists and has content
        if not os.path.exists(audio_path):
            print(f"ERROR: Audio file not found: {audio_path}")
            return None
        
        file_size = os.path.getsize(audio_path)
        print(f"Audio file size: {file_size / 1024:.2f} KB")
        
        if file_size == 0:
            print(f"ERROR: Audio file is empty")
            return None
        
        # Groq Whisper has a 25MB limit
        if file_size > 25 * 1024 * 1024:
            print(f"ERROR: Audio file too large ({file_size / 1024 / 1024:.2f} MB). Max is 25 MB.")
            return None
        
        print(f"Opening audio file: {audio_path}")
        
        # Use Groq if available (FREE and faster), fallback to OpenAI
        if groq_client:
            print(f"Calling Groq Whisper API (FREE)...")
            with open(audio_path, "rb") as audio_file:
                transcription = groq_client.audio.transcriptions.create(
                    file=audio_file,
                    model="whisper-large-v3",
                    response_format="text",
                    temperature=0.0
                )
            transcript = transcription if isinstance(transcription, str) else transcription.text
        else:
            print(f"Calling OpenAI Whisper API...")
            with open(audio_path, "rb") as audio_file:
                transcript = openai.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_file,
                    response_format="text"
                )
        
        print(f"Transcription successful. Length: {len(transcript)} characters")
        return transcript
    except Exception as e:
        print(f"Transcription error: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return None


def translate_text(text, target_language):
    """Translate text using OpenAI."""
    try:
        lang_names = {
            "hi": "Hindi",
            "es": "Spanish",
            "fr": "French",
            "de": "German",
            "zh": "Chinese",
            "ja": "Japanese",
            "ko": "Korean",
            "ar": "Arabic",
            "pt": "Portuguese",
            "ru": "Russian",
            "it": "Italian",
            "mr": "Marathi",
            "bn": "Bengali",
            "ta": "Tamil",
            "te": "Telugu",
            "en": "English"
        }
        
        target_lang_name = lang_names.get(target_language, target_language)
        
        response = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": f"You are a professional translator. Translate the following text to {target_lang_name}. Preserve the tone and style. Return only the translation."},
                {"role": "user", "content": text}
            ],
            max_tokens=2000
        )
        
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"Translation error: {e}")
        return text


def list_murf_voices():
    """Get available voices from Murf."""
    try:
        url = f"{MURF_API_BASE}/voices"
        response = requests.get(url, headers={"api-key": MURF_API_KEY})
        response.raise_for_status()
        data = response.json()
        voices = data.get("voices") if isinstance(data, dict) else data
        return voices or []
    except Exception as e:
        print(f"Error listing voices: {e}")
        return []


def generate_voice(text, voice_id, output_path):
    """Generate voice using Murf API (direct API call)."""
    try:
        url = f"{MURF_API_BASE}/generate"
        payload = {
            "voiceId": voice_id,
            "text": text,
            "format": "mp3"
        }
        headers = {
            "api-key": MURF_API_KEY,
            "Content-Type": "application/json"
        }
        
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        result = response.json()
        
        # Get audio URL
        audio_url = result.get("audioFile") or result.get("data", {}).get("audioFile")
        if not audio_url:
            print(f"No audio URL in response: {result}")
            return False
        
        # Download audio
        audio_response = requests.get(audio_url)
        audio_response.raise_for_status()
        
        with open(output_path, "wb") as f:
            f.write(audio_response.content)
        
        return os.path.exists(output_path)
        
    except Exception as e:
        print(f"Voice generation error: {e}")
        return False


def merge_audio_video(video_path, audio_path, output_path):
    """Merge dubbed audio with original video."""
    try:
        cmd = [
            "ffmpeg",
            "-y",
            "-i", video_path,
            "-i", audio_path,
            "-c:v", "copy",
            "-c:a", "aac",
            "-map", "0:v:0",
            "-map", "1:a:0",
            "-shortest",
            output_path
        ]
        subprocess.run(cmd, check=True, capture_output=True)
        return True
    except Exception as e:
        print(f"Video merge error: {e}")
        return False


def process_video_simple(job_id, video_path, target_language, source_language, jobs_dict):
    """
    Simple video processing pipeline.
    
    Steps:
    1. Extract audio
    2. Transcribe with OpenAI Whisper
    3. Translate with OpenAI
    4. Generate voice with Murf
    5. Merge audio back to video
    """
    try:
        # Update status: Starting
        update_job_status(jobs_dict, job_id, "processing", 5, "init", "Initializing processing...")
        
        # Setup paths
        job_dir = Path(video_path).parent
        audio_path = job_dir / "extracted_audio.wav"
        dubbed_audio_path = job_dir / "dubbed_audio.mp3"
        output_video_path = job_dir / f"final_dubbed_{job_id}.mp4"
        
        # Step 1: Extract audio
        update_job_status(jobs_dict, job_id, "processing", 15, "extract_audio", "Extracting audio from video...")
        print(f"[{job_id}] Extracting audio...")
        if not extract_audio(video_path, str(audio_path)):
            raise Exception("Failed to extract audio")
        
        # Step 2: Transcribe
        update_job_status(jobs_dict, job_id, "processing", 30, "transcribe", "Transcribing audio...")
        print(f"[{job_id}] Transcribing audio...")
        transcript = transcribe_audio(str(audio_path))
        if not transcript:
            raise Exception("Failed to transcribe audio")
        
        print(f"[{job_id}] Transcript: {transcript[:100]}...")
        
        # Step 3: Translate
        update_job_status(jobs_dict, job_id, "processing", 50, "translate", f"Translating to {target_language}...")
        print(f"[{job_id}] Translating...")
        translated_text = translate_text(transcript, target_language)
        print(f"[{job_id}] Translation: {translated_text[:100]}...")
        
        # Step 4: Generate voice
        update_job_status(jobs_dict, job_id, "processing", 70, "voice_generation", "Generating dubbed voice...")
        print(f"[{job_id}] Generating voice...")
        
        # Get available voices and pick one
        voices = list_murf_voices()
        if not voices:
            raise Exception("No voices available from Murf")
        
        # Pick a suitable voice (first available for now)
        voice_id = voices[0].get("voiceId") or voices[0].get("id")
        print(f"[{job_id}] Using voice: {voice_id}")
        
        if not generate_voice(translated_text, voice_id, str(dubbed_audio_path)):
            raise Exception("Failed to generate voice")
        
        # Step 5: Merge audio back
        update_job_status(jobs_dict, job_id, "processing", 85, "merge", "Merging audio with video...")
        print(f"[{job_id}] Merging audio and video...")
        if not merge_audio_video(video_path, str(dubbed_audio_path), str(output_video_path)):
            raise Exception("Failed to merge audio and video")
        
        # Done!
        update_job_status(jobs_dict, job_id, "done", 100, "complete", "Dubbing complete!")
        jobs_dict[job_id]["result_path"] = str(output_video_path)
        
        print(f"[{job_id}] SUCCESS - Processing complete! Output: {output_video_path}")
        
        # Cleanup intermediate files
        try:
            if audio_path.exists():
                audio_path.unlink()
        except:
            pass
        
        return True
        
    except Exception as e:
        error_msg = f"Processing failed: {str(e)}"
        print(f"[{job_id}] ERROR - {error_msg}")
        update_job_status(jobs_dict, job_id, "error", 0, "error", error_msg)
        return False

