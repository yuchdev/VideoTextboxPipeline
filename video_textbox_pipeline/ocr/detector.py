"""OCR detector using PaddleOCR for subtitle text detection."""

import numpy as np
from typing import List, Tuple, Optional
from paddleocr import PaddleOCR


class OCRDetector:
    """Detect text in video frames using PaddleOCR."""
    
    def __init__(self, lang: str = 'en', use_gpu: bool = False):
        """Initialize OCR detector.
        
        Args:
            lang: Language for OCR (default: 'en')
            use_gpu: Whether to use GPU acceleration (default: False)
        """
        self.ocr = PaddleOCR(
            use_angle_cls=True,
            lang=lang,
            use_gpu=use_gpu,
            show_log=False
        )
    
    def detect_text(self, frame: np.ndarray, 
                    min_confidence: float = 0.5) -> List[Tuple[str, List[List[int]], float]]:
        """Detect text in a frame.
        
        Args:
            frame: Input frame as numpy array (BGR format)
            min_confidence: Minimum confidence threshold for detection
            
        Returns:
            List of tuples: (text, bbox_points, confidence)
            bbox_points is a list of 4 corner points [[x1,y1], [x2,y2], [x3,y3], [x4,y4]]
        """
        result = self.ocr.ocr(frame, cls=True)
        
        if not result or not result[0]:
            return []
        
        detections = []
        for line in result[0]:
            bbox_points = line[0]  # List of 4 corner points
            text_info = line[1]  # (text, confidence)
            text = text_info[0]
            confidence = text_info[1]
            
            if confidence >= min_confidence:
                detections.append((text, bbox_points, confidence))
        
        return detections
    
    def detect_subtitle_region(self, frame: np.ndarray, 
                               bottom_ratio: float = 0.3,
                               min_confidence: float = 0.5) -> List[Tuple[str, List[List[int]], float]]:
        """Detect text specifically in the subtitle region (typically bottom of frame).
        
        Args:
            frame: Input frame as numpy array
            bottom_ratio: Ratio of frame height to consider as subtitle region (default: 0.3 = bottom 30%)
            min_confidence: Minimum confidence threshold
            
        Returns:
            List of tuples: (text, bbox_points, confidence)
        """
        all_detections = self.detect_text(frame, min_confidence)
        
        # Filter detections in bottom region
        frame_height = frame.shape[0]
        threshold_y = frame_height * (1 - bottom_ratio)
        
        subtitle_detections = []
        for text, bbox_points, confidence in all_detections:
            # Calculate center Y coordinate of bbox
            center_y = sum(point[1] for point in bbox_points) / 4
            
            if center_y >= threshold_y:
                subtitle_detections.append((text, bbox_points, confidence))
        
        return subtitle_detections
    
    def get_text_bbox(self, bbox_points: List[List[int]]) -> Tuple[int, int, int, int]:
        """Convert bbox points to (x, y, width, height) format.
        
        Args:
            bbox_points: List of 4 corner points [[x1,y1], [x2,y2], [x3,y3], [x4,y4]]
            
        Returns:
            Tuple of (x, y, width, height)
        """
        xs = [point[0] for point in bbox_points]
        ys = [point[1] for point in bbox_points]
        
        x = min(xs)
        y = min(ys)
        width = max(xs) - x
        height = max(ys) - y
        
        return (int(x), int(y), int(width), int(height))
