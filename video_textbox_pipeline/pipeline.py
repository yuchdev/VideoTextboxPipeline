"""Main pipeline orchestrator for video subtitle translation."""

import cv2
import numpy as np
from typing import Optional, List, Dict, Any
from tqdm import tqdm

from .ocr import OCRDetector
from .grouping import SegmentGrouper
from .language import LanguageDetector
from .translation import Translator
from .rendering import SubtitleRenderer
from .utils import VideoReader, VideoWriter


class SubtitleTranslationPipeline:
    """Main pipeline for translating burned-in video subtitles."""
    
    def __init__(self,
                 target_lang: str = 'en',
                 source_lang: Optional[str] = None,
                 render_mode: str = 'rectangle',
                 ocr_lang: str = 'en',
                 use_gpu: bool = False,
                 similarity_threshold: float = 0.8,
                 min_segment_frames: int = 3,
                 font_path: Optional[str] = None,
                 font_size: int = 32):
        """Initialize the subtitle translation pipeline.
        
        Args:
            target_lang: Target language for translation
            source_lang: Source language (if None, auto-detect)
            render_mode: Rendering mode ('rectangle' or 'inpaint')
            ocr_lang: Language for OCR detection
            use_gpu: Whether to use GPU for OCR
            similarity_threshold: Text similarity threshold for segment grouping
            min_segment_frames: Minimum frames for valid subtitle segment
            font_path: Path to custom font file
            font_size: Font size for rendered subtitles
        """
        self.target_lang = target_lang
        self.source_lang = source_lang
        
        # Initialize components
        self.ocr_detector = OCRDetector(lang=ocr_lang, use_gpu=use_gpu)
        self.segment_grouper = SegmentGrouper(
            similarity_threshold=similarity_threshold,
            min_segment_frames=min_segment_frames
        )
        self.language_detector = LanguageDetector()
        self.translator = Translator()
        self.renderer = SubtitleRenderer(mode=render_mode, font_path=font_path, font_size=font_size)
    
    def process_video(self, input_path: str, output_path: str, 
                     progress_callback: Optional[callable] = None) -> Dict[str, Any]:
        """Process video and translate subtitles.
        
        Args:
            input_path: Path to input video file
            output_path: Path to output video file
            progress_callback: Optional callback for progress updates
            
        Returns:
            Dictionary with processing statistics
        """
        print(f"Processing video: {input_path}")
        
        # Step 1: Extract frames and detect text
        print("Step 1: Detecting subtitles in frames...")
        frame_detections = self._detect_subtitles_in_video(input_path, progress_callback)
        
        if not frame_detections:
            print("No subtitles detected in video.")
            return {'segments': 0, 'frames_processed': 0}
        
        # Step 2: Group detections into segments
        print("Step 2: Grouping frames into subtitle segments...")
        segments = self.segment_grouper.group_detections(frame_detections)
        segments = self.segment_grouper.merge_overlapping_segments(segments)
        
        print(f"Found {len(segments)} subtitle segments")
        
        # Step 3: Detect source language if not provided
        if self.source_lang is None:
            print("Step 3: Auto-detecting source language...")
            texts = [seg.text for seg in segments]
            detected_lang = self.language_detector.detect_from_segments(texts)
            self.source_lang = detected_lang or 'en'
            print(f"Detected language: {self.language_detector.get_language_name(self.source_lang)}")
        else:
            print(f"Step 3: Using provided source language: {self.source_lang}")
        
        # Step 4: Translate segments
        print("Step 4: Translating subtitles...")
        translated_segments = self._translate_segments(segments)
        
        # Step 5: Render translated subtitles
        print("Step 5: Rendering translated subtitles to video...")
        stats = self._render_video(input_path, output_path, translated_segments, progress_callback)
        
        print(f"Processing complete! Output saved to: {output_path}")
        
        return {
            'segments': len(segments),
            'frames_processed': stats['frames_processed'],
            'source_language': self.source_lang,
            'target_language': self.target_lang
        }
    
    def _detect_subtitles_in_video(self, video_path: str, 
                                   progress_callback: Optional[callable] = None) -> List[tuple]:
        """Detect subtitles in all video frames.
        
        Args:
            video_path: Path to video file
            progress_callback: Optional progress callback
            
        Returns:
            List of (frame_num, text, bbox) tuples
        """
        detections = []
        
        with VideoReader(video_path) as reader:
            frame_iterator = tqdm(reader.read_frames(), total=reader.frame_count, desc="Detecting")
            
            for frame_num, frame in frame_iterator:
                # Detect subtitles in bottom region
                subtitle_detections = self.ocr_detector.detect_subtitle_region(frame)
                
                # Combine all detected text in this frame
                for text, bbox_points, confidence in subtitle_detections:
                    bbox = self.ocr_detector.get_text_bbox(bbox_points)
                    detections.append((frame_num, text, bbox))
                
                if progress_callback:
                    progress_callback('detect', frame_num, reader.frame_count)
        
        return detections
    
    def _translate_segments(self, segments: List) -> List[Dict[str, Any]]:
        """Translate all subtitle segments.
        
        Args:
            segments: List of SubtitleSegment objects
            
        Returns:
            List of dictionaries with original and translated text
        """
        translated = []
        
        for segment in tqdm(segments, desc="Translating"):
            original_text = segment.text
            translated_text = self.translator.translate(
                original_text,
                self.source_lang,
                self.target_lang
            )
            
            translated.append({
                'start_frame': segment.start_frame,
                'end_frame': segment.end_frame,
                'bbox': segment.bbox,
                'original_text': original_text,
                'translated_text': translated_text
            })
        
        return translated
    
    def _render_video(self, input_path: str, output_path: str,
                     translated_segments: List[Dict[str, Any]],
                     progress_callback: Optional[callable] = None) -> Dict[str, int]:
        """Render video with translated subtitles.
        
        Args:
            input_path: Path to input video
            output_path: Path to output video
            translated_segments: List of translated segment dictionaries
            progress_callback: Optional progress callback
            
        Returns:
            Dictionary with rendering statistics
        """
        # Create segment lookup for fast access
        segment_map = {}
        for seg in translated_segments:
            for frame_num in range(seg['start_frame'], seg['end_frame'] + 1):
                segment_map[frame_num] = seg
        
        frames_processed = 0
        
        with VideoReader(input_path) as reader:
            with VideoWriter(output_path, reader.fps, reader.width, reader.height) as writer:
                frame_iterator = tqdm(reader.read_frames(), total=reader.frame_count, desc="Rendering")
                
                for frame_num, frame in frame_iterator:
                    # Check if this frame has a subtitle
                    if frame_num in segment_map:
                        seg = segment_map[frame_num]
                        # Render translated subtitle
                        frame = self.renderer.render(
                            frame,
                            seg['translated_text'],
                            seg['bbox']
                        )
                    
                    writer.write_frame(frame)
                    frames_processed += 1
                    
                    if progress_callback:
                        progress_callback('render', frame_num, reader.frame_count)
        
        return {'frames_processed': frames_processed}
