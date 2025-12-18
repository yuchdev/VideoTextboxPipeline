"""Translation backend interfaces and implementations."""

from abc import ABC, abstractmethod
from typing import Optional


class TranslatorBackend(ABC):
    """Abstract base class for translation backends."""
    
    @abstractmethod
    def translate(self, text: str, source_lang: str, target_lang: str) -> str:
        """Translate text from source language to target language.
        
        Args:
            text: Text to translate
            source_lang: Source language code
            target_lang: Target language code
            
        Returns:
            Translated text
        """
        pass


class GoogleTranslatorBackend(TranslatorBackend):
    """Google Translate backend implementation."""
    
    def __init__(self):
        """Initialize Google Translator backend."""
        from googletrans import Translator
        self.translator = Translator()
    
    def translate(self, text: str, source_lang: str, target_lang: str) -> str:
        """Translate text using Google Translate.
        
        Args:
            text: Text to translate
            source_lang: Source language code
            target_lang: Target language code
            
        Returns:
            Translated text
        """
        if not text or not text.strip():
            return text
        
        try:
            result = self.translator.translate(
                text,
                src=source_lang,
                dest=target_lang
            )
            return result.text
        except Exception as e:
            print(f"Translation error: {e}")
            return text


class MockTranslatorBackend(TranslatorBackend):
    """Mock translator backend for testing (returns text with [TRANSLATED] prefix)."""
    
    def translate(self, text: str, source_lang: str, target_lang: str) -> str:
        """Mock translation.
        
        Args:
            text: Text to translate
            source_lang: Source language code
            target_lang: Target language code
            
        Returns:
            Text with [TRANSLATED] prefix
        """
        return f"[TRANSLATED:{source_lang}->{target_lang}] {text}"
