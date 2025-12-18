# Testing Guide

This guide explains how to test the VideoTextboxPipeline implementation.

## Prerequisites

Install all dependencies:
```bash
pip install -r requirements.txt
```

## Verification Script

Run the automated verification script to check the implementation:

```bash
python verify_implementation.py
```

This will verify:
- Module structure
- Documentation files
- Python syntax
- Architecture design

## Architecture Demonstration

View the architecture and design:

```bash
python demo_architecture.py
```

## Manual Testing

### 1. Prepare Test Video

You'll need a video file with burned-in subtitles. For testing purposes:
- Duration: 10-30 seconds recommended
- Resolution: Any (720p or higher recommended)
- Subtitles: Should be visible in the bottom portion of the frame
- Languages: EN, UK, or RU for best results

### 2. Basic Pipeline Test

Test the basic pipeline functionality:

```bash
python -m video_textbox_pipeline input_video.mp4 output_video.mp4 --target-lang en
```

### 3. Test with Configuration

Create a test configuration:

```yaml
# test_config.yaml
target_lang: en
source_lang: ru
render_mode: rectangle
use_gpu: false
font_size: 36
```

Run with config:

```bash
python -m video_textbox_pipeline input.mp4 output.mp4 --config test_config.yaml
```

### 4. Test Individual Components

Use the component usage example:

```bash
cd examples
python component_usage.py
```

## Expected Behavior

### OCR Detection
- Should detect text in bottom 30% of frame by default
- Confidence threshold filters low-quality detections
- Returns text, bounding box, and confidence score

### Segmentation
- Groups frames with similar text (threshold: 0.8)
- Filters out segments with fewer than 3 frames
- Merges overlapping segments

### Language Detection
- Auto-detects from multiple text samples
- Returns ISO language code (en, uk, ru)
- Fallback to 'en' if detection fails

### Translation
- Skips if source == target language
- Uses Google Translate by default
- Supports custom backends

### Rendering
- Rectangle mode: Matches background color
- Inpaint mode: Removes original text first
- Centers translated text in original bbox

## Troubleshooting Tests

### Import Errors
```
ModuleNotFoundError: No module named 'cv2'
```
Solution: Install dependencies with `pip install -r requirements.txt`

### OCR Not Working
- Ensure PaddleOCR models are downloaded (happens on first run)
- Check if subtitles are in bottom 30% of frame
- Try adjusting `--bottom-ratio` parameter

### Poor Translation Quality
- Google Translate has usage limits
- Consider implementing a custom backend
- Check source language detection accuracy

### Rendering Issues
- Try different render modes (rectangle vs inpaint)
- Adjust font size with `--font-size`
- Provide custom font with `--font-path`

## Performance Testing

### CPU vs GPU
Compare processing times:
```bash
# CPU
time python -m video_textbox_pipeline input.mp4 output_cpu.mp4

# GPU (if available)
time python -m video_textbox_pipeline input.mp4 output_gpu.mp4 --use-gpu
```

### Different Render Modes
Compare quality and speed:
```bash
# Rectangle mode (faster)
time python -m video_textbox_pipeline input.mp4 output_rect.mp4 --render-mode rectangle

# Inpaint mode (slower, better quality)
time python -m video_textbox_pipeline input.mp4 output_inpaint.mp4 --render-mode inpaint
```

## Validation Checklist

- [ ] All modules import successfully
- [ ] CLI help displays correctly
- [ ] Configuration loading works
- [ ] OCR detects subtitle text
- [ ] Segments group correctly
- [ ] Language detection works
- [ ] Translation produces output
- [ ] Rendering applies subtitles
- [ ] Output video is playable
- [ ] No memory leaks on long videos

## Future Testing

Consider adding:
- Unit tests with pytest
- Mock objects for testing without dependencies
- Sample test videos in repository
- Automated CI/CD testing
- Performance benchmarks
- Integration tests
