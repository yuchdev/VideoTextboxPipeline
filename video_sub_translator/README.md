# video-sub-translator

Production-quality Python pipeline for translating burned-in video subtitles.

## Features

- **OCR Detection**: Detects burned-in subtitles using PaddleOCR
- **Intelligent Segmentation**: Groups frames into stable subtitle segments
- **Language Detection**: Auto-detects source language (EN/UK/RU)
- **Pluggable Translation**: Supports multiple translation backends
- **Dual Rendering Modes**:
  - **Mode B (default)**: Background-matched rectangle overlay
  - **Mode A (optional)**: Text-mask + inpainting + translated text
- **Audio Preservation**: Re-encodes video while preserving original audio

## Installation

### Prerequisites

Ensure ffmpeg is installed and available in PATH:

```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install -y ffmpeg

# macOS
brew install ffmpeg

# Windows
# Download from https://ffmpeg.org/download.html
```

### Install Package

```bash
# Clone repository
git clone https://github.com/yuchdev/VideoTextboxPipeline.git
cd VideoTextboxPipeline/video_sub_translator

# Install with dev dependencies
pip install -e ".[dev]"

# Or install without dev dependencies
pip install -e .
```

### Verify Installation

```bash
vst doctor
```

## Quick Start

### Basic Usage

```bash
# Translate video with auto-detected source language
vst run -i input.mp4 -o output.mp4

# Specify target language
vst run -i input.mp4 -o output.mp4 --config config.yaml
```

### Configuration File

Create `config.yaml`:

```yaml
input:
  video_path: input.mp4
output:
  video_path: output.mp4
  
fps_sampling:
  scan_fps: 2
  keyframe_interval: 30

subtitle_roi:
  bottom_percent: 0.3
  min_width_ratio: 0.2
  max_height_ratio: 0.2

tracking:
  redetect_interval: 10
  smoothing_window: 5

ocr:
  languages: ['en', 'ch']
  det_threshold: 0.6
  rec_threshold: 0.6

segmenter:
  min_duration_frames: 3
  similarity_threshold: 0.85
  max_gap_frames: 2

translation:
  backend: dummy
  target_lang: en
  source_lang: null  # auto-detect
  max_line_length: 42

renderer:
  mode: overlay  # or 'inpaint'
  padding: 10
  corner_radius: 5
  opacity: 0.9
  outline_width: 2
  font_size: 32
  font_paths:
    - /usr/share/fonts/truetype/noto/NotoSans-Regular.ttf
    - /usr/share/fonts/truetype/dejavu/DejaVuSans.ttf

ffmpeg:
  crf: 23
  preset: medium
```

## CLI Commands

### Run Full Pipeline

```bash
vst run -i input.mp4 -o output.mp4 --config config.yaml
```

### Debug Commands

```bash
# Detect subtitle regions (debug)
vst detect -i input.mp4 --dump debug.json

# OCR text extraction (debug)
vst ocr -i input.mp4 --dump ocr.json

# Translate segments
vst translate --segments segments.json --to uk

# Render only
vst render -i input.mp4 --segments segments.json -o output.mp4

# System check
vst doctor
```

## Architecture

### Pipeline Flow

1. **Frame Sampling**: Extract frames at configured FPS
2. **Subtitle Detection**: Detect subtitle regions in bottom portion of frames
3. **Tracking**: Track subtitle bounding boxes across frames
4. **OCR**: Extract text from detected regions
5. **Segmentation**: Group frames into stable subtitle segments
6. **Language Detection**: Auto-detect source language
7. **Translation**: Translate text using configured backend
8. **Rendering**: Apply translated subtitles (overlay or inpaint mode)
9. **Video Encoding**: Re-encode video with translated subtitles

### Module Structure

```
video_sub_translator/
├── src/video_sub_translator/
│   ├── __init__.py
│   ├── cli.py              # CLI interface
│   ├── config.py           # Configuration
│   ├── logging.py          # Logging setup
│   ├── ffmpeg.py           # FFmpeg wrapper
│   ├── models.py           # Pydantic models
│   ├── pipeline.py         # Pipeline orchestrator
│   ├── ocr/                # OCR module
│   ├── detect/             # Detection & tracking
│   ├── translate/          # Translation backends
│   ├── render/             # Rendering modes
│   └── utils/              # Utilities
├── tests/                  # Test suite
├── docs/                   # Documentation
└── pyproject.toml          # Project config
```

## Supported Languages

- English (en)
- Ukrainian (uk) - with special character detection
- Russian (ru)

## Rendering Modes

### Overlay Mode (Mode B - Default)

- Samples border pixels to extract background color
- Draws filled rectangle with matched background
- Renders translated text on top
- **Pros**: Fast, reliable, works with all backgrounds
- **Cons**: May not perfectly match complex backgrounds

### Inpaint Mode (Mode A - Optional)

- Creates mask for original text area
- Uses OpenCV inpainting to remove text
- Renders translated text on cleaned background
- **Pros**: More visually seamless
- **Cons**: Slower, may artifacts with complex backgrounds

## Limitations

- Requires burned-in subtitles (does not use existing subtitle tracks)
- Best results with clean, high-contrast subtitles
- Language detection requires sufficient text
- Inpaint mode may struggle with complex backgrounds

## Troubleshooting

See [docs/troubleshooting.md](docs/troubleshooting.md) for:
- PaddleOCR installation issues
- ffmpeg not found errors
- Missing fonts / Cyrillic rendering issues
- Jittery bounding box problems
- Wrong region detection tuning

## Roadmap

- [ ] Deep learning inpainting models
- [ ] More translation backends (DeepL, Azure, etc.)
- [ ] GPU acceleration for rendering
- [ ] Batch video processing
- [ ] SRT subtitle file export
- [ ] Multi-language subtitle support in single video

## Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md).

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Acknowledgments

- PaddleOCR team for excellent OCR engine
- OpenCV community for computer vision tools
