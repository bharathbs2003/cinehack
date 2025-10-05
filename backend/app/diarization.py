"""
Speaker diarization using pyannote.audio
Identifies and labels different speakers in the audio.
"""
from typing import List, Dict, Optional
import torch
from pyannote.audio import Pipeline
from .config import settings
import os


class SpeakerDiarizer:
    def __init__(self, auth_token: Optional[str] = None):
        """
        Initialize speaker diarization pipeline.
        
        Args:
            auth_token: HuggingFace API token (required for pyannote models)
        """
        self.auth_token = auth_token or os.getenv("HUGGINGFACE_TOKEN") or settings.HUGGINGFACE_TOKEN
        self.pipeline = None
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        
    def load_pipeline(self):
        """Load pyannote diarization pipeline."""
        if self.pipeline is None:
            if not self.auth_token:
                raise ValueError("❌ HUGGINGFACE_TOKEN is required for speaker diarization!")
                
            print(f"👥 Loading speaker diarization pipeline on {self.device}...")
            
            self.pipeline = Pipeline.from_pretrained(
                "pyannote/speaker-diarization-3.1",
                use_auth_token=self.auth_token
            )
            
            if self.device == "cuda":
                self.pipeline.to(torch.device("cuda"))
                
    def diarize(self, audio_path: str, min_speakers: Optional[int] = None, max_speakers: Optional[int] = None) -> List[Dict]:
        """
        Perform speaker diarization on audio file.
        
        Args:
            audio_path: Path to audio/video file
            min_speakers: Minimum number of speakers (optional)
            max_speakers: Maximum number of speakers (optional)
            
        Returns:
            List of segments: [{"speaker": "SPEAKER_00", "start": 0.0, "end": 2.5}, ...]
        """
        self.load_pipeline()
        
        print(f"🎙️ Running speaker diarization...")
        
        # Run diarization
        diarization_params = {}
        if min_speakers:
            diarization_params["min_speakers"] = min_speakers
        if max_speakers:
            diarization_params["max_speakers"] = max_speakers
            
        diarization = self.pipeline(audio_path, **diarization_params)
        
        # Convert to list of segments
        segments = []
        for turn, _, speaker in diarization.itertracks(yield_label=True):
            segments.append({
                "speaker": speaker,
                "start": turn.start,
                "end": turn.end
            })
            
        num_speakers = len(set(seg["speaker"] for seg in segments))
        print(f"✅ Identified {num_speakers} speaker(s)")
        
        return segments
    
    def get_speaker_stats(self, segments: List[Dict]) -> Dict:
        """
        Get statistics about speakers.
        
        Returns:
            Dictionary with speaker statistics
        """
        speaker_times = {}
        
        for seg in segments:
            speaker = seg["speaker"]
            duration = seg["end"] - seg["start"]
            
            if speaker not in speaker_times:
                speaker_times[speaker] = {
                    "total_duration": 0,
                    "num_segments": 0
                }
                
            speaker_times[speaker]["total_duration"] += duration
            speaker_times[speaker]["num_segments"] += 1
            
        return {
            "num_speakers": len(speaker_times),
            "speakers": speaker_times
        }

