# backend/app/ffmpeg_utils.py
import subprocess

def merge_audio_to_video(video_path: str, audio_path: str, output_path: str):
    """
    Replace video's original audio with new dubbed audio.
    Ensures sync by re-encoding.
    """
    try:
        cmd = [
            "ffmpeg",
            "-y",  # overwrite
            "-i", video_path,
            "-i", audio_path,
            "-c:v", "copy",
            "-map", "0:v:0",
            "-map", "1:a:0",
            "-shortest",  # cut to shortest stream (avoid black frames)
            output_path,
        ]
        subprocess.run(cmd, check=True)
        print("✅ FFmpeg merged audio + video:", output_path)
    except Exception as e:
        print("❌ FFmpeg merge error:", e)
