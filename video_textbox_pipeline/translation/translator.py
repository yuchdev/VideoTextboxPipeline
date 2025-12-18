"""Main translator module with pluggable backend support."""

from typing import Optional
from .backends import TranslatorBackend, GoogleTranslatorBackend


class Translator:
    """Main translator class with pluggable backend architecture."""
    
    def __init__(self, backend: Optional[TranslatorBackend] = None):
        """Initialize translator with a backend.
        
        Args:
            backend: Translation backend to use (default: GoogleTranslatorBackend)
        """
        self.backend = backend or GoogleTranslatorBackend()
    
    def translate(self, text: str, source_lang: str, target_lang: str) -> str:
        """Translate text from source to target language.
        
        Args:
            text: Text to translate
            source_lang: Source language code
            target_lang: Target language code
            
        Returns:
            Translated text
        """
        if not text or not text.strip():
            return text
        
        # Skip translation if source and target are the same
        if source_lang == target_lang:
            return text
        
        return self.backend.translate(text, source_lang, target_lang)
    
    def set_backend(self, backend: TranslatorBackend):
        """Change the translation backend.
        
        Args:
            backend: New translation backend
        """
        self.backend = backend
