import os
import requests
from pydub import AudioSegment  # pip install pydub

MURF_HTTP_BASE = "https://api.murf.ai/v1/speech"

class MurfClient:
    def __init__(self, api_key: str | None = None):
        self.api_key = api_key or os.getenv("MURF_API_KEY")
        if not self.api_key:
            raise ValueError("❌ MURF_API_KEY is missing! Please set it in .env")

    def list_voices(self):
        try:
            url = f"{MURF_HTTP_BASE}/voices"
            resp = requests.get(url, headers={"api-key": self.api_key})
            resp.raise_for_status()
            data = resp.json()
            voices = data.get("voices") if isinstance(data, dict) else data
            print(f"🎤 Retrieved {len(voices)} voices from Murf")
            return voices or []
        except Exception as e:
            print("⚠️ voices error:", e)
            return []

    def _generate_single(self, text: str, voice_id: str, format: str = "mp3"):
        """
        Generate speech for a single text chunk.
        """
        payload = {"voiceId": voice_id, "text": text, "format": format}
        url = f"{MURF_HTTP_BASE}/generate"
        resp = requests.post(
            url,
            headers={
                "api-key": self.api_key,
                "Content-Type": "application/json",
            },
            json=payload,
        )
        resp.raise_for_status()
        return resp.json()

    def generate_voice(self, text: str, voice_id: str, format: str = "mp3", output_file: str = "output.mp3"):
        """
        Generate speech for long text (splits into chunks if > 3000 chars).
        Merges audio chunks into a single file.
        """
        MAX_LEN = 3000
        chunks = [text[i:i+MAX_LEN] for i in range(0, len(text), MAX_LEN)]

        all_segments = []

        for idx, chunk in enumerate(chunks, start=1):
            print(f"🎙️ Processing chunk {idx}/{len(chunks)} ({len(chunk)} chars)")
            try:
                data = self._generate_single(chunk, voice_id, format=format)
                audio_url = (
                    data.get("audioFile")
                    or data.get("data", {}).get("audioFile")
                )
                if not audio_url:
                    print("⚠️ No audioFile returned:", data)
                    continue

                # download chunk audio
                audio_resp = requests.get(audio_url)
                tmp_path = f"chunk_{idx}.mp3"
                with open(tmp_path, "wb") as f:
                    f.write(audio_resp.content)

                all_segments.append(AudioSegment.from_file(tmp_path, format="mp3"))

            except Exception as e:
                print(f"❌ Error in chunk {idx}:", e)

        if not all_segments:
            print("⚠️ No audio generated at all.")
            return {}

        # merge chunks
        final_audio = all_segments[0]
        for seg in all_segments[1:]:
            final_audio += seg

        final_audio.export(output_file, format="mp3")
        print(f"✅ Final merged audio saved: {output_file}")

        return {"audioFile": output_file}
