"""
Emotion detection using SpeechBrain's wav2vec2-based emotion recognition.
Detects emotions like happy, sad, angry, neutral for each speaker segment.
"""
from typing import List, Dict, Optional
import torch
import torchaudio
from speechbrain.pretrained import EncoderClassifier
import numpy as np
from pydub import AudioSegment
import os


class EmotionDetector:
    def __init__(self, device: Optional[str] = None):
        """
        Initialize emotion detection model.
        
        Args:
            device: Device to run model on ('cuda' or 'cpu')
        """
        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")
        self.classifier = None
        
        # Emotion label mapping for IEMOCAP
        self.emotion_labels = {
            0: "neutral",
            1: "happy",
            2: "sad",
            3: "angry"
        }
        
    def load_model(self):
        """Load SpeechBrain emotion recognition model."""
        if self.classifier is None:
            print(f"😊 Loading emotion detection model on {self.device}...")
            
            try:
                self.classifier = EncoderClassifier.from_hparams(
                    source="speechbrain/emotion-recognition-wav2vec2-IEMOCAP",
                    savedir="models/emotion_recognition",
                    run_opts={"device": self.device}
                )
            except Exception as e:
                print(f"⚠️ Failed to load emotion model: {e}")
                print("Continuing without emotion detection...")
                self.classifier = None
                
    def detect_emotion(self, audio_path: str, start_time: float, end_time: float) -> str:
        """
        Detect emotion for a specific segment of audio.
        
        Args:
            audio_path: Path to audio file
            start_time: Start time in seconds
            end_time: End time in seconds
            
        Returns:
            Emotion label (e.g., 'happy', 'sad', 'angry', 'neutral')
        """
        if self.classifier is None:
            return "neutral"
            
        try:
            # Extract segment from audio
            segment_path = self._extract_segment(audio_path, start_time, end_time)
            
            # Load audio
            signal, sr = torchaudio.load(segment_path)
            
            # Ensure mono
            if signal.shape[0] > 1:
                signal = torch.mean(signal, dim=0, keepdim=True)
                
            # Resample if needed (model expects 16kHz)
            if sr != 16000:
                resampler = torchaudio.transforms.Resample(sr, 16000)
                signal = resampler(signal)
                
            # Predict emotion
            with torch.no_grad():
                out_prob, score, index, text_lab = self.classifier.classify_batch(signal)
                
            # Clean up temp file
            if os.path.exists(segment_path):
                os.remove(segment_path)
                
            # Return emotion label
            return text_lab[0] if text_lab else "neutral"
            
        except Exception as e:
            print(f"⚠️ Emotion detection error for segment {start_time}-{end_time}: {e}")
            return "neutral"
            
    def detect_emotions_for_segments(self, audio_path: str, segments: List[Dict]) -> List[Dict]:
        """
        Detect emotions for all segments.
        
        Args:
            audio_path: Path to audio file
            segments: List of segments with start/end times
            
        Returns:
            Segments with added emotion field
        """
        self.load_model()
        
        if self.classifier is None:
            # Add default emotion if model failed to load
            for seg in segments:
                seg["emotion"] = "neutral"
            return segments
            
        print("😊 Detecting emotions for segments...")
        
        enriched_segments = []
        
        for i, segment in enumerate(segments):
            start = segment.get("start", 0)
            end = segment.get("end", 0)
            
            # Skip very short segments
            if end - start < 0.5:
                segment["emotion"] = "neutral"
            else:
                emotion = self.detect_emotion(audio_path, start, end)
                segment["emotion"] = emotion
                
            enriched_segments.append(segment)
            
            if (i + 1) % 10 == 0:
                print(f"  Processed {i + 1}/{len(segments)} segments...")
                
        return enriched_segments
    
    def _extract_segment(self, audio_path: str, start_time: float, end_time: float) -> str:
        """
        Extract a segment from audio file and save temporarily.
        
        Returns:
            Path to extracted segment
        """
        audio = AudioSegment.from_file(audio_path)
        
        # Extract segment (times in milliseconds)
        segment = audio[int(start_time * 1000):int(end_time * 1000)]
        
        # Save to temporary file
        temp_path = f"temp_segment_{os.getpid()}_{int(start_time * 1000)}.wav"
        segment.export(temp_path, format="wav")
        
        return temp_path
    
    def get_emotion_summary(self, segments: List[Dict]) -> Dict:
        """
        Get summary statistics of emotions across all segments.
        
        Returns:
            Dictionary with emotion counts and percentages
        """
        emotion_counts = {}
        total = len(segments)
        
        for seg in segments:
            emotion = seg.get("emotion", "neutral")
            emotion_counts[emotion] = emotion_counts.get(emotion, 0) + 1
            
        emotion_percentages = {
            emotion: (count / total * 100) if total > 0 else 0
            for emotion, count in emotion_counts.items()
        }
        
        return {
            "total_segments": total,
            "emotion_counts": emotion_counts,
            "emotion_percentages": emotion_percentages
        }

