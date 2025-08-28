import os
import tempfile
import requests
from fastapi import FastAPI, UploadFile, Form, HTTPException
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware

from .config import settings
from .transcribe_translate import transcribe_audio, translate_text
from .speaker_utils import extract_frames, guess_gender_from_frame
from .murf_client import MurfClient
from .ffmpeg_utils import merge_audio_to_video

app = FastAPI(title="EduDub Live")

# ✅ Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # dev only
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

murf = MurfClient(api_key=settings.MURF_API_KEY)

MALE_VOICES = ["en-US-ryan", "en-IN-pritam", "en-UK-george"]
FEMALE_VOICES = ["en-UK-hazel", "en-US-emma", "en-IN-swara"]

def pick_voice_by_gender(voices: list, gender: str) -> str:
    gender = gender.lower()
    if gender == "male":
        for v in voices:
            if v.get("voiceId") in MALE_VOICES:
                return v["voiceId"]
    if gender == "female":
        for v in voices:
            if v.get("voiceId") in FEMALE_VOICES:
                return v["voiceId"]
    # fallback → pick first available
    first = voices[0]
    return first.get("voiceId") or first.get("id")


@app.get("/")
async def root():
    return {"message": "EduDub backend is running 🚀"}


@app.post("/dub")
async def dub(file: UploadFile, lang: str = Form("hi")):
    # --- Save uploaded video safely ---
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as tmp_video:
        tmp_video.write(await file.read())
        video_path = tmp_video.name

    # --- 1. Transcribe ---
    segs = transcribe_audio(video_path)
    if not segs or not any(s["text"].strip() for s in segs):
        raise HTTPException(status_code=500, detail="Transcription failed: No text found")
    text = " ".join([s["text"] for s in segs])

    # --- 2. Translate ---
    translated = translate_text(text, lang)

    # --- 3. Gender detection ---
    frames = extract_frames(video_path, [1.0, 3.0, 5.0])
    genders = [guess_gender_from_frame(f) for f in frames if f]
    genders = [g for g in genders if g != "unknown"]
    gender = max(set(genders), key=genders.count) if genders else "male"  # default male
    print("🧑 Detected gender:", gender)

    # --- 4. Voice selection ---
    voices = murf.list_voices()
    voice_id = pick_voice_by_gender(voices, gender)
    print("🎙 Picked voice ID:", voice_id)

    # --- 5. TTS generation ---
    result = murf.generate_voice(translated, voice_id)
    audio_url = result.get("audioFile") or result.get("data", {}).get("audioFile")
    if not audio_url:
        raise HTTPException(status_code=500, detail="Murf TTS failed")

    # --- 6. Save dubbed audio safely ---
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp_audio:
        tmp_audio.write(requests.get(audio_url).content)
        audio_path = tmp_audio.name

    # --- 7. Merge audio with video ---
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as tmp_out:
        out_path = tmp_out.name
    try:
        merge_audio_to_video(video_path, audio_path, out_path)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"FFmpeg merge failed: {e}")

    # --- 8. Return dubbed video ---
    return FileResponse(out_path, media_type="video/mp4", filename="dubbed.mp4")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.app.main:app", host=settings.HOST, port=settings.PORT, reload=True)
