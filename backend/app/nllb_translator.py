"""
Translation using Meta's NLLB-200 model for high-quality multilingual translation.
Supports 200+ languages with better quality than generic translation APIs.
"""
from typing import List, Dict, Optional
import torch
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer
import gc


class NLLBTranslator:
    def __init__(self, model_name: str = "facebook/nllb-200-distilled-600M", device: Optional[str] = None):
        """
        Initialize NLLB translator.
        
        Args:
            model_name: HuggingFace model name
            device: Device to run model on
        """
        self.model_name = model_name
        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")
        self.model = None
        self.tokenizer = None
        
        # Language code mapping
        self.lang_codes = {
            "en": "eng_Latn",
            "hi": "hin_Deva",
            "es": "spa_Latn",
            "fr": "fra_Latn",
            "de": "deu_Latn",
            "zh": "zho_Hans",
            "ja": "jpn_Jpan",
            "ko": "kor_Hang",
            "ar": "arb_Arab",
            "pt": "por_Latn",
            "ru": "rus_Cyrl",
            "it": "ita_Latn",
            "mr": "mar_Deva",
            "bn": "ben_Beng",
            "ta": "tam_Taml",
            "te": "tel_Telu",
        }
        
    def load_model(self):
        """Load NLLB model and tokenizer."""
        if self.model is None:
            print(f"🌍 Loading NLLB translation model ({self.model_name}) on {self.device}...")
            
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            self.model = AutoModelForSeq2SeqLM.from_pretrained(self.model_name)
            self.model.to(self.device)
            self.model.eval()
            
            print(f"✅ NLLB model loaded successfully")
            
    def translate(
        self, 
        text: str, 
        source_lang: str = "en", 
        target_lang: str = "hi",
        max_length: int = 512
    ) -> str:
        """
        Translate text from source language to target language.
        
        Args:
            text: Text to translate
            source_lang: Source language code (e.g., 'en', 'hi')
            target_lang: Target language code
            max_length: Maximum length of generated translation
            
        Returns:
            Translated text
        """
        self.load_model()
        
        if not text.strip():
            return ""
            
        # Get FLORES-200 language codes
        src_code = self.lang_codes.get(source_lang, "eng_Latn")
        tgt_code = self.lang_codes.get(target_lang, "hin_Deva")
        
        try:
            # Tokenize
            self.tokenizer.src_lang = src_code
            inputs = self.tokenizer(
                text, 
                return_tensors="pt", 
                padding=True, 
                truncation=True, 
                max_length=max_length
            ).to(self.device)
            
            # Generate translation
            with torch.no_grad():
                generated_tokens = self.model.generate(
                    **inputs,
                    forced_bos_token_id=self.tokenizer.lang_code_to_id[tgt_code],
                    max_length=max_length,
                    num_beams=5,
                    early_stopping=True
                )
                
            # Decode
            translation = self.tokenizer.batch_decode(
                generated_tokens, 
                skip_special_tokens=True
            )[0]
            
            return translation
            
        except Exception as e:
            print(f"⚠️ Translation error: {e}")
            return text  # Return original text on error
            
    def translate_segments(
        self, 
        segments: List[Dict], 
        source_lang: str = "en", 
        target_lang: str = "hi"
    ) -> List[Dict]:
        """
        Translate all text segments while preserving metadata.
        
        Args:
            segments: List of segments with 'text' field
            source_lang: Source language code
            target_lang: Target language code
            
        Returns:
            Segments with added 'translated_text' field
        """
        self.load_model()
        
        print(f"🌍 Translating {len(segments)} segments from {source_lang} to {target_lang}...")
        
        translated_segments = []
        
        for i, segment in enumerate(segments):
            original_text = segment.get("text", "")
            
            if not original_text.strip():
                segment["translated_text"] = ""
            else:
                translated = self.translate(original_text, source_lang, target_lang)
                segment["translated_text"] = translated
                
            translated_segments.append(segment)
            
            if (i + 1) % 10 == 0:
                print(f"  Translated {i + 1}/{len(segments)} segments...")
                
        print(f"✅ Translation complete!")
        
        return translated_segments
    
    def cleanup(self):
        """Release model resources."""
        if self.model:
            del self.model
            del self.tokenizer
            self.model = None
            self.tokenizer = None
            gc.collect()
            if self.device == "cuda":
                torch.cuda.empty_cache()

