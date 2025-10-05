"""
Speaker voice management with Indian Murf voices.
Maps genders to Indian voice characters for consistent speaker dubbing.
"""
import requests
from typing import Dict, List, Optional
from .config import settings

MURF_API_BASE = "https://api.murf.ai/v1"
MURF_API_KEY = settings.MURF_API_KEY

# Pre-defined Indian voice mapping by gender
# This will be dynamically fetched and cached
INDIAN_VOICES_CACHE = {
    "male": [],
    "female": [],
    "neutral": []
}


# Popular Indian Murf voices (backup if API fails)
INDIAN_VOICES_FALLBACK = {
    "male": [
        {"name": "Arjun", "voiceId": "en-IN-arjun", "language": "en-IN", "gender": "male", "accent": "Indian"},
        {"name": "Rohan", "voiceId": "en-IN-rohan", "language": "en-IN", "gender": "male", "accent": "Indian"},
        {"name": "Raj", "voiceId": "en-IN-raj", "language": "en-IN", "gender": "male", "accent": "Indian"},
        {"name": "Vikram", "voiceId": "en-IN-vikram", "language": "en-IN", "gender": "male", "accent": "Indian"},
        {"name": "Amit", "voiceId": "en-IN-amit", "language": "en-IN", "gender": "male", "accent": "Indian"},
    ],
    "female": [
        {"name": "Priya", "voiceId": "en-IN-priya", "language": "en-IN", "gender": "female", "accent": "Indian"},
        {"name": "Anjali", "voiceId": "en-IN-anjali", "language": "en-IN", "gender": "female", "accent": "Indian"},
        {"name": "Diya", "voiceId": "en-IN-diya", "language": "en-IN", "gender": "female", "accent": "Indian"},
        {"name": "Kavya", "voiceId": "en-IN-kavya", "language": "en-IN", "gender": "female", "accent": "Indian"},
        {"name": "Meera", "voiceId": "en-IN-meera", "language": "en-IN", "gender": "female", "accent": "Indian"},
    ],
    "neutral": []
}


def fetch_murf_voices() -> List[Dict]:
    """Fetch all available voices from Murf API."""
    try:
        url = f"{MURF_API_BASE}/speech/voices"
        headers = {"api-key": MURF_API_KEY}
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        voices = data.get("voices", []) if isinstance(data, dict) else data
        return voices
    except Exception as e:
        print(f"Error fetching Murf voices: {e}")
        return []


def get_indian_voices_by_gender() -> Dict[str, List[Dict]]:
    """
    Get Indian voices from Murf API, organized by gender.
    Returns a dictionary with keys: 'male', 'female', 'neutral'
    """
    global INDIAN_VOICES_CACHE
    
    # Return cache if already populated
    if INDIAN_VOICES_CACHE["male"] or INDIAN_VOICES_CACHE["female"]:
        return INDIAN_VOICES_CACHE
    
    print("Fetching Indian voices from Murf API...")
    
    all_voices = fetch_murf_voices()
    
    if not all_voices:
        print("Using fallback Indian voices")
        return INDIAN_VOICES_FALLBACK
    
    # Filter for Indian voices
    indian_voices = {"male": [], "female": [], "neutral": []}
    
    for voice in all_voices:
        # Check if voice is Indian (by language or accent)
        language = voice.get("languageName", "").lower()
        language_code = voice.get("languageCode", "").lower()
        accent = voice.get("accent", "").lower()
        voice_name = voice.get("name", "").lower()
        
        # Identify Indian voices
        is_indian = (
            "india" in language or 
            "hindi" in language or 
            "indian" in accent or
            language_code.startswith("hi-") or
            language_code.startswith("en-in") or
            any(name in voice_name for name in ["arjun", "priya", "raj", "kavya", "amit", "diya"])
        )
        
        if is_indian:
            gender = voice.get("gender", "neutral").lower()
            
            # Normalize gender
            if "male" in gender and "female" not in gender:
                gender = "male"
            elif "female" in gender:
                gender = "female"
            else:
                gender = "neutral"
            
            voice_info = {
                "name": voice.get("name", "Unknown"),
                "voiceId": voice.get("voiceId") or voice.get("id"),
                "language": voice.get("languageCode", "en-IN"),
                "gender": gender,
                "accent": voice.get("accent", "Indian"),
                "age": voice.get("age", "adult"),
                "style": voice.get("style", "neutral")
            }
            
            indian_voices[gender].append(voice_info)
    
    # If no Indian voices found, use fallback
    if not indian_voices["male"] and not indian_voices["female"]:
        print("No Indian voices found in API, using fallback")
        indian_voices = INDIAN_VOICES_FALLBACK
    else:
        print(f"Found {len(indian_voices['male'])} male and {len(indian_voices['female'])} female Indian voices")
    
    # Cache the results
    INDIAN_VOICES_CACHE = indian_voices
    
    return indian_voices


