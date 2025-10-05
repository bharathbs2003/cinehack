"""
Advanced video dubbing processor with:
- Speaker diarization (identify different speakers)
- Word-level timestamps (accurate timing)
- Voice gender detection and matching
- Background audio preservation
- Timing-accurate audio reconstruction
- Indian voice character mapping
"""
import os
import json
import subprocess
import requests
from pathlib import Path
from groq import Groq
import openai
from .config import settings
from .speaker_diarization import process_speaker_diarization, refine_speaker_segments_with_words
from .speaker_voices import assign_voices_to_speakers, print_indian_voices_summary

# Initialize APIs
openai.api_key = settings.OPENAI_API_KEY
groq_client = Groq(api_key=settings.GROQ_API_KEY) if settings.GROQ_API_KEY else None

# Murf API constants
MURF_API_BASE = "https://api.murf.ai/v1"
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


def extract_audio_with_background(video_path, speech_path, background_path):
    """
    Extract audio and separate speech from background.
    Uses ffmpeg to extract full audio, then we'll separate later.
    """
    try:
        print(f"Extracting audio from: {video_path}")
        
        # Extract full audio (for background preservation)
        cmd_full = [
            "ffmpeg", "-y",
            "-i", video_path,
            "-vn",
            "-acodec", "pcm_s16le",
            "-ar", "44100",
            "-ac", "2",
            background_path
        ]
        subprocess.run(cmd_full, check=True, capture_output=True, text=True)
        
        # Extract mono audio for speech (better for transcription)
        cmd_speech = [
            "ffmpeg", "-y",
            "-i", video_path,
            "-vn",
            "-acodec", "pcm_s16le",
            "-ar", "16000",
            "-ac", "1",
            speech_path
        ]
        subprocess.run(cmd_speech, check=True, capture_output=True, text=True)
        
        if os.path.exists(speech_path):
            file_size = os.path.getsize(speech_path)
            print(f"Audio extracted. Speech: {file_size / 1024:.2f} KB")
            return True
        return False
            
    except subprocess.CalledProcessError as e:
        print(f"FFmpeg error: {e}")
        print(f"FFmpeg stderr: {e.stderr}")
        return False
    except Exception as e:
        print(f"Audio extraction error: {type(e).__name__}: {e}")
        return False


