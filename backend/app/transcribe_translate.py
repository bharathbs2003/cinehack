import openai
from typing import List
from .config import settings

# Local whisper import
import whisper
import os

# Set API key for OpenAI
openai.api_key = settings.OPENAI_API_KEY


def transcribe_audio(file_path: str) -> List[dict]:
    """
    Transcribe audio/video file into text segments.
    Returns: [{'start': float, 'end': float, 'text': str}]
    """
    try:
        if settings.WHISPER_BACKEND.lower() == "openai":
            # --- OpenAI Whisper API ---
            with open(file_path, "rb") as f:
                resp = openai.audio.transcriptions.create(
                    file=f,
                    model="gpt-4o-mini-transcribe"
                )
            text = resp.get("text", "")
            if not text:
                raise RuntimeError("Empty transcription from OpenAI Whisper")
            return [{"start": 0.0, "end": 0.0, "text": text}]

        else:
            # --- Local Whisper ---
            model = whisper.load_model("base")  # can use "small", "medium", "large"
            result = model.transcribe(file_path)
            segments = result.get("segments", [])

            if not segments:
                raise RuntimeError("No transcription segments from local Whisper")

            return [
                {"start": seg["start"], "end": seg["end"], "text": seg["text"]}
                for seg in segments
            ]

    except Exception as e:
        print("⚠️ Transcription error:", e)
        return [{"start": 0.0, "end": 0.0, "text": ""}]


def translate_text(text: str, target_lang: str = "hi") -> str:
    """
    Translate text into target language using OpenAI Chat API.
    """
    try:
        if not text.strip():
            return ""

        prompt = f"Translate this text into {target_lang}:\n\n{text}"
        resp = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=1024
        )
        return resp.choices[0].message.content.strip()
    except Exception as e:
        print("⚠️ Translation error:", e)
        return text
