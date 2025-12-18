"""Language detection module for auto-detecting source language."""

from langdetect import detect, LangDetectException
from typing import Optional


class LanguageDetector:
    """Detect language of text with support for EN/UK/RU."""
    
    # Language code mappings
    SUPPORTED_LANGUAGES = {
        'en': 'English',
        'uk': 'Ukrainian',
        'ru': 'Russian'
    }
    
    def __init__(self):
        """Initialize language detector."""
        pass
    
    def detect_language(self, text: str) -> Optional[str]:
        """Detect the language of given text.
        
        Args:
            text: Input text to detect language
            
        Returns:
            Language code (en, uk, ru) or None if detection fails
        """
        if not text or not text.strip():
            return None
        
        try:
            detected = detect(text)
            
            # Map to supported languages
            if detected in self.SUPPORTED_LANGUAGES:
                return detected
            
            # Return the detected language even if not in supported list
            return detected
            
        except LangDetectException:
            return None
    
    def is_supported_language(self, lang_code: str) -> bool:
        """Check if a language is supported.
        
        Args:
            lang_code: Language code to check
            
        Returns:
            True if language is supported
        """
        return lang_code in self.SUPPORTED_LANGUAGES
    
    def get_language_name(self, lang_code: str) -> str:
        """Get human-readable language name.
        
        Args:
            lang_code: Language code
            
        Returns:
            Language name or the code itself if not found
        """
        return self.SUPPORTED_LANGUAGES.get(lang_code, lang_code)
    
    def detect_from_segments(self, texts: list) -> Optional[str]:
        """Detect language from multiple text segments (uses voting).
        
        Args:
            texts: List of text strings
            
        Returns:
            Most common detected language or None
        """
        if not texts:
            return None
        
        detections = []
        for text in texts:
            lang = self.detect_language(text)
            if lang:
                detections.append(lang)
        
        if not detections:
            return None
        
        # Return most common detection
        from collections import Counter
        return Counter(detections).most_common(1)[0][0]
