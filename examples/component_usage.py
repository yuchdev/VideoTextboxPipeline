"""
Example of using individual pipeline components separately.

This demonstrates how to use OCR, grouping, translation, and rendering
components independently for more fine-grained control.
"""

import cv2
from video_textbox_pipeline.ocr import OCRDetector
from video_textbox_pipeline.grouping import SegmentGrouper
from video_textbox_pipeline.language import LanguageDetector
from video_textbox_pipeline.translation import Translator
from video_textbox_pipeline.rendering import SubtitleRenderer
from video_textbox_pipeline.utils import VideoReader


def main():
    # Initialize components
    ocr = OCRDetector(lang='en', use_gpu=False)
    grouper = SegmentGrouper(similarity_threshold=0.8, min_segment_frames=3)
    lang_detector = LanguageDetector()
    translator = Translator()
    renderer = SubtitleRenderer(mode='rectangle', font_size=32)
    
    # Step 1: Detect text in frames
    print("Step 1: Detecting text in frames...")
    frame_detections = []
    
    with VideoReader('input_video.mp4') as reader:
        for frame_num, frame in reader.read_frames():
            # Detect subtitles in this frame
            detections = ocr.detect_subtitle_region(frame, bottom_ratio=0.3)
            
            for text, bbox_points, confidence in detections:
                bbox = ocr.get_text_bbox(bbox_points)
                frame_detections.append((frame_num, text, bbox))
            
            # Process only first 100 frames for this example
            if frame_num >= 100:
                break
    
    print(f"Detected text in {len(frame_detections)} frames")
    
    # Step 2: Group into segments
    print("\nStep 2: Grouping frames into segments...")
    segments = grouper.group_detections(frame_detections)
    segments = grouper.merge_overlapping_segments(segments)
    
    print(f"Created {len(segments)} segments")
    
    # Step 3: Detect language
    print("\nStep 3: Detecting language...")
    texts = [seg.text for seg in segments]
    detected_lang = lang_detector.detect_from_segments(texts)
    print(f"Detected language: {lang_detector.get_language_name(detected_lang)}")
    
    # Step 4: Translate
    print("\nStep 4: Translating segments...")
    for segment in segments:
        original = segment.text
        translated = translator.translate(original, detected_lang, 'en')
        print(f"  '{original}' -> '{translated}'")
    
    # Step 5: Render (example for single frame)
    print("\nStep 5: Rendering example...")
    with VideoReader('input_video.mp4') as reader:
        frame = reader.get_frame(segments[0].start_frame)
        
        if frame is not None:
            # Render translated subtitle
            translated_text = translator.translate(segments[0].text, detected_lang, 'en')
            rendered_frame = renderer.render(
                frame,
                translated_text,
                segments[0].bbox
            )
            
            # Save example frame
            cv2.imwrite('rendered_example.jpg', rendered_frame)
            print("Saved rendered example to 'rendered_example.jpg'")


if __name__ == '__main__':
    main()
