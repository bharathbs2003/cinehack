"""
Wav2Lip integration for accurate lip-sync.
Ensures dubbed audio matches lip movements in the video.
"""
import os
import subprocess
from typing import Optional
import torch
import cv2
import numpy as np


class Wav2LipSyncer:
    def __init__(self, checkpoint_path: Optional[str] = None, device: Optional[str] = None):
        """
        Initialize Wav2Lip lip-syncing.
        
        Args:
            checkpoint_path: Path to Wav2Lip model checkpoint
            device: Device to run on ('cuda' or 'cpu')
        """
        self.checkpoint_path = checkpoint_path or "models/wav2lip_gan.pth"
        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")
        self.model = None
        
    def check_wav2lip_installation(self) -> bool:
        """
        Check if Wav2Lip is properly installed.
        
        Returns:
            True if Wav2Lip is available, False otherwise
        """
        try:
            # Check if checkpoint exists
            if not os.path.exists(self.checkpoint_path):
                print(f"⚠️ Wav2Lip checkpoint not found at {self.checkpoint_path}")
                return False
                
            # Check if required Python packages are available
            import face_detection
            return True
            
        except ImportError:
            print("⚠️ Wav2Lip dependencies not installed")
            return False
            
    def apply_lip_sync(
        self,
        video_path: str,
        audio_path: str,
        output_path: str,
        face_detect_batch_size: int = 16,
        wav2lip_batch_size: int = 128,
        resize_factor: int = 1,
        fps: Optional[float] = None
    ) -> bool:
        """
        Apply lip-sync to video using Wav2Lip.
        
        Args:
            video_path: Path to input video
            audio_path: Path to dubbed audio
            output_path: Path to save lip-synced video
            face_detect_batch_size: Batch size for face detection
            wav2lip_batch_size: Batch size for Wav2Lip inference
            resize_factor: Resize factor for processing (1 = no resize)
            fps: Output FPS (None = use source fps)
            
        Returns:
            True if successful, False otherwise
        """
        if not self.check_wav2lip_installation():
            print("⚠️ Wav2Lip not available, skipping lip-sync...")
            # Fallback: just merge audio and video without lip-sync
            return self._simple_audio_merge(video_path, audio_path, output_path)
            
        try:
            print(f"💋 Applying lip-sync with Wav2Lip...")
            
            # Wav2Lip inference command
            # Note: This assumes Wav2Lip repository is cloned and set up
            wav2lip_cmd = [
                "python", "inference.py",
                "--checkpoint_path", self.checkpoint_path,
                "--face", video_path,
                "--audio", audio_path,
                "--outfile", output_path,
                "--resize_factor", str(resize_factor),
                "--face_det_batch_size", str(face_detect_batch_size),
                "--wav2lip_batch_size", str(wav2lip_batch_size)
            ]
            
            if fps:
                wav2lip_cmd.extend(["--fps", str(fps)])
                
            # Change to Wav2Lip directory if needed
            wav2lip_dir = os.environ.get("WAV2LIP_DIR", "Wav2Lip")
            
            if os.path.exists(wav2lip_dir):
                result = subprocess.run(
                    wav2lip_cmd,
                    cwd=wav2lip_dir,
                    capture_output=True,
                    text=True
                )
                
                if result.returncode == 0:
                    print("✅ Lip-sync applied successfully!")
                    return True
                else:
                    print(f"⚠️ Wav2Lip error: {result.stderr}")
                    return self._simple_audio_merge(video_path, audio_path, output_path)
            else:
                print(f"⚠️ Wav2Lip directory not found at {wav2lip_dir}")
                return self._simple_audio_merge(video_path, audio_path, output_path)
                
        except Exception as e:
            print(f"⚠️ Lip-sync error: {e}")
            return self._simple_audio_merge(video_path, audio_path, output_path)
            
    def _simple_audio_merge(self, video_path: str, audio_path: str, output_path: str) -> bool:
        """
        Fallback: Simple audio-video merge without lip-sync.
        """
        try:
            print("🔧 Using simple audio merge (no lip-sync)...")
            
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
            print("✅ Audio merged successfully!")
            return True
            
        except Exception as e:
            print(f"❌ Audio merge failed: {e}")
            return False
            
    def download_wav2lip_model(self) -> bool:
        """
        Download Wav2Lip model checkpoint if not present.
        
        Returns:
            True if successful, False otherwise
        """
        if os.path.exists(self.checkpoint_path):
            print(f"✅ Wav2Lip checkpoint already exists at {self.checkpoint_path}")
            return True
            
        print("📥 Downloading Wav2Lip model...")
        
        try:
            # Create models directory
            os.makedirs(os.path.dirname(self.checkpoint_path), exist_ok=True)
            
            # Download from GitHub releases or Google Drive
            # Note: Update this URL with the actual model download link
            model_url = "https://github.com/Rudrabha/Wav2Lip/releases/download/models/wav2lip_gan.pth"
            
            import requests
            response = requests.get(model_url, stream=True)
            response.raise_for_status()
            
            with open(self.checkpoint_path, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
                    
            print(f"✅ Model downloaded to {self.checkpoint_path}")
            return True
            
        except Exception as e:
            print(f"⚠️ Failed to download model: {e}")
            print("Please download manually from: https://github.com/Rudrabha/Wav2Lip")
            return False

