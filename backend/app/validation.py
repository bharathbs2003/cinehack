"""
Validation utilities for testing and quality assurance.
"""
import os
import json
from typing import Dict, List, Optional
import cv2
from pydub import AudioSegment


class DubbingValidator:
    """Validator for dubbing pipeline output."""
    
    def __init__(self):
        self.validation_results = {}
        
    def validate_output(
        self,
        original_video_path: str,
        dubbed_video_path: str,
        transcript_path: Optional[str] = None
    ) -> Dict:
        """
        Comprehensive validation of dubbing output.
        
        Args:
            original_video_path: Path to original video
            dubbed_video_path: Path to dubbed video
            transcript_path: Path to transcript JSON
            
        Returns:
            Validation results dictionary
        """
        results = {
            "overall_status": "pass",
            "checks": {}
        }
        
        # Check 1: File existence
        results["checks"]["file_exists"] = self._check_file_exists(dubbed_video_path)
        
        # Check 2: Video duration match
        results["checks"]["duration_match"] = self._check_duration_match(
            original_video_path,
            dubbed_video_path
        )
        
        # Check 3: Audio presence
        results["checks"]["audio_present"] = self._check_audio_presence(dubbed_video_path)
        
        # Check 4: Video quality
        results["checks"]["video_quality"] = self._check_video_quality(dubbed_video_path)
        
        # Check 5: Transcript validation
        if transcript_path and os.path.exists(transcript_path):
            results["checks"]["transcript_valid"] = self._validate_transcript(transcript_path)
            
        # Determine overall status
        failed_checks = [
            check for check, result in results["checks"].items()
            if not result.get("passed", False)
        ]
        
        if failed_checks:
            results["overall_status"] = "fail"
            results["failed_checks"] = failed_checks
        else:
            results["overall_status"] = "pass"
            
        return results
    
    def _check_file_exists(self, file_path: str) -> Dict:
        """Check if output file exists."""
        exists = os.path.exists(file_path)
        return {
            "passed": exists,
            "message": "Output file exists" if exists else "Output file not found",
            "file_path": file_path
        }
    
    def _check_duration_match(
        self,
        original_path: str,
        dubbed_path: str,
        tolerance_seconds: float = 0.5
    ) -> Dict:
        """Check if dubbed video duration matches original."""
        try:
            # Get original duration
            orig_cap = cv2.VideoCapture(original_path)
            orig_fps = orig_cap.get(cv2.CAP_PROP_FPS)
            orig_frames = orig_cap.get(cv2.CAP_PROP_FRAME_COUNT)
            orig_duration = orig_frames / orig_fps if orig_fps > 0 else 0
            orig_cap.release()
            
            # Get dubbed duration
            dubbed_cap = cv2.VideoCapture(dubbed_path)
            dubbed_fps = dubbed_cap.get(cv2.CAP_PROP_FPS)
            dubbed_frames = dubbed_cap.get(cv2.CAP_PROP_FRAME_COUNT)
            dubbed_duration = dubbed_frames / dubbed_fps if dubbed_fps > 0 else 0
            dubbed_cap.release()
            
            # Check difference
            diff = abs(orig_duration - dubbed_duration)
            passed = diff <= tolerance_seconds
            
            return {
                "passed": passed,
                "message": f"Duration difference: {diff:.2f}s",
                "original_duration": orig_duration,
                "dubbed_duration": dubbed_duration,
                "difference": diff,
                "tolerance": tolerance_seconds
            }
            
        except Exception as e:
            return {
                "passed": False,
                "message": f"Error checking duration: {e}"
            }
    
    def _check_audio_presence(self, video_path: str) -> Dict:
        """Check if video has audio track."""
        try:
            # Try to load audio
            audio = AudioSegment.from_file(video_path)
            has_audio = len(audio) > 0
            
            return {
                "passed": has_audio,
                "message": "Audio track present" if has_audio else "No audio track found",
                "audio_duration": len(audio) / 1000.0 if has_audio else 0
            }
            
        except Exception as e:
            return {
                "passed": False,
                "message": f"Error checking audio: {e}"
            }
    
    def _check_video_quality(self, video_path: str) -> Dict:
        """Check basic video quality metrics."""
        try:
            cap = cv2.VideoCapture(video_path)
            
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            fps = cap.get(cv2.CAP_PROP_FPS)
            frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            
            cap.release()
            
            # Basic quality checks
            min_resolution = 480
            min_fps = 15
            
            passed = (
                width >= min_resolution and
                height >= min_resolution and
                fps >= min_fps and
                frame_count > 0
            )
            
            return {
                "passed": passed,
                "message": "Video quality acceptable" if passed else "Video quality issues detected",
                "width": width,
                "height": height,
                "fps": fps,
                "frame_count": frame_count
            }
            
        except Exception as e:
            return {
                "passed": False,
                "message": f"Error checking video quality: {e}"
            }
    
    def _validate_transcript(self, transcript_path: str) -> Dict:
        """Validate transcript JSON structure."""
        try:
            with open(transcript_path, "r", encoding="utf-8") as f:
                transcript = json.load(f)
                
            if not isinstance(transcript, list):
                return {
                    "passed": False,
                    "message": "Transcript should be a list of segments"
                }
                
            # Check required fields
            required_fields = ["start", "end", "text"]
            
            for i, segment in enumerate(transcript):
                for field in required_fields:
                    if field not in segment:
                        return {
                            "passed": False,
                            "message": f"Segment {i} missing required field: {field}"
                        }
                        
            return {
                "passed": True,
                "message": "Transcript structure valid",
                "num_segments": len(transcript)
            }
            
        except Exception as e:
            return {
                "passed": False,
                "message": f"Error validating transcript: {e}"
            }
    
    def check_speaker_count_match(
        self,
        transcript: List[Dict],
        expected_speakers: int
    ) -> Dict:
        """Check if detected speaker count matches expected."""
        try:
            detected_speakers = set()
            
            for segment in transcript:
                if "speaker" in segment:
                    detected_speakers.add(segment["speaker"])
                    
            num_detected = len(detected_speakers)
            passed = num_detected == expected_speakers
            
            return {
                "passed": passed,
                "message": f"Detected {num_detected} speakers, expected {expected_speakers}",
                "detected_speakers": list(detected_speakers),
                "expected_count": expected_speakers,
                "actual_count": num_detected
            }
            
        except Exception as e:
            return {
                "passed": False,
                "message": f"Error checking speaker count: {e}"
            }
    
    def check_emotion_alignment(
        self,
        transcript: List[Dict],
        min_accuracy: float = 0.9
    ) -> Dict:
        """Check if emotions are present and valid."""
        try:
            total_segments = len(transcript)
            segments_with_emotion = 0
            
            valid_emotions = ["happy", "sad", "angry", "neutral", "fear", "disgust", "surprise"]
            
            for segment in transcript:
                if "emotion" in segment and segment["emotion"] in valid_emotions:
                    segments_with_emotion += 1
                    
            accuracy = segments_with_emotion / total_segments if total_segments > 0 else 0
            passed = accuracy >= min_accuracy
            
            return {
                "passed": passed,
                "message": f"Emotion detection accuracy: {accuracy:.2%}",
                "accuracy": accuracy,
                "total_segments": total_segments,
                "segments_with_emotion": segments_with_emotion,
                "min_accuracy": min_accuracy
            }
            
        except Exception as e:
            return {
                "passed": False,
                "message": f"Error checking emotions: {e}"
            }

