import os
import tempfile
import requests
import uuid
import threading
from fastapi import FastAPI, UploadFile, Form, HTTPException
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware

from .config import settings
from .transcribe_translate import transcribe_audio, translate_text
from .speaker_utils import extract_frames, guess_gender_from_frame
from .murf_client import MurfClient
from .ffmpeg_utils import merge_audio_to_video

app = FastAPI(title="EduDub Live")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For dev only
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Murf client
murf = MurfClient(api_key=settings.MURF_API_KEY)

MALE_VOICES = ["en-US-ryan", "en-IN-pritam", "en-UK-george"]
FEMALE_VOICES = ["en-UK-hazel", "en-US-emma", "en-IN-swara"]

# In-memory job store
JOBS = {}


def normalize_gender(g):
    g = str(g).lower()
    if "male" in g or "man" in g:
        return "male"
    if "female" in g or "woman" in g:
        return "female"
    return "unknown"


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
    # fallback → first voice
    first = voices[0]
    return first.get("voiceId") or first.get("id")


def process_dubbing(job_id, video_path, lang):
    try:
        JOBS[job_id]["status"] = "processing"

        #  Transcribe
        segs = transcribe_audio(video_path)
        if not segs or not any(s["text"].strip() for s in segs):
            JOBS[job_id]["status"] = "error"
            JOBS[job_id]["error"] = "Transcription failed"
            return
        text = " ".join([s["text"] for s in segs])

        #  Translate
        translated = translate_text(text, lang)

        #  Gender detection
        frames = extract_frames(video_path, [1.0, 3.0, 5.0])
        genders = [normalize_gender(guess_gender_from_frame(f)) for f in frames if f]
        genders = [g for g in genders if g != "unknown"]
        gender = max(set(genders), key=genders.count) if genders else "male"
        print(" Detected gender:", gender)

        #  Voice selection
        voices = murf.list_voices()
        voice_id = pick_voice_by_gender(voices, gender)
        print(" Selected voice:", voice_id)

        #  TTS generation
        audio_output = f"audio_{job_id}.mp3"
        murf.generate_voice(translated, voice_id, output_file=audio_output)

        #  Merge audio + video
        out_path = f"dubbed_{job_id}.mp4"
        merge_audio_to_video(video_path, audio_output, out_path)

        #  Update job
        JOBS[job_id]["status"] = "done"
        JOBS[job_id]["result"] = out_path

        #  Cleanup temp audio/video
        os.remove(video_path)
        if os.path.exists(audio_output):
            os.remove(audio_output)

    except Exception as e:
        JOBS[job_id]["status"] = "error"
        JOBS[job_id]["error"] = str(e)
        print(" Dubbing error:", e)


@app.get("/")
async def root():
    return {"message": "EduDub backend is running "}


@app.post("/dub")
async def dub(file: UploadFile, lang: str = Form("hi")):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as tmp_video:
        tmp_video.write(await file.read())
        video_path = tmp_video.name

    job_id = str(uuid.uuid4())
    JOBS[job_id] = {"status": "queued"}

    threading.Thread(target=process_dubbing, args=(job_id, video_path, lang), daemon=True).start()

    return {"job_id": job_id, "status": "queued"}


@app.get("/status/{job_id}")
async def get_status(job_id: str):
    job = JOBS.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return {"job_id": job_id, "status": job["status"], "error": job.get("error")}


@app.get("/result/{job_id}")
async def get_result(job_id: str):
    job = JOBS.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    if job["status"] != "done":
        raise HTTPException(status_code=400, detail="Job not finished yet")
    return FileResponse(job["result"], media_type="video/mp4", filename="dubbed.mp4")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.app.main:app", host=settings.HOST, port=settings.PORT, reload=True)
