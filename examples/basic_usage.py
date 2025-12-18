"""
Basic usage example for VideoTextboxPipeline.

This example demonstrates the simplest way to use the pipeline
to translate video subtitles from auto-detected language to English.
"""

from video_textbox_pipeline import SubtitleTranslationPipeline


def main():
    # Initialize the pipeline with basic settings
    pipeline = SubtitleTranslationPipeline(
        target_lang='en',  # Translate to English
        source_lang=None,  # Auto-detect source language
        render_mode='rectangle',  # Use rectangle rendering mode
        use_gpu=False  # Use CPU for OCR
    )
    
    # Process the video
    print("Processing video...")
    stats = pipeline.process_video(
        input_path='input_video.mp4',
        output_path='output_video.mp4'
    )
    
    # Print statistics
    print("\nProcessing Complete!")
    print(f"Segments detected: {stats['segments']}")
    print(f"Frames processed: {stats['frames_processed']}")
    print(f"Source language: {stats['source_language']}")
    print(f"Target language: {stats['target_language']}")


if __name__ == '__main__':
    main()
