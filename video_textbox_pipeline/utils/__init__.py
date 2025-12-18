"""Utility functions and helpers."""

from .video_utils import VideoReader, VideoWriter
from .text_utils import calculate_text_similarity, extract_dominant_color

__all__ = ['VideoReader', 'VideoWriter', 'calculate_text_similarity', 'extract_dominant_color']
