"""
Audio reconstruction and synchronization utilities.
Merges multiple audio segments into a single dubbed track with proper timing.
"""
from typing import List, Dict, Optional
import os
from pydub import AudioSegment
from pydub.silence import detect_silence
import numpy as np


class AudioReconstructor:
    def __init__(self):
        """Initialize audio reconstructor."""
        self.sample_rate = 44100
        
    def merge_segments_to_track(
        self,
        segments: List[Dict],
        output_path: str,
        total_duration_ms: Optional[int] = None,
        add_silence_padding: bool = True
    ) -> str:
        """
        Merge multiple audio segments into a single track with proper timing.
        
        Args:
            segments: List of segments with 'audio_path', 'start', 'end' fields
            output_path: Path to save merged audio
            total_duration_ms: Total duration in milliseconds (None = auto-detect)
            add_silence_padding: Whether to add silence between segments
            
        Returns:
            Path to merged audio file
        """
        print(f"🎵 Merging {len(segments)} audio segments...")
        
        # Filter segments with valid audio
        valid_segments = [
            seg for seg in segments 
            if seg.get("audio_path") and os.path.exists(seg["audio_path"])
        ]
        
        if not valid_segments:
            print("⚠️ No valid audio segments to merge!")
            return None
            
        # Determine total duration
        if total_duration_ms is None:
            max_end = max(seg.get("end", 0) for seg in segments)
            total_duration_ms = int(max_end * 1000) + 1000  # Add 1 second buffer
            
        # Create silent base track
        base_track = AudioSegment.silent(duration=total_duration_ms)
        
        # Overlay each segment at its timestamp
        for i, segment in enumerate(valid_segments):
            try:
                audio_path = segment["audio_path"]
                start_time = segment.get("start", 0)
                
                # Load segment audio
                audio_segment = AudioSegment.from_file(audio_path)
                
                # Position in milliseconds
                position_ms = int(start_time * 1000)
                
                # Overlay onto base track
                base_track = base_track.overlay(audio_segment, position=position_ms)
                
                if (i + 1) % 20 == 0:
                    print(f"  Merged {i + 1}/{len(valid_segments)} segments...")
                    
            except Exception as e:
                print(f"⚠️ Error merging segment {i}: {e}")
                continue
                
        # Export merged track
        base_track.export(output_path, format="mp3", bitrate="192k")
        print(f"✅ Merged audio saved to: {output_path}")
        
        return output_path
    
    def adjust_speed_for_duration(
        self,
        audio_path: str,
        target_duration_ms: int,
        output_path: Optional[str] = None
    ) -> str:
        """
        Adjust audio speed to match target duration.
        Useful for maintaining original video timing.
        
        Args:
            audio_path: Path to audio file
            target_duration_ms: Target duration in milliseconds
            output_path: Path to save adjusted audio
            
        Returns:
            Path to adjusted audio
        """
        audio = AudioSegment.from_file(audio_path)
        current_duration = len(audio)
        
        if current_duration == target_duration_ms:
            return audio_path
            
        speed_ratio = current_duration / target_duration_ms
        
        print(f"⏱️ Adjusting audio speed by {speed_ratio:.2f}x...")
        
        # Speed up or slow down
        adjusted_audio = audio._spawn(
            audio.raw_data,
            overrides={"frame_rate": int(audio.frame_rate * speed_ratio)}
        ).set_frame_rate(audio.frame_rate)
        
        if output_path is None:
            output_path = audio_path.replace(".mp3", "_adjusted.mp3")
            
        adjusted_audio.export(output_path, format="mp3")
        
        return output_path
    
    def normalize_volume(
        self,
        audio_path: str,
        target_dBFS: float = -20.0,
        output_path: Optional[str] = None
    ) -> str:
        """
        Normalize audio volume to target level.
        
        Args:
            audio_path: Path to audio file
            target_dBFS: Target volume in dBFS
            output_path: Path to save normalized audio
            
        Returns:
            Path to normalized audio
        """
        audio = AudioSegment.from_file(audio_path)
        
        # Calculate volume adjustment
        change_in_dBFS = target_dBFS - audio.dBFS
        
        if abs(change_in_dBFS) < 0.5:
            return audio_path  # Already at target volume
            
        print(f"🔊 Normalizing volume by {change_in_dBFS:.2f} dB...")
        
        # Apply adjustment
        normalized_audio = audio.apply_gain(change_in_dBFS)
        
        if output_path is None:
            output_path = audio_path.replace(".mp3", "_normalized.mp3")
            
        normalized_audio.export(output_path, format="mp3")
        
        return output_path
    
    def add_crossfade(
        self,
        segments: List[Dict],
        crossfade_duration_ms: int = 100
    ) -> List[AudioSegment]:
        """
        Add crossfade between consecutive audio segments.
        
        Args:
            segments: List of segments with audio_path
            crossfade_duration_ms: Crossfade duration in milliseconds
            
        Returns:
            List of AudioSegment objects with crossfade applied
        """
        audio_segments = []
        
        for segment in segments:
            if segment.get("audio_path") and os.path.exists(segment["audio_path"]):
                audio = AudioSegment.from_file(segment["audio_path"])
                audio_segments.append(audio)
                
        if len(audio_segments) < 2:
            return audio_segments
            
        # Apply crossfade between consecutive segments
        result = [audio_segments[0]]
        
        for i in range(1, len(audio_segments)):
            prev_segment = result[-1]
            curr_segment = audio_segments[i]
            
            # Crossfade
            crossfaded = prev_segment.append(curr_segment, crossfade=crossfade_duration_ms)
            result[-1] = crossfaded
            
        return result
    
    def extract_audio_from_video(
        self,
        video_path: str,
        output_path: Optional[str] = None,
        format: str = "wav"
    ) -> str:
        """
        Extract audio from video file.
        
        Args:
            video_path: Path to video file
            output_path: Path to save extracted audio
            format: Audio format (wav, mp3, etc.)
            
        Returns:
            Path to extracted audio
        """
        if output_path is None:
            output_path = video_path.rsplit(".", 1)[0] + f".{format}"
            
        print(f"🎵 Extracting audio from video...")
        
        import subprocess
        
        cmd = [
            "ffmpeg",
            "-y",
            "-i", video_path,
            "-vn",  # No video
            "-acodec", "pcm_s16le" if format == "wav" else "libmp3lame",
            "-ar", "44100",
            "-ac", "2",
            output_path
        ]
        
        subprocess.run(cmd, check=True, capture_output=True)
        
        print(f"✅ Audio extracted to: {output_path}")
        
        return output_path
    
    def get_audio_duration(self, audio_path: str) -> float:
        """
        Get duration of audio file in seconds.
        
        Args:
            audio_path: Path to audio file
            
        Returns:
            Duration in seconds
        """
        audio = AudioSegment.from_file(audio_path)
        return len(audio) / 1000.0
    
    def validate_audio_sync(
        self,
        original_audio_path: str,
        dubbed_audio_path: str,
        tolerance_seconds: float = 0.5
    ) -> Dict:
        """
        Validate that dubbed audio matches original duration.
        
        Args:
            original_audio_path: Path to original audio
            dubbed_audio_path: Path to dubbed audio
            tolerance_seconds: Acceptable duration difference
            
        Returns:
            Validation results
        """
        orig_duration = self.get_audio_duration(original_audio_path)
        dubbed_duration = self.get_audio_duration(dubbed_audio_path)
        
        diff = abs(orig_duration - dubbed_duration)
        
        return {
            "original_duration": orig_duration,
            "dubbed_duration": dubbed_duration,
            "difference": diff,
            "within_tolerance": diff <= tolerance_seconds,
            "tolerance": tolerance_seconds
        }

