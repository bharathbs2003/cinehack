"""
ElevenLabs TTS integration with emotion-aware voice generation.
Provides high-quality, natural-sounding speech with emotion preservation.
"""
from typing import List, Dict, Optional
import requests
import os
from .config import settings


class ElevenLabsTTS:
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize ElevenLabs TTS client.
        
        Args:
            api_key: ElevenLabs API key
        """
        self.api_key = api_key or os.getenv("ELEVENLABS_API_KEY") or getattr(settings, "ELEVENLABS_API_KEY", None)
        self.base_url = "https://api.elevenlabs.io/v1"
        
        if not self.api_key:
            print("⚠️ ELEVENLABS_API_KEY not found. TTS will not work without it.")
            
    def list_voices(self) -> List[Dict]:
        """
        Get available voices from ElevenLabs.
        
        Returns:
            List of voice objects with metadata
        """
        if not self.api_key:
            return []
            
        try:
            response = requests.get(
                f"{self.base_url}/voices",
                headers={"xi-api-key": self.api_key}
            )
            response.raise_for_status()
            
            voices = response.json().get("voices", [])
            print(f"🎤 Retrieved {len(voices)} voices from ElevenLabs")
            
            return voices
            
        except Exception as e:
            print(f"⚠️ Error fetching voices: {e}")
            return []
            
    def select_voice_by_characteristics(
        self, 
        gender: Optional[str] = None, 
        accent: Optional[str] = None,
        age: Optional[str] = None
    ) -> Optional[str]:
        """
        Select an appropriate voice based on characteristics.
        
        Args:
            gender: 'male', 'female', or None
            accent: Accent preference (e.g., 'american', 'british')
            age: Age preference (e.g., 'young', 'middle_aged', 'old')
            
        Returns:
            Voice ID
        """
        voices = self.list_voices()
        
        if not voices:
            return None
            
        # Filter by characteristics
        filtered_voices = voices
        
        if gender:
            gender_lower = gender.lower()
            filtered_voices = [
                v for v in filtered_voices 
                if v.get("labels", {}).get("gender", "").lower() == gender_lower
            ]
            
        if accent:
            accent_lower = accent.lower()
            filtered_voices = [
                v for v in filtered_voices 
                if accent_lower in v.get("labels", {}).get("accent", "").lower()
            ]
            
        if age:
            age_lower = age.lower()
            filtered_voices = [
                v for v in filtered_voices 
                if age_lower in v.get("labels", {}).get("age", "").lower()
            ]
            
        # Return first match or fallback to first available voice
        if filtered_voices:
            return filtered_voices[0]["voice_id"]
        elif voices:
            return voices[0]["voice_id"]
        else:
            return None
            
    def generate_speech(
        self,
        text: str,
        voice_id: str,
        output_path: str,
        stability: float = 0.5,
        similarity_boost: float = 0.75,
        style: float = 0.0,
        emotion: Optional[str] = None
    ) -> bool:
        """
        Generate speech from text with emotion modulation.
        
        Args:
            text: Text to convert to speech
            voice_id: ElevenLabs voice ID
            output_path: Path to save audio file
            stability: Voice stability (0-1)
            similarity_boost: Voice similarity boost (0-1)
            style: Style exaggeration (0-1)
            emotion: Emotion hint (e.g., 'happy', 'sad', 'angry')
            
        Returns:
            True if successful, False otherwise
        """
        if not self.api_key:
            print("❌ Cannot generate speech: API key missing")
            return False
            
        try:
            # Adjust voice settings based on emotion
            voice_settings = {
                "stability": stability,
                "similarity_boost": similarity_boost,
                "style": style
            }
            
            if emotion:
                voice_settings = self._adjust_for_emotion(voice_settings, emotion)
                
            url = f"{self.base_url}/text-to-speech/{voice_id}"
            
            headers = {
                "xi-api-key": self.api_key,
                "Content-Type": "application/json"
            }
            
            payload = {
                "text": text,
                "model_id": "eleven_multilingual_v2",  # Supports multiple languages
                "voice_settings": voice_settings
            }
            
            response = requests.post(url, json=payload, headers=headers)
            response.raise_for_status()
            
            # Save audio
            with open(output_path, "wb") as f:
                f.write(response.content)
                
            return True
            
        except Exception as e:
            print(f"⚠️ Speech generation error: {e}")
            return False
            
    def generate_speech_for_segments(
        self,
        segments: List[Dict],
        voice_mapping: Dict[str, str],
        output_dir: str,
        use_emotions: bool = True
    ) -> List[Dict]:
        """
        Generate speech for multiple segments with speaker-specific voices.
        
        Args:
            segments: List of segments with text, speaker, and emotion
            voice_mapping: Dictionary mapping speaker IDs to voice IDs
            output_dir: Directory to save audio files
            use_emotions: Whether to use emotion modulation
            
        Returns:
            Segments with added 'audio_path' field
        """
        if not self.api_key:
            print("❌ Cannot generate speech: API key missing")
            return segments
            
        print(f"🎙️ Generating speech for {len(segments)} segments...")
        
        os.makedirs(output_dir, exist_ok=True)
        
        enriched_segments = []
        
        for i, segment in enumerate(segments):
            text = segment.get("translated_text") or segment.get("text", "")
            speaker = segment.get("speaker", "SPEAKER_00")
            emotion = segment.get("emotion", "neutral") if use_emotions else None
            
            if not text.strip():
                segment["audio_path"] = None
                enriched_segments.append(segment)
                continue
                
            # Get voice for speaker
            voice_id = voice_mapping.get(speaker)
            
            if not voice_id:
                print(f"⚠️ No voice mapping for {speaker}, using default")
                voice_id = list(voice_mapping.values())[0] if voice_mapping else self.list_voices()[0]["voice_id"]
                
            # Generate audio
            audio_filename = f"segment_{i:04d}_{speaker}.mp3"
            audio_path = os.path.join(output_dir, audio_filename)
            
            success = self.generate_speech(
                text=text,
                voice_id=voice_id,
                output_path=audio_path,
                emotion=emotion
            )
            
            segment["audio_path"] = audio_path if success else None
            enriched_segments.append(segment)
            
            if (i + 1) % 10 == 0:
                print(f"  Generated {i + 1}/{len(segments)} segments...")
                
        print(f"✅ Speech generation complete!")
        
        return enriched_segments
    
    def _adjust_for_emotion(self, settings: Dict, emotion: str) -> Dict:
        """
        Adjust voice settings based on emotion.
        """
        emotion_lower = emotion.lower()
        
        # Emotion-based adjustments
        if emotion_lower in ["happy", "excited", "joyful"]:
            settings["stability"] = max(0.3, settings["stability"] - 0.2)
            settings["style"] = min(1.0, settings.get("style", 0) + 0.3)
        elif emotion_lower in ["sad", "melancholy", "depressed"]:
            settings["stability"] = min(0.8, settings["stability"] + 0.2)
            settings["style"] = min(1.0, settings.get("style", 0) + 0.2)
        elif emotion_lower in ["angry", "furious", "frustrated"]:
            settings["stability"] = max(0.2, settings["stability"] - 0.3)
            settings["style"] = min(1.0, settings.get("style", 0) + 0.4)
        elif emotion_lower in ["calm", "peaceful", "neutral"]:
            settings["stability"] = 0.5
            settings["style"] = 0.0
            
        return settings