def transcribe_with_timestamps(audio_path):
    """
    Transcribe audio with word-level timestamps using Groq.
    Returns segments with start/end times for each word.
    """
    try:
        if not os.path.exists(audio_path):
            print(f"ERROR: Audio file not found: {audio_path}")
            return None
        
        file_size = os.path.getsize(audio_path)
        print(f"Audio file size: {file_size / 1024:.2f} KB")
        
        if file_size == 0 or file_size > 25 * 1024 * 1024:
            print(f"ERROR: Audio file invalid size")
            return None
        
        print(f"Calling Groq Whisper with timestamps...")
        
        # Use verbose_json to get word-level timestamps
        with open(audio_path, "rb") as audio_file:
            transcription = groq_client.audio.transcriptions.create(
                file=audio_file,
                model="whisper-large-v3",
                response_format="verbose_json",
                temperature=0.0
            )
        
        # Parse the response
        result = {
            "text": transcription.text,
            "segments": [],
            "words": []
        }
        
        # Extract segments with timestamps
        if hasattr(transcription, 'segments'):
            for segment in transcription.segments:
                seg_data = {
                    "start": segment.get('start', 0),
                    "end": segment.get('end', 0),
                    "text": segment.get('text', ''),
                    "words": []
                }
                
                # Extract word-level timestamps if available
                if 'words' in segment:
                    for word in segment['words']:
                        seg_data["words"].append({
                            "word": word.get('word', ''),
                            "start": word.get('start', 0),
                            "end": word.get('end', 0)
                        })
                        result["words"].append({
                            "word": word.get('word', ''),
                            "start": word.get('start', 0),
                            "end": word.get('end', 0)
                        })
                
                result["segments"].append(seg_data)
        
        print(f"Transcription complete: {len(result['segments'])} segments, {len(result['words'])} words")
        return result
        
    except Exception as e:
        print(f"Transcription error: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return None


def detect_speaker_gender(audio_path, segment_start, segment_end):
    """
    Detect speaker gender from audio segment.
    Simple heuristic: analyze pitch/frequency.
    Returns: 'male', 'female', or 'neutral'
    """
    try:
        # Extract segment
        temp_segment = audio_path.replace('.wav', f'_temp_{segment_start}.wav')
        
        cmd = [
            "ffmpeg", "-y",
            "-i", audio_path,
            "-ss", str(segment_start),
            "-to", str(segment_end),
            "-acodec", "pcm_s16le",
            temp_segment
        ]
        subprocess.run(cmd, check=True, capture_output=True)
        
        # Analyze pitch using ffmpeg stats
        cmd_stats = [
            "ffmpeg",
            "-i", temp_segment,
            "-af", "astats=metadata=1:reset=1",
            "-f", "null",
            "-"
        ]
        result = subprocess.run(cmd_stats, capture_output=True, text=True)
        
        # Simple heuristic: check for keywords or default to neutral
        # In production, you'd use a proper gender detection model
        # For now, we'll return neutral and let user specify
        
        # Cleanup
        if os.path.exists(temp_segment):
            os.remove(temp_segment)
        
        # Default to neutral for now
        # In production: use ML model or API for gender detection
        return 'neutral'
        
    except Exception as e:
        print(f"Gender detection error: {e}")
        return 'neutral'


def get_murf_voices_by_language_gender(language_code, gender='neutral'):
    """
    Get appropriate Murf voices for language and gender.
    """
    try:
        url = f"{MURF_API_BASE}/speech/voices"
        headers = {"api-key": MURF_API_KEY}
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        all_voices = response.json()
        voices = all_voices.get("voices", []) if isinstance(all_voices, dict) else all_voices
        
        # Map language codes
        lang_map = {
            'en': 'english', 'es': 'spanish', 'fr': 'french', 'de': 'german',
            'it': 'italian', 'pt': 'portuguese', 'hi': 'hindi', 'zh': 'chinese',
            'ja': 'japanese', 'ko': 'korean', 'ar': 'arabic', 'ru': 'russian'
        }
        
        target_lang = lang_map.get(language_code, 'english')
        
        # Filter by language and gender
        filtered_voices = []
        for voice in voices:
            voice_lang = voice.get('languageName', '').lower()
            voice_gender = voice.get('gender', '').lower()
            
            if target_lang in voice_lang:
                if gender == 'neutral' or gender in voice_gender:
                    filtered_voices.append(voice)
        
        print(f"Found {len(filtered_voices)} {gender} voices for {language_code}")
        return filtered_voices if filtered_voices else voices[:5]
        
    except Exception as e:
        print(f"Error fetching voices: {e}")
        return []


def translate_segment(text, target_language, context=""):
    """Translate text preserving timing cues."""
    try:
        lang_names = {
            "hi": "Hindi", "es": "Spanish", "fr": "French", "de": "German",
            "zh": "Chinese", "ja": "Japanese", "ko": "Korean", "ar": "Arabic",
            "pt": "Portuguese", "ru": "Russian", "it": "Italian",
            "en": "English"
        }
        
        target_lang_name = lang_names.get(target_language, target_language)
        
        system_prompt = f"""You are a professional translator for video dubbing. 
Translate to {target_lang_name} while:
1. Preserving natural speech rhythm
2. Keeping similar length to original (for lip sync)
3. Maintaining emotional tone
4. Using natural, conversational language

Return ONLY the translation, no explanations."""

        if context:
            user_content = f"Context: {context}\n\nTranslate: {text}"
        else:
            user_content = text
        
        response = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_content}
            ],
            max_tokens=500,
            temperature=0.3
        )
        
        return response.choices[0].message.content.strip()
        
    except Exception as e:
        print(f"Translation error: {e}")
        return text


