"""Segment grouper for detecting stable subtitle segments in video frames."""

import numpy as np
from typing import List, Dict, Any, Tuple
from ..utils.text_utils import calculate_text_similarity


class SubtitleSegment:
    """Represents a stable subtitle segment across multiple frames."""
    
    def __init__(self, start_frame: int, text: str, bbox: Tuple[int, int, int, int]):
        """Initialize subtitle segment.
        
        Args:
            start_frame: Starting frame number
            text: Detected text
            bbox: Bounding box as (x, y, width, height)
        """
        self.start_frame = start_frame
        self.end_frame = start_frame
        self.text = text
        self.bbox = bbox
        self.frame_count = 1
    
    def update(self, frame_num: int, text: str, bbox: Tuple[int, int, int, int]):
        """Update segment with new frame data.
        
        Args:
            frame_num: Current frame number
            text: Detected text
            bbox: Bounding box
        """
        self.end_frame = frame_num
        self.frame_count += 1
        # Update text to most recent (could also use voting/consensus)
        self.text = text
        # Average bbox position
        x1, y1, w1, h1 = self.bbox
        x2, y2, w2, h2 = bbox
        self.bbox = (
            int((x1 + x2) / 2),
            int((y1 + y2) / 2),
            int((w1 + w2) / 2),
            int((h1 + h2) / 2)
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert segment to dictionary.
        
        Returns:
            Dictionary representation of segment
        """
        return {
            'start_frame': self.start_frame,
            'end_frame': self.end_frame,
            'frame_count': self.frame_count,
            'text': self.text,
            'bbox': self.bbox
        }


class SegmentGrouper:
    """Group frames into stable subtitle segments."""
    
    def __init__(self, similarity_threshold: float = 0.8, 
                 min_segment_frames: int = 3,
                 max_gap_frames: int = 2):
        """Initialize segment grouper.
        
        Args:
            similarity_threshold: Text similarity threshold for grouping (0-1)
            min_segment_frames: Minimum frames for a valid segment
            max_gap_frames: Maximum gap between frames to still consider same segment
        """
        self.similarity_threshold = similarity_threshold
        self.min_segment_frames = min_segment_frames
        self.max_gap_frames = max_gap_frames
    
    def group_detections(self, frame_detections: List[Tuple[int, str, Tuple[int, int, int, int]]]) -> List[SubtitleSegment]:
        """Group frame detections into stable subtitle segments.
        
        Args:
            frame_detections: List of (frame_num, text, bbox) tuples
            
        Returns:
            List of SubtitleSegment objects
        """
        if not frame_detections:
            return []
        
        segments = []
        current_segment = None
        last_frame = -1
        
        for frame_num, text, bbox in frame_detections:
            if current_segment is None:
                # Start new segment
                current_segment = SubtitleSegment(frame_num, text, bbox)
                last_frame = frame_num
            else:
                # Check if this detection belongs to current segment
                similarity = calculate_text_similarity(text, current_segment.text)
                frame_gap = frame_num - last_frame
                
                if similarity >= self.similarity_threshold and frame_gap <= self.max_gap_frames + 1:
                    # Continue current segment
                    current_segment.update(frame_num, text, bbox)
                    last_frame = frame_num
                else:
                    # Finalize current segment and start new one
                    if current_segment.frame_count >= self.min_segment_frames:
                        segments.append(current_segment)
                    
                    current_segment = SubtitleSegment(frame_num, text, bbox)
                    last_frame = frame_num
        
        # Add final segment
        if current_segment and current_segment.frame_count >= self.min_segment_frames:
            segments.append(current_segment)
        
        return segments
    
    def merge_overlapping_segments(self, segments: List[SubtitleSegment]) -> List[SubtitleSegment]:
        """Merge segments that overlap in time.
        
        Args:
            segments: List of subtitle segments
            
        Returns:
            List of merged segments
        """
        if not segments:
            return []
        
        # Sort segments by start frame
        sorted_segments = sorted(segments, key=lambda s: s.start_frame)
        
        merged = [sorted_segments[0]]
        
        for segment in sorted_segments[1:]:
            last_merged = merged[-1]
            
            # Check for overlap or close proximity
            if segment.start_frame <= last_merged.end_frame + self.max_gap_frames:
                # Extend the last merged segment
                last_merged.end_frame = max(last_merged.end_frame, segment.end_frame)
                last_merged.frame_count = last_merged.end_frame - last_merged.start_frame + 1
                # Prefer longer or more recent text
                if len(segment.text) > len(last_merged.text):
                    last_merged.text = segment.text
            else:
                # Add as new merged segment
                merged.append(segment)
        
        return merged
