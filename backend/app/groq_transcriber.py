"""
Groq Whisper transcription - FREE and FAST alternative to OpenAI
"""
import os
from groq import Groq

def transcribe_audio_groq(audio_path, api_key):
    """
    Transcribe audio using Groq's free Whisper API.
    
    Args:
        audio_path: Path to audio file
        api_key: Groq API key
    
    Returns:
        str: Transcribed text or None if failed
    """
    try:
        # Check file exists
        if not os.path.exists(audio_path):
            print(f"ERROR: Audio file not found: {audio_path}")
            return None
        
        file_size = os.path.getsize(audio_path)
        print(f"Audio file size: {file_size / 1024:.2f} KB")
        
        if file_size == 0:
            print(f"ERROR: Audio file is empty")
            return None
        
        # Groq accepts up to 25MB files
        if file_size > 25 * 1024 * 1024:
            print(f"ERROR: Audio file too large ({file_size / 1024 / 1024:.2f} MB). Max is 25 MB.")
            return None
        
        print(f"Opening audio file: {audio_path}")
        
        # Initialize Groq client
        client = Groq(api_key=api_key)
        
        # Transcribe with Groq Whisper
        print(f"Calling Groq Whisper API...")
        with open(audio_path, "rb") as audio_file:
            transcription = client.audio.transcriptions.create(
                file=audio_file,
                model="whisper-large-v3",  # Groq's Whisper model
                response_format="text",
                language="en",  # Auto-detect if needed
                temperature=0.0
            )
        
        # Groq returns the text directly
        transcript = transcription if isinstance(transcription, str) else transcription.text
        
        print(f"Transcription successful. Length: {len(transcript)} characters")
        return transcript
        
    except Exception as e:
        print(f"Groq transcription error: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return None


def test_groq_api(api_key):
    """Test if Groq API key is valid"""
    try:
        client = Groq(api_key=api_key)
        # Try a simple API call
        models = client.models.list()
        print(f"✅ Groq API key is valid!")
        print(f"Available models: {len(models.data)}")
        return True
    except Exception as e:
        print(f"❌ Groq API key test failed: {e}")
        return False

