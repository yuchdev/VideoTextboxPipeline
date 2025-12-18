"""Text processing utilities."""

import difflib
import numpy as np
from typing import Tuple
from collections import Counter


def calculate_text_similarity(text1: str, text2: str) -> float:
    """Calculate similarity between two text strings.
    
    Args:
        text1: First text string
        text2: Second text string
        
    Returns:
        Similarity score between 0 and 1
    """
    if not text1 or not text2:
        return 0.0
    
    # Use SequenceMatcher for similarity
    return difflib.SequenceMatcher(None, text1, text2).ratio()


def extract_dominant_color(image: np.ndarray, bbox: Tuple[int, int, int, int]) -> Tuple[int, int, int]:
    """Extract dominant color from a region of an image.
    
    Args:
        image: Input image array (BGR format)
        bbox: Bounding box as (x, y, width, height)
        
    Returns:
        Dominant color as (B, G, R) tuple
    """
    x, y, w, h = bbox
    
    # Extract region of interest
    roi = image[y:y+h, x:x+w]
    
    # Reshape to list of pixels
    pixels = roi.reshape(-1, 3)
    
    # Find most common color
    pixels_list = [tuple(pixel) for pixel in pixels]
    color_counts = Counter(pixels_list)
    dominant_color = color_counts.most_common(1)[0][0]
    
    return dominant_color


def normalize_text(text: str) -> str:
    """Normalize text for comparison.
    
    Args:
        text: Input text string
        
    Returns:
        Normalized text string
    """
    return text.strip().lower()
