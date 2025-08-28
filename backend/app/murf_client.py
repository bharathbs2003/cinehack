# backend/app/murf_client.py
import os
import requests

MURF_HTTP_BASE = "https://api.murf.ai/v1/speech"


class MurfClient:
    def __init__(self, api_key: str | None = None):
        self.api_key = api_key or os.getenv("MURF_API_KEY")
        if not self.api_key:
            raise ValueError("❌ MURF_API_KEY is missing! Please set it in .env")

    def list_voices(self):
        """
        Fetch list of available voices from Murf.
        """
        try:
            url = f"{MURF_HTTP_BASE}/voices"
            resp = requests.get(url, headers={"api-key": self.api_key})
            resp.raise_for_status()
            data = resp.json()

            # Murf returns a list
            if isinstance(data, dict) and "voices" in data:
                voices = data["voices"]
            elif isinstance(data, list):
                voices = data
            else:
                voices = []

            print(f"🎤 Retrieved {len(voices)} voices from Murf")
            return voices
        except Exception as e:
            print("⚠️ voices error:", e)
            return []

    def generate_voice(self, text: str, voice_id: str, format: str = "mp3"):
        """
        Generate speech audio from text using Murf.
        Returns JSON response including audioFile URL.
        """
        try:
            payload = {
                "voiceId": voice_id,
                "text": text,
                "format": format,
            }
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
            data = resp.json()

            audio_url = (
                data.get("audioFile")
                or data.get("data", {}).get("audioFile")
                or None
            )

            if not audio_url:
                print("⚠️ No audioFile returned from Murf:", data)
                return {}

            data["audioFile"] = audio_url
            return data
        except Exception as e:
            print("❌ Murf generate_voice error:", e)
            return {}