def generate_voice_segment(text, voice_id, output_path, speed=1.0):
    """Generate voice for a segment with timing control."""
    try:
        url = f"{MURF_API_BASE}/speech/generate"
        payload = {
            "voiceId": voice_id,
            "text": text,
            "format": "wav",
            "speed": speed,
            "pitch": 0
        }
        headers = {
            "api-key": MURF_API_KEY,
            "Content-Type": "application/json"
        }
        
        response = requests.post(url, json=payload, headers=headers, timeout=60)
        response.raise_for_status()
        result = response.json()
        
        audio_url = result.get("audioFile") or result.get("data", {}).get("audioFile")
        if not audio_url:
            print(f"No audio URL in response")
            return False
        
        audio_response = requests.get(audio_url, timeout=30)
        audio_response.raise_for_status()
        
        with open(output_path, "wb") as f:
            f.write(audio_response.content)
        
        return os.path.exists(output_path)
        
    except Exception as e:
        print(f"Voice generation error: {e}")
        return False


def adjust_audio_duration(audio_path, target_duration, output_path):
    """
    Adjust audio duration to match original timing using speed adjustment.
    Preserves pitch while changing speed.
    """
    try:
        # Get current duration
        cmd_duration = [
            "ffprobe", "-v", "error",
            "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1",
            audio_path
        ]
        result = subprocess.run(cmd_duration, capture_output=True, text=True)
        current_duration = float(result.stdout.strip())
        
        # Calculate speed adjustment
        speed_factor = current_duration / target_duration
        
        # Limit speed adjustment to reasonable range (0.5x to 2.0x)
        speed_factor = max(0.5, min(2.0, speed_factor))
        
        print(f"Adjusting speed: {current_duration:.2f}s -> {target_duration:.2f}s (factor: {speed_factor:.2f})")
        
        # Use atempo filter (supports 0.5 to 2.0)
        cmd = [
            "ffmpeg", "-y",
            "-i", audio_path,
            "-filter:a", f"atempo={speed_factor}",
            output_path
        ]
        subprocess.run(cmd, check=True, capture_output=True)
        
        return os.path.exists(output_path)
        
    except Exception as e:
        print(f"Duration adjustment error: {e}")
        # Fallback: just copy file
        import shutil
        shutil.copy(audio_path, output_path)
        return True


def merge_audio_segments(segments_info, background_audio, output_path):
    """
    Merge dubbed segments with background audio preservation.
    segments_info: [{'audio': path, 'start': time, 'end': time}, ...]
    """
    try:
        print(f"Merging {len(segments_info)} audio segments...")
        
        # Create filter complex for mixing
        filter_parts = []
        input_files = []
        
        # Add background audio (at lower volume)
        input_files.extend(["-i", background_audio])
        filter_parts.append("[0:a]volume=0.3[bg]")
        
        # Add each segment
        for i, seg in enumerate(segments_info, 1):
            input_files.extend(["-i", seg['audio']])
            # Delay audio to correct position
            delay_ms = int(seg['start'] * 1000)
            filter_parts.append(f"[{i}:a]adelay={delay_ms}|{delay_ms}[seg{i}]")
        
        # Mix all together
        mix_inputs = "[bg]"
        for i in range(1, len(segments_info) + 1):
            mix_inputs += f"[seg{i}]"
        
        filter_parts.append(f"{mix_inputs}amix=inputs={len(segments_info) + 1}:duration=longest[out]")
        
        filter_complex = ";".join(filter_parts)
        
        # Build ffmpeg command
        cmd = [
            "ffmpeg", "-y"
        ] + input_files + [
            "-filter_complex", filter_complex,
            "-map", "[out]",
            output_path
        ]
        
        subprocess.run(cmd, check=True, capture_output=True, text=True)
        
        if os.path.exists(output_path):
            print(f"Audio merged successfully: {output_path}")
            return True
        return False
        
    except Exception as e:
        print(f"Audio merge error: {e}")
        import traceback
        traceback.print_exc()
        return False


