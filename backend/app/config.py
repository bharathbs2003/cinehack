from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # API keys
    MURF_API_KEY: str = ""
    OPENAI_API_KEY: str = ""
    GROQ_API_KEY: Optional[str] = None
    WHISPER_API_KEY: Optional[str] = None
    ELEVENLABS_API_KEY: Optional[str] = None
    HUGGINGFACE_TOKEN: Optional[str] = None

    # Whisper backend selection: "openai" | "local" | "whisperx"
    WHISPER_BACKEND: str = "whisperx"  

    # ffmpeg path (for merging audio/video)
    ffmpeg_path: str = "ffmpeg"  # Use system PATH by default

    # Server config
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # Murf WS settings
    MURF_WS_TOKEN_TTL: int = 3600
    
    # Celery / Redis
    CELERY_BROKER_URL: str = "redis://localhost:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/0"
    
    # Pipeline settings
    USE_WHISPERX: bool = True
    USE_DIARIZATION: bool = True
    USE_EMOTION_DETECTION: bool = True
    USE_ELEVENLABS: bool = False  # Set to True if you have API key
    USE_WAV2LIP: bool = False  # Set to True if Wav2Lip is set up
    
    # Paths
    UPLOAD_DIR: str = "tmp_uploads"
    OUTPUT_DIR: str = "output"
    MODELS_DIR: str = "models"
    WAV2LIP_DIR: str = "Wav2Lip"

    class Config:
        env_file = ".env"


settings = Settings()
