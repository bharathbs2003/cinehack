import subprocess

def merge_audio_to_video(video_path: str, audio_path: str, output_path: str):
    """
    Replace video's original audio with new dubbed audio.
    Handles long videos safely by re-encoding audio if needed.
    """
    try:
        cmd = [
            "ffmpeg",
            "-y",                  # overwrite output
            "-i", video_path,      # input video
            "-i", audio_path,      # input audio
            "-c:v", "copy",        # keep video stream as-is
            "-c:a", "aac",         # re-encode audio to AAC
            "-map", "0:v:0",       # take video from first input
            "-map", "1:a:0",       # take audio from second input
            "-shortest",           # cut extra audio/video if lengths differ
            output_path,
        ]
        subprocess.run(cmd, check=True)
        print("✅ FFmpeg merged audio + video:", output_path)
    except Exception as e:
        print("❌ FFmpeg merge error:", e)
        raise