def merge_audio_video(video_path, audio_path, output_path):
    """Merge dubbed audio with original video."""
    try:
        cmd = [
            "ffmpeg", "-y",
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


def process_video_advanced(job_id, video_path, target_language, source_language, jobs_dict):
    """
    Advanced video processing with proper speaker handling and timing.
    """
    try:
        # Initialize
        update_job_status(jobs_dict, job_id, "processing", 5, "init", "Initializing advanced processing...")
        
        job_dir = Path(video_path).parent
        speech_audio = job_dir / "speech.wav"
        background_audio = job_dir / "background.wav"
        segments_dir = job_dir / "segments"
        segments_dir.mkdir(exist_ok=True)
        
        # Step 1: Extract audio with background separation
        update_job_status(jobs_dict, job_id, "processing", 10, "extract_audio", "Extracting audio...")
        print(f"[{job_id}] Extracting audio with background...")
        
        if not extract_audio_with_background(video_path, str(speech_audio), str(background_audio)):
            raise Exception("Failed to extract audio")
        
        # Step 2: Transcribe with word-level timestamps
        update_job_status(jobs_dict, job_id, "processing", 25, "transcribe", "Transcribing with timestamps...")
        print(f"[{job_id}] Transcribing with timestamps...")
        
        transcript_data = transcribe_with_timestamps(str(speech_audio))
        if not transcript_data:
            raise Exception("Failed to transcribe audio")
        
        print(f"[{job_id}] Transcript: {transcript_data['text'][:100]}...")
        
        # Save transcript
        transcript_file = job_dir / "transcript.json"
        with open(transcript_file, 'w', encoding='utf-8') as f:
            json.dump(transcript_data, f, indent=2, ensure_ascii=False)
        
        # Step 2.5: Speaker Diarization (NEW!)
        update_job_status(jobs_dict, job_id, "processing", 30, "diarization", "Identifying speakers...")
        print(f"[{job_id}] Running speaker diarization...")
        
        speaker_segments, speaker_genders = process_speaker_diarization(transcript_data)
        
        if not speaker_segments:
            print(f"[{job_id}] No speaker segments, using original segments")
            speaker_segments = transcript_data['segments']
            # Assign default speaker
            for seg in speaker_segments:
                seg['speaker'] = 'SPEAKER_00'
            speaker_genders = {'SPEAKER_00': 'male'}
        
        # Step 2.6: Assign Indian voices to each speaker (NEW!)
        print(f"[{job_id}] Assigning Indian voices to speakers...")
        print_indian_voices_summary()
        
        speaker_voice_map = assign_voices_to_speakers(speaker_genders, target_language)
        
        if not speaker_voice_map:
            raise Exception("Failed to assign voices to speakers")
        
        # Save speaker info
        speaker_info_file = job_dir / "speakers.json"
        speaker_info = {
            "speaker_genders": speaker_genders,
            "speaker_voices": {
                spk: {"name": voice['name'], "voiceId": voice['voiceId'], "gender": voice['gender']}
                for spk, voice in speaker_voice_map.items()
            }
        }
        with open(speaker_info_file, 'w', encoding='utf-8') as f:
            json.dump(speaker_info, f, indent=2, ensure_ascii=False)
        
        print(f"[{job_id}] Speaker-Voice Mapping:")
        for speaker, voice in speaker_voice_map.items():
            print(f"  {speaker} ({speaker_genders[speaker]}) -> {voice['name']} (ID: {voice['voiceId']})")
        
        # Step 3: Process segments with speaker-specific voices
        update_job_status(jobs_dict, job_id, "processing", 40, "translate", "Translating segments...")
        print(f"[{job_id}] Processing {len(speaker_segments)} speaker segments...")
        
        segments_info = []
        
        for idx, segment in enumerate(speaker_segments):
            segment_text = segment['text'].strip()
            if not segment_text:
                continue
            
            speaker_id = segment.get('speaker', 'SPEAKER_00')
            
            print(f"[{job_id}] Segment {idx + 1}/{len(speaker_segments)}: [{speaker_id}] {segment_text[:50]}...")
            
            # Translate
            translated_text = translate_segment(
                segment_text,
                target_language,
                context=transcript_data['text'][:200]  # Provide context
            )
            print(f"[{job_id}]   Translated: {translated_text[:50]}...")
            
            # Get speaker-specific voice (NEW!)
            if speaker_id in speaker_voice_map:
                voice = speaker_voice_map[speaker_id]
                voice_id = voice['voiceId']
                voice_name = voice['name']
                print(f"[{job_id}]   Using voice: {voice_name} ({speaker_genders.get(speaker_id, 'neutral')})")
            else:
                # Fallback: use first available voice
                print(f"[{job_id}]   WARNING: No voice assigned for {speaker_id}, using fallback")
                if speaker_voice_map:
                    voice = list(speaker_voice_map.values())[0]
                    voice_id = voice['voiceId']
                else:
                    raise Exception(f"No voice available for speaker {speaker_id}")
            
            # Generate voice
            segment_audio_path = segments_dir / f"segment_{idx}.wav"
            
            update_job_status(
                jobs_dict, job_id, "processing",
                40 + int(40 * idx / len(speaker_segments)),
                "voice_generation",
                f"Generating voice {idx + 1}/{len(speaker_segments)} [{speaker_id}]..."
            )
            
            if not generate_voice_segment(translated_text, voice_id, str(segment_audio_path)):
                print(f"[{job_id}] Failed to generate segment {idx}, skipping...")
                continue
            
            # Adjust duration to match original
            original_duration = segment['end'] - segment['start']
            adjusted_audio_path = segments_dir / f"segment_{idx}_adj.wav"
            
            adjust_audio_duration(str(segment_audio_path), original_duration, str(adjusted_audio_path))
            
            segments_info.append({
                'audio': str(adjusted_audio_path),
                'start': segment['start'],
                'end': segment['end'],
                'text': translated_text
            })
        
        # Step 4: Merge all segments with background
        update_job_status(jobs_dict, job_id, "processing", 85, "merge", "Merging audio with background...")
        print(f"[{job_id}] Merging {len(segments_info)} segments with background...")
        
        merged_audio = job_dir / "dubbed_audio.wav"
        if not merge_audio_segments(segments_info, str(background_audio), str(merged_audio)):
            raise Exception("Failed to merge audio segments")
        
        # Step 5: Merge with video
        update_job_status(jobs_dict, job_id, "processing", 95, "final_merge", "Creating final video...")
        print(f"[{job_id}] Merging audio with video...")
        
        output_video_path = job_dir / f"final_dubbed_{job_id}.mp4"
        if not merge_audio_video(video_path, str(merged_audio), str(output_video_path)):
            raise Exception("Failed to merge audio and video")
        
        # Done!
        update_job_status(jobs_dict, job_id, "done", 100, "complete", "Advanced dubbing complete!")
        jobs_dict[job_id]["result_path"] = str(output_video_path)
        jobs_dict[job_id]["transcript_path"] = str(transcript_file)
        
        print(f"[{job_id}] SUCCESS - Advanced processing complete!")
        print(f"[{job_id}]   Output: {output_video_path}")
        print(f"[{job_id}]   Transcript: {transcript_file}")
        
        return True
        
    except Exception as e:
        error_msg = f"Processing failed: {str(e)}"
        print(f"[{job_id}] ERROR - {error_msg}")
        import traceback
        traceback.print_exc()
        update_job_status(jobs_dict, job_id, "error", 0, "error", error_msg)
        return False

