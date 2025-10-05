"""
WhisperX-based transcription with word-level timestamps and diarization alignment.
Provides more accurate timing than standard Whisper.
"""
import whisperx
import gc
import torch
from typing import List, Dict, Optional
from .config import settings


class WhisperXTranscriber:
    def __init__(self, model_size: str = "base", device: str = "cuda" if torch.cuda.is_available() else "cpu"):
        self.model_size = model_size
        self.device = device
        self.compute_type = "float16" if device == "cuda" else "int8"
        self.model = None
        self.align_model = None
        self.align_metadata = None
        
    def load_model(self):
        """Load WhisperX model if not already loaded."""
        if self.model is None:
            print(f"🎯 Loading WhisperX model ({self.model_size}) on {self.device}...")
            self.model = whisperx.load_model(
                self.model_size, 
                self.device, 
                compute_type=self.compute_type
            )
            
    def transcribe(self, audio_path: str, language: Optional[str] = None) -> Dict:
        """
        Transcribe audio with word-level timestamps.
        
        Args:
            audio_path: Path to audio/video file
            language: Optional language code (e.g., 'en', 'hi', 'es')
            
        Returns:
            Dictionary with segments containing word-level timestamps
        """
        self.load_model()
        
        print(f"🎤 Transcribing with WhisperX...")
        
        # Load audio
        audio = whisperx.load_audio(audio_path)
        
        # Transcribe
        result = self.model.transcribe(audio, batch_size=16, language=language)
        
        # Align whisper output for word-level timestamps
        if result["language"] and result["segments"]:
            print(f"🔄 Aligning timestamps for language: {result['language']}...")
            try:
                model_a, metadata = whisperx.load_align_model(
                    language_code=result["language"], 
                    device=self.device
                )
                result = whisperx.align(
                    result["segments"], 
                    model_a, 
                    metadata, 
                    audio, 
                    self.device,
                    return_char_alignments=False
                )
                
                # Clean up alignment model
                del model_a
                gc.collect()
                if self.device == "cuda":
                    torch.cuda.empty_cache()
                    
            except Exception as e:
                print(f"⚠️ Alignment failed: {e}. Using unaligned timestamps.")
                
        return result
    
    def transcribe_with_diarization(
        self, 
        audio_path: str, 
        diarization_segments: List[Dict],
        language: Optional[str] = None
    ) -> List[Dict]:
        """
        Transcribe and assign speakers based on diarization results.
        
        Args:
            audio_path: Path to audio file
            diarization_segments: List of diarization segments with speaker labels
            language: Optional language code
            
        Returns:
            List of segments with speaker labels and word-level timestamps
        """
        result = self.transcribe(audio_path, language)
        
        if not diarization_segments:
            return result.get("segments", [])
        
        print("👥 Assigning speakers to transcript segments...")
        
        # Assign speaker labels to segments
        segments_with_speakers = []
        
        for segment in result.get("segments", []):
            seg_start = segment.get("start", 0)
            seg_end = segment.get("end", 0)
            
            # Find overlapping speaker
            speaker = self._find_speaker_for_segment(seg_start, seg_end, diarization_segments)
            
            segment["speaker"] = speaker
            segments_with_speakers.append(segment)
            
        return segments_with_speakers
    
    def _find_speaker_for_segment(self, start: float, end: float, diarization_segments: List[Dict]) -> str:
        """
        Find the most overlapping speaker for a given time segment.
        """
        max_overlap = 0
        assigned_speaker = "SPEAKER_00"
        
        for diar_seg in diarization_segments:
            overlap_start = max(start, diar_seg["start"])
            overlap_end = min(end, diar_seg["end"])
            overlap = max(0, overlap_end - overlap_start)
            
            if overlap > max_overlap:
                max_overlap = overlap
                assigned_speaker = diar_seg["speaker"]
                
        return assigned_speaker
    
    def cleanup(self):
        """Release model resources."""
        if self.model:
            del self.model
            self.model = None
            gc.collect()
            if self.device == "cuda":
                torch.cuda.empty_cache()