def assign_voices_to_speakers(speaker_genders: Dict[str, str], language_code: str = "en-IN") -> Dict[str, Dict]:
    """
    Assign different Indian voices to different speakers based on their gender.
    
    Args:
        speaker_genders: Dict mapping speaker IDs to genders
                        Example: {"SPEAKER_00": "male", "SPEAKER_01": "female"}
        language_code: Target language code (default: en-IN for Indian English)
    
    Returns:
        Dict mapping speaker IDs to voice information
        Example: {
            "SPEAKER_00": {"name": "Arjun", "voiceId": "en-IN-arjun", ...},
            "SPEAKER_01": {"name": "Priya", "voiceId": "en-IN-priya", ...}
        }
    """
    indian_voices = get_indian_voices_by_gender()
    
    speaker_voice_map = {}
    voice_index = {"male": 0, "female": 0, "neutral": 0}
    
    for speaker_id, gender in speaker_genders.items():
        # Get available voices for this gender
        available_voices = indian_voices.get(gender, indian_voices["neutral"])
        
        if not available_voices:
            # Fallback to any available voice
            for g in ["male", "female", "neutral"]:
                if indian_voices[g]:
                    available_voices = indian_voices[g]
                    break
        
        if not available_voices:
            print(f"WARNING: No voices available for {speaker_id} ({gender})")
            continue
        
        # Assign voice (cycle through available voices)
        idx = voice_index[gender] % len(available_voices)
        voice = available_voices[idx]
        
        speaker_voice_map[speaker_id] = voice
        voice_index[gender] += 1
        
        print(f"Assigned {speaker_id} ({gender}) -> {voice['name']} (voiceId: {voice['voiceId']})")
    
    return speaker_voice_map


def detect_speaker_gender_simple(speaker_id: str, segment_text: str) -> str:
    """
    Simple gender detection based on text cues and patterns.
    In production, use audio-based gender detection (pitch analysis, ML model, etc.)
    
    Args:
        speaker_id: Speaker identifier (e.g., "SPEAKER_00")
        segment_text: Text spoken by this speaker
    
    Returns:
        Gender: "male", "female", or "neutral"
    """
    # Simple heuristic based on common patterns
    # In production, replace with actual audio-based gender detection
    
    text_lower = segment_text.lower()
    
    # Check for gender-specific pronouns or words in common speech
    female_indicators = ["she", "her", "mrs", "ms", "miss", "lady", "woman", "girl", "mother", "sister", "daughter"]
    male_indicators = ["he", "him", "mr", "sir", "man", "boy", "father", "brother", "son"]
    
    female_count = sum(1 for word in female_indicators if word in text_lower)
    male_count = sum(1 for word in male_indicators if word in text_lower)
    
    if female_count > male_count:
        return "female"
    elif male_count > female_count:
        return "male"
    else:
        # Default: alternate between male and female for different speakers
        # Extract speaker number (e.g., "SPEAKER_00" -> 0)
        try:
            speaker_num = int(speaker_id.split("_")[-1])
            return "female" if speaker_num % 2 == 1 else "male"
        except:
            return "neutral"


def print_indian_voices_summary():
    """Print a summary of available Indian voices."""
    voices = get_indian_voices_by_gender()
    
    print("\n" + "=" * 60)
    print("INDIAN VOICES AVAILABLE (MURF)")
    print("=" * 60)
    
    for gender in ["male", "female"]:
        voice_list = voices.get(gender, [])
        print(f"\n{gender.upper()} VOICES ({len(voice_list)}):")
        for i, voice in enumerate(voice_list, 1):
            print(f"  {i}. {voice['name']:15} - {voice['voiceId']:20} ({voice.get('style', 'neutral')})")
    
    print("\n" + "=" * 60)


def get_voice_for_language_gender(language_code: str, gender: str, voice_index: int = 0) -> Optional[Dict]:
    """
    Get a specific voice for a language and gender.
    
    Args:
        language_code: Language code (e.g., "hi" for Hindi, "en" for English)
        gender: "male" or "female"
        voice_index: Index of voice to return (for variety)
    
    Returns:
        Voice information dict or None
    """
    # Map language codes
    lang_map = {
        "hi": "hindi",
        "en": "indian",  # Will look for Indian English voices
        "en-in": "indian"
    }
    
    target_lang = lang_map.get(language_code.lower(), "indian")
    
    # For Indian languages, use Indian voices
    if target_lang in ["hindi", "indian"]:
        voices = get_indian_voices_by_gender()
        voice_list = voices.get(gender, [])
        
        if voice_list:
            return voice_list[voice_index % len(voice_list)]
    
    # Fallback: fetch from Murf API for other languages
    all_voices = fetch_murf_voices()
    
    filtered = [v for v in all_voices 
                if gender in v.get("gender", "").lower() 
                and target_lang in v.get("languageName", "").lower()]
    
    if filtered:
        return filtered[voice_index % len(filtered)]
    
    return None

