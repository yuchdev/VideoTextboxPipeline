#!/usr/bin/env python
"""Command-line interface for the Video Textbox Pipeline."""

import argparse
import sys
from pathlib import Path

from video_textbox_pipeline import SubtitleTranslationPipeline
from video_textbox_pipeline.config import PipelineConfig


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description='Automated pipeline for translating burned-in video subtitles',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Translate video from auto-detected language to English
  python -m video_textbox_pipeline.cli input.mp4 output.mp4 --target-lang en
  
  # Translate from Russian to English with inpainting mode
  python -m video_textbox_pipeline.cli input.mp4 output.mp4 --source-lang ru --target-lang en --render-mode inpaint
  
  # Use custom configuration file
  python -m video_textbox_pipeline.cli input.mp4 output.mp4 --config config.yaml
        """
    )
    
    parser.add_argument('input', type=str, help='Input video file path')
    parser.add_argument('output', type=str, help='Output video file path')
    
    # Language options
    parser.add_argument('--source-lang', type=str, default=None,
                       help='Source language code (auto-detect if not provided)')
    parser.add_argument('--target-lang', type=str, default='en',
                       help='Target language code (default: en)')
    
    # OCR options
    parser.add_argument('--ocr-lang', type=str, default='en',
                       help='OCR language (default: en)')
    parser.add_argument('--use-gpu', action='store_true',
                       help='Use GPU for OCR (default: False)')
    
    # Rendering options
    parser.add_argument('--render-mode', type=str, choices=['rectangle', 'inpaint'],
                       default='rectangle',
                       help='Rendering mode (default: rectangle)')
    parser.add_argument('--font-path', type=str, default=None,
                       help='Path to custom font file')
    parser.add_argument('--font-size', type=int, default=32,
                       help='Font size for rendered text (default: 32)')
    
    # Advanced options
    parser.add_argument('--similarity-threshold', type=float, default=0.8,
                       help='Text similarity threshold for grouping (default: 0.8)')
    parser.add_argument('--min-segment-frames', type=int, default=3,
                       help='Minimum frames for valid segment (default: 3)')
    
    # Configuration file
    parser.add_argument('--config', type=str, default=None,
                       help='Path to YAML configuration file')
    
    # Other options
    parser.add_argument('--save-config', type=str, default=None,
                       help='Save current configuration to YAML file')
    
    args = parser.parse_args()
    
    # Validate input file
    if not Path(args.input).exists():
        print(f"Error: Input file not found: {args.input}", file=sys.stderr)
        return 1
    
    # Load or create configuration
    if args.config:
        print(f"Loading configuration from: {args.config}")
        config = PipelineConfig.from_yaml(args.config)
    else:
        config = PipelineConfig(
            target_lang=args.target_lang,
            source_lang=args.source_lang,
            ocr_lang=args.ocr_lang,
            use_gpu=args.use_gpu,
            render_mode=args.render_mode,
            font_path=args.font_path,
            font_size=args.font_size,
            similarity_threshold=args.similarity_threshold,
            min_segment_frames=args.min_segment_frames
        )
    
    # Save configuration if requested
    if args.save_config:
        print(f"Saving configuration to: {args.save_config}")
        config.to_yaml(args.save_config)
    
    # Initialize pipeline
    print("Initializing pipeline...")
    pipeline = SubtitleTranslationPipeline(
        target_lang=config.target_lang,
        source_lang=config.source_lang,
        render_mode=config.render_mode,
        ocr_lang=config.ocr_lang,
        use_gpu=config.use_gpu,
        similarity_threshold=config.similarity_threshold,
        min_segment_frames=config.min_segment_frames,
        font_path=config.font_path,
        font_size=config.font_size
    )
    
    # Process video
    try:
        stats = pipeline.process_video(args.input, args.output)
        
        print("\n" + "="*50)
        print("Processing Statistics:")
        print(f"  Segments detected: {stats['segments']}")
        print(f"  Frames processed: {stats['frames_processed']}")
        print(f"  Source language: {stats['source_language']}")
        print(f"  Target language: {stats['target_language']}")
        print("="*50)
        
        return 0
        
    except Exception as e:
        print(f"\nError processing video: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())
