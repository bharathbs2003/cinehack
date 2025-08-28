from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # API keys
    MURF_API_KEY: str
    OPENAI_API_KEY: str
    WHISPER_API_KEY: str | None = None   # optional, not always needed for local whisper

    # Whisper backend selection: "openai" | "local"
    WHISPER_BACKEND: str = "local"  

    # ffmpeg path (for merging audio/video)
    ffmpeg_path: str = r"D:\ffmpeg-7.1.1-essentials_build\ffmpeg-7.1.1-essentials_build\bin\ffmpeg.exe"

    # Server config
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # Murf WS settings
    MURF_WS_TOKEN_TTL: int = 3600

    class Config:
        env_file = ".env"


settings = Settings()
