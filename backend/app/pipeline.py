"""
Main dubbing pipeline orchestrator.
Coordinates all components: transcription, diarization, emotion, translation, TTS, and lip-sync.
"""
import os
import uuid
import json
from typing import Dict, List, Optional, Callable
from datetime import datetime
import gc

from .whisperx_transcriber import WhisperXTranscriber
from .diarization import SpeakerDiarizer
from .emotion_detector import EmotionDetector
from .nllb_translator import NLLBTranslator
from .elevenlabs_tts import ElevenLabsTTS
from .murf_client import MurfClient
from .wav2lip_sync import Wav2LipSyncer
from .audio_reconstruction import AudioReconstructor
from .config import settings


class DubbingPipeline:
    """
    Complete video dubbing pipeline with all advanced features.
    """
    
    def __init__(
        self,
        use_whisperx: bool = True,
        use_diarization: bool = True,
        use_emotion: bool = True,
        use_elevenlabs: bool = False,
        use_wav2lip: bool = True
    ):
        """
        Initialize dubbing pipeline.
        
        Args:
            use_whisperx: Use WhisperX for transcription (vs basic Whisper)
            use_diarization: Enable speaker diarization
            use_emotion: Enable emotion detection
            use_elevenlabs: Use ElevenLabs TTS (vs Murf)
            use_wav2lip: Enable lip-sync with Wav2Lip
        """
        self.use_whisperx = use_whisperx
        self.use_diarization = use_diarization
        self.use_emotion = use_emotion
        self.use_elevenlabs = use_elevenlabs
        self.use_wav2lip = use_wav2lip
        
        # Initialize components
        self.transcriber = None
        self.diarizer = None
        self.emotion_detector = None
        self.translator = None
        self.tts_client = None
        self.lip_syncer = None
        self.audio_reconstructor = AudioReconstructor()
        
    def _log(self, message: str, progress_callback: Optional[Callable] = None, stage: str = "", progress: int = 0):
        """Log message and update progress."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_message = f"[{timestamp}] {message}"
        print(log_message)
        
        if progress_callback:
            progress_callback(stage, progress, message)
            
    def process(
        self,
        video_path: str,
        target_language: str,
        source_language: str = "en",
        output_dir: str = "output",
        min_speakers: Optional[int] = None,
        max_speakers: Optional[int] = None,
        progress_callback: Optional[Callable] = None
    ) -> Dict:
        """
        Run complete dubbing pipeline.
        
        Args:
            video_path: Path to input video
            target_language: Target language code
            source_language: Source language code
            output_dir: Output directory
            min_speakers: Minimum speakers for diarization
            max_speakers: Maximum speakers for diarization
            progress_callback: Callback function for progress updates
            
        Returns:
            Dictionary with results and paths
        """
        job_id = str(uuid.uuid4())[:8]
        job_dir = os.path.join(output_dir, job_id)
        os.makedirs(job_dir, exist_ok=True)
        
        self._log(f"🎬 Starting dubbing pipeline [Job: {job_id}]", progress_callback, "init", 0)
        
        try:
            # Step 1: Extract audio from video
            self._log("✔ Extracting audio from video...", progress_callback, "extract_audio", 5)
            audio_path = self.audio_reconstructor.extract_audio_from_video(
                video_path,
                os.path.join(job_dir, "original_audio.wav")
            )
            
            # Step 2: Transcription
            self._log("✔ Transcribing audio...", progress_callback, "transcribe", 10)
            if self.use_whisperx:
                self.transcriber = WhisperXTranscriber()
                transcription_result = self.transcriber.transcribe(audio_path, source_language)
                segments = transcription_result.get("segments", [])
            else:
                from .transcribe_translate import transcribe_audio
                segments = transcribe_audio(audio_path)
                
            if not segments:
                raise ValueError("Transcription failed: No segments detected")
                
            self._log(f"✔ Transcribed {len(segments)} segments", progress_callback, "transcribe", 20)
            
            # Step 3: Speaker Diarization
            diarization_segments = []
            if self.use_diarization:
                self._log("✔ Performing speaker diarization...", progress_callback, "diarization", 25)
                try:
                    self.diarizer = SpeakerDiarizer()
                    diarization_segments = self.diarizer.diarize(
                        audio_path,
                        min_speakers=min_speakers,
                        max_speakers=max_speakers
                    )
                    
                    # Assign speakers to segments
                    segments = self._assign_speakers(segments, diarization_segments)
                    
                    stats = self.diarizer.get_speaker_stats(diarization_segments)
                    self._log(f"✔ Identified {stats['num_speakers']} speaker(s)", progress_callback, "diarization", 30)
                except Exception as e:
                    self._log(f"⚠️ Diarization failed: {e}. Continuing without speaker labels.", progress_callback, "diarization", 30)
                    
            # Step 4: Emotion Detection
            if self.use_emotion:
                self._log("✔ Detecting emotions...", progress_callback, "emotion", 35)
                try:
                    self.emotion_detector = EmotionDetector()
                    segments = self.emotion_detector.detect_emotions_for_segments(audio_path, segments)
                    
                    emotion_summary = self.emotion_detector.get_emotion_summary(segments)
                    self._log(f"✔ Emotion detection complete: {emotion_summary['emotion_counts']}", progress_callback, "emotion", 45)
                except Exception as e:
                    self._log(f"⚠️ Emotion detection failed: {e}. Continuing without emotions.", progress_callback, "emotion", 45)
                    
            # Step 5: Translation
            self._log(f"✔ Translating to {target_language}...", progress_callback, "translate", 50)
            self.translator = NLLBTranslator()
            segments = self.translator.translate_segments(segments, source_language, target_language)
            self._log("✔ Translation complete", progress_callback, "translate", 60)
            
            # Step 6: Voice Generation
            self._log("✔ Generating dubbed voices...", progress_callback, "voice_generation", 65)
            
            # Create voice mapping for speakers
            voice_mapping = self._create_voice_mapping(segments)
            
            tts_dir = os.path.join(job_dir, "tts_segments")
            os.makedirs(tts_dir, exist_ok=True)
            
            if self.use_elevenlabs:
                try:
                    self.tts_client = ElevenLabsTTS()
                    segments = self.tts_client.generate_speech_for_segments(
                        segments,
                        voice_mapping,
                        tts_dir,
                        use_emotions=self.use_emotion
                    )
                except Exception as e:
                    self._log(f"⚠️ ElevenLabs TTS failed: {e}. Falling back to Murf.", progress_callback, "voice_generation", 70)
                    self.use_elevenlabs = False
                    
            if not self.use_elevenlabs:
                # Use Murf as fallback
                self.tts_client = MurfClient(api_key=settings.MURF_API_KEY)
                segments = self._generate_with_murf(segments, voice_mapping, tts_dir)
                
            self._log("✔ Voice generation complete", progress_callback, "voice_generation", 80)
            
            # Step 7: Audio Reconstruction
            self._log("✔ Reconstructing dubbed audio track...", progress_callback, "audio_merge", 85)
            
            # Get original video duration
            import cv2
            cap = cv2.VideoCapture(video_path)
            fps = cap.get(cv2.CAP_PROP_FPS)
            frame_count = cap.get(cv2.CAP_PROP_FRAME_COUNT)
            duration_ms = int((frame_count / fps) * 1000) if fps > 0 else None
            cap.release()
            
            dubbed_audio_path = os.path.join(job_dir, "dubbed_audio.mp3")
            self.audio_reconstructor.merge_segments_to_track(
                segments,
                dubbed_audio_path,
                total_duration_ms=duration_ms
            )
            
            # Normalize volume
            dubbed_audio_path = self.audio_reconstructor.normalize_volume(dubbed_audio_path)
            
            self._log("✔ Audio reconstruction complete", progress_callback, "audio_merge", 90)
            
            # Step 8: Video Reconstruction with Lip-Sync
            self._log("✔ Applying lip-sync and finalizing video...", progress_callback, "lipsync", 92)
            
            final_video_path = os.path.join(job_dir, f"final_dubbed_{job_id}.mp4")
            
            if self.use_wav2lip:
                try:
                    self.lip_syncer = Wav2LipSyncer()
                    success = self.lip_syncer.apply_lip_sync(
                        video_path,
                        dubbed_audio_path,
                        final_video_path
                    )
                    
                    if not success:
                        raise Exception("Wav2Lip failed")
                        
                except Exception as e:
                    self._log(f"⚠️ Lip-sync failed: {e}. Using simple merge.", progress_callback, "lipsync", 95)
                    # Fallback to simple merge
                    import subprocess
                    subprocess.run([
                        "ffmpeg", "-y",
                        "-i", video_path,
                        "-i", dubbed_audio_path,
                        "-c:v", "copy",
                        "-c:a", "aac",
                        "-map", "0:v:0",
                        "-map", "1:a:0",
                        "-shortest",
                        final_video_path
                    ], check=True, capture_output=True)
            else:
                # Simple audio merge without lip-sync
                import subprocess
                subprocess.run([
                    "ffmpeg", "-y",
                    "-i", video_path,
                    "-i", dubbed_audio_path,
                    "-c:v", "copy",
                    "-c:a", "aac",
                    "-map", "0:v:0",
                    "-map", "1:a:0",
                    "-shortest",
                    final_video_path
                ], check=True, capture_output=True)
                
            self._log("🎬 Final video saved!", progress_callback, "complete", 100)
            
            # Cleanup
            self._cleanup()
            
            # Prepare result
            result = {
                "job_id": job_id,
                "status": "success",
                "final_video_path": final_video_path,
                "dubbed_audio_path": dubbed_audio_path,
                "transcript": segments,
                "metadata": {
                    "source_language": source_language,
                    "target_language": target_language,
                    "num_segments": len(segments),
                    "num_speakers": len(set(seg.get("speaker", "SPEAKER_00") for seg in segments)),
                    "duration_seconds": duration_ms / 1000 if duration_ms else 0,
                    "processing_date": datetime.now().isoformat()
                }
            }
            
            return result
            
        except Exception as e:
            self._log(f"❌ Pipeline error: {e}", progress_callback, "error", 0)
            raise
            
    def _assign_speakers(self, segments: List[Dict], diarization_segments: List[Dict]) -> List[Dict]:
        """Assign speaker labels to transcript segments."""
        for segment in segments:
            start = segment.get("start", 0)
            end = segment.get("end", 0)
            
            # Find overlapping speaker
            max_overlap = 0
            assigned_speaker = "SPEAKER_00"
            
            for diar_seg in diarization_segments:
                overlap_start = max(start, diar_seg["start"])
                overlap_end = min(end, diar_seg["end"])
                overlap = max(0, overlap_end - overlap_start)
                
                if overlap > max_overlap:
                    max_overlap = overlap
                    assigned_speaker = diar_seg["speaker"]
                    
            segment["speaker"] = assigned_speaker
            
        return segments
    
    def _create_voice_mapping(self, segments: List[Dict]) -> Dict[str, str]:
        """Create voice mapping for each speaker."""
        speakers = list(set(seg.get("speaker", "SPEAKER_00") for seg in segments))
        voice_mapping = {}
        
        if self.use_elevenlabs and self.tts_client:
            voices = self.tts_client.list_voices()
            
            for i, speaker in enumerate(speakers):
                # Alternate between male/female voices
                gender = "male" if i % 2 == 0 else "female"
                voice_id = self.tts_client.select_voice_by_characteristics(gender=gender)
                voice_mapping[speaker] = voice_id or voices[i % len(voices)]["voice_id"]
        else:
            # Use Murf voices
            male_voices = ["en-US-ryan", "en-IN-pritam"]
            female_voices = ["en-UK-hazel", "en-US-emma"]
            
            for i, speaker in enumerate(speakers):
                if i % 2 == 0:
                    voice_mapping[speaker] = male_voices[i % len(male_voices)]
                else:
                    voice_mapping[speaker] = female_voices[i % len(female_voices)]
                    
        return voice_mapping
    
    def _generate_with_murf(self, segments: List[Dict], voice_mapping: Dict, output_dir: str) -> List[Dict]:
        """Generate speech using Murf TTS."""
        for i, segment in enumerate(segments):
            text = segment.get("translated_text") or segment.get("text", "")
            speaker = segment.get("speaker", "SPEAKER_00")
            
            if not text.strip():
                segment["audio_path"] = None
                continue
                
            voice_id = voice_mapping.get(speaker, list(voice_mapping.values())[0])
            
            audio_filename = f"segment_{i:04d}_{speaker}.mp3"
            audio_path = os.path.join(output_dir, audio_filename)
            
            try:
                self.tts_client.generate_voice(text, voice_id, output_file=audio_path)
                segment["audio_path"] = audio_path
            except Exception as e:
                print(f"⚠️ TTS error for segment {i}: {e}")
                segment["audio_path"] = None
                
        return segments
    
    def _cleanup(self):
        """Cleanup resources."""
        if self.transcriber:
            self.transcriber.cleanup()
        if self.translator:
            self.translator.cleanup()
            
        gc.collect()

