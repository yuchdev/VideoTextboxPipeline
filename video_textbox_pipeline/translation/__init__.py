"""Translation module with pluggable backend architecture."""

from .translator import Translator
from .backends import GoogleTranslatorBackend

__all__ = ['Translator', 'GoogleTranslatorBackend']
