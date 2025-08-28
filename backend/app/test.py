import os
import requests
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables
load_dotenv()

OPENAI_KEY = os.getenv("OPENAI_API_KEY")
MURF_KEY = os.getenv("MURF_API_KEY")

# 1️⃣ Test OpenAI
def test_openai():
    try:
        client = OpenAI(api_key=OPENAI_KEY)
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": "Say hello in one word"}]
        )
        print("✅ OpenAI API Key working:", response.choices[0].message.content)
    except Exception as e:
        print("❌ OpenAI API failed:", e)


# 2️⃣ List Murf Voices
def list_murf_voices():
    try:
        url = "https://api.murf.ai/v1/speech/voices"
        headers = {"api-key": MURF_KEY}
        res = requests.get(url, headers=headers)

        if res.status_code == 200:
            voices = res.json()  # Murf returns a list
            print("\n✅ Available Murf Voices (showing first 10):")
            for v in voices[:10]:
                vid = v.get("voiceId")
                name = v.get("name")
                lang = v.get("language")
                style = v.get("style", "")
                print(f"- ID: {vid} | Name: {name} | Language: {lang} | Style: {style}")
            return voices
        else:
            print("❌ Failed to fetch voices:", res.status_code, res.text)
            return []
    except Exception as e:
        print("❌ Murf Voices Error:", e)
        return []


# 3️⃣ Generate Voice with Murf
def test_murf_generate(voice_id=""):
    try:
        if not voice_id:
            print("⚠️ No voice_id provided, skipping generation")
            return

        url = "https://api.murf.ai/v1/speech/generate"
        headers = {"api-key": MURF_KEY, "Content-Type": "application/json"}
        payload = {
            "voiceId": voice_id,
            "text": "Hello! This is a Murf API test voice generated successfully.",
            "format": "mp3"
        }

        res = requests.post(url, headers=headers, json=payload)
        if res.status_code == 200:
            data = res.json()
            print("\n✅ Murf voice generated!")
            print("🔗 Audio file:", data.get("audioFile"))
        else:
            print("❌ Murf generate failed:", res.status_code, res.text)
    except Exception as e:
        print("❌ Murf Generate Error:", e)


if __name__ == "__main__":
    print("🔍 Testing APIs...\n")

    # Test OpenAI
    test_openai()

    # Test Murf
    voices = list_murf_voices()
    if voices:
        first_voice = voices[0].get("voiceId")  # pick the first available voice
        test_murf_generate(first_voice)
