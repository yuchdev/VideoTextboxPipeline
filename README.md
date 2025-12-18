# VideoTextboxPipeline

Automated pipeline for translating burned-in video subtitles. The project detects on-screen subtitle text via OCR, groups frames into stable subtitle segments, auto-detects source language (EN/UK/RU), translates text using a pluggable backend, and renders translated subtitles back into the video.

## Features

- **OCR Detection**: Detect on-screen subtitle text using PaddleOCR
- **Intelligent Grouping**: Group frames into stable subtitle segments
- **Language Detection**: Auto-detect source language (EN/UK/RU)
- **Pluggable Translation**: Translate text using pluggable backend architecture
- **Dual Rendering Modes**:
  - **Rectangle Mode**: Background-matched rectangle rendering
  - **Inpaint Mode**: Text removal via inpainting (optional)
- **Modular Design**: Easy to extend with custom components

## Tech Stack

- Python 3.7+
- PaddleOCR - OCR engine
- OpenCV - Video processing
- Pillow - Image manipulation
- ffmpeg - Video encoding/decoding
- langdetect - Language detection
- googletrans - Translation backend

## Installation

### Prerequisites

```bash
# Install system dependencies (Ubuntu/Debian)
sudo apt-get update
sudo apt-get install -y ffmpeg libsm6 libxext6 libxrender-dev

# For other systems, ensure ffmpeg is installed
```

### Install Package

```bash
# Clone the repository
git clone https://github.com/yuchdev/VideoTextboxPipeline.git
cd VideoTextboxPipeline

# Install dependencies
pip install -r requirements.txt
```

## Quick Start

### Basic Usage

```bash
# Translate video from auto-detected language to English
python -m video_textbox_pipeline.cli input.mp4 output.mp4 --target-lang en
```

### Advanced Usage

```bash
# Translate from Russian to English with inpainting mode
python -m video_textbox_pipeline.cli input.mp4 output.mp4 \
    --source-lang ru \
    --target-lang en \
    --render-mode inpaint

# Use custom font and settings
python -m video_textbox_pipeline.cli input.mp4 output.mp4 \
    --target-lang en \
    --font-path /path/to/font.ttf \
    --font-size 40 \
    --similarity-threshold 0.85
```

### Using Configuration File

Create a `config.yaml`:

```yaml
target_lang: en
source_lang: ru
ocr_lang: en
use_gpu: false
min_confidence: 0.5
bottom_ratio: 0.3
similarity_threshold: 0.8
min_segment_frames: 3
max_gap_frames: 2
render_mode: rectangle
font_path: null
font_size: 32
text_color: [255, 255, 255]
padding: 10
output_codec: mp4v
```

Run with config:

```bash
python -m video_textbox_pipeline.cli input.mp4 output.mp4 --config config.yaml
```

## Python API

### Basic Pipeline Usage

```python
from video_textbox_pipeline import SubtitleTranslationPipeline

# Initialize pipeline
pipeline = SubtitleTranslationPipeline(
    target_lang='en',
    source_lang='ru',  # or None for auto-detect
    render_mode='rectangle',  # or 'inpaint'
    use_gpu=False
)

# Process video
stats = pipeline.process_video('input.mp4', 'output.mp4')
print(f"Processed {stats['segments']} subtitle segments")
```

### Custom Translation Backend

```python
from video_textbox_pipeline.translation import Translator
from video_textbox_pipeline.translation.backends import TranslatorBackend

# Create custom backend
class MyCustomBackend(TranslatorBackend):
    def translate(self, text, source_lang, target_lang):
        # Your custom translation logic
        return translated_text

# Use custom backend
translator = Translator(backend=MyCustomBackend())
pipeline.translator = translator
```

### Individual Components

```python
from video_textbox_pipeline.ocr import OCRDetector
from video_textbox_pipeline.grouping import SegmentGrouper
from video_textbox_pipeline.language import LanguageDetector
from video_textbox_pipeline.rendering import SubtitleRenderer

# OCR Detection
ocr = OCRDetector(lang='en', use_gpu=False)
detections = ocr.detect_subtitle_region(frame)

# Frame Grouping
grouper = SegmentGrouper(similarity_threshold=0.8)
segments = grouper.group_detections(frame_detections)

# Language Detection
detector = LanguageDetector()
lang = detector.detect_language(text)

# Rendering
renderer = SubtitleRenderer(mode='rectangle', font_size=32)
rendered_frame = renderer.render(frame, text, bbox)
```

## Architecture

### Modular Design

```
video_textbox_pipeline/
├── __init__.py           # Main package interface
├── pipeline.py           # Pipeline orchestrator
├── config.py             # Configuration management
├── cli.py               # Command-line interface
├── ocr/                 # OCR detection module
│   ├── __init__.py
│   └── detector.py      # PaddleOCR wrapper
├── grouping/            # Frame grouping module
│   ├── __init__.py
│   └── segment_grouper.py  # Segment detection
├── language/            # Language detection module
│   ├── __init__.py
│   └── detector.py      # Language detection
├── translation/         # Translation module
│   ├── __init__.py
│   ├── translator.py    # Main translator
│   └── backends.py      # Pluggable backends
├── rendering/           # Rendering module
│   ├── __init__.py
│   └── renderer.py      # Subtitle rendering
└── utils/              # Utility functions
    ├── __init__.py
    ├── video_utils.py   # Video I/O
    └── text_utils.py    # Text processing
```

### Pipeline Flow

1. **OCR Detection**: Extract text from video frames using PaddleOCR
2. **Segmentation**: Group consecutive frames with similar text into segments
3. **Language Detection**: Auto-detect source language from extracted text
4. **Translation**: Translate segments using pluggable backend
5. **Rendering**: Apply translated subtitles to video frames

## Configuration Options

| Option | Description | Default |
|--------|-------------|---------|
| `target_lang` | Target language code | `en` |
| `source_lang` | Source language (None for auto-detect) | `None` |
| `ocr_lang` | OCR detection language | `en` |
| `use_gpu` | Use GPU for OCR | `False` |
| `render_mode` | Rendering mode (rectangle/inpaint) | `rectangle` |
| `similarity_threshold` | Text similarity for grouping | `0.8` |
| `min_segment_frames` | Minimum frames for valid segment | `3` |
| `font_size` | Font size for rendered text | `32` |

## Supported Languages

- **English (en)**: Full support
- **Ukrainian (uk)**: Full support
- **Russian (ru)**: Full support
- Other languages supported by PaddleOCR and translation backend

## Rendering Modes

### Rectangle Mode (Default)

- Extracts dominant background color from original subtitle region
- Draws filled rectangle with matched background color
- Renders translated text on top
- Fast and reliable

### Inpaint Mode

- Uses OpenCV inpainting to remove original text
- Renders translated text on cleaned background
- More visually seamless but slower
- May not work well with complex backgrounds

## Performance Tips

1. **GPU Acceleration**: Use `--use-gpu` for faster OCR on systems with CUDA
2. **Segment Tuning**: Adjust `similarity_threshold` and `min_segment_frames` for better grouping
3. **Font Selection**: Use appropriate fonts for target language
4. **Resolution**: Process at native resolution for best OCR results

## Troubleshooting

### OCR Not Detecting Text

- Ensure subtitles are in bottom 30% of frame (adjust `bottom_ratio`)
- Check OCR language matches video (`--ocr-lang`)
- Try lowering `min_confidence` threshold

### Incorrect Language Detection

- Manually specify source language with `--source-lang`
- Ensure sufficient text for accurate detection

### Poor Rendering Quality

- Use `rectangle` mode for complex backgrounds
- Adjust `font_size` to match original subtitles
- Provide custom font with `--font-path`

## Contributing

Contributions are welcome! Please follow these guidelines:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

MIT License - See LICENSE file for details

## Acknowledgments

- PaddleOCR team for excellent OCR engine
- OpenCV community for computer vision tools
- Contributors and users of this project

## Future Enhancements

- Support for more translation backends (DeepL, Azure, etc.)
- Batch processing for multiple videos
- Web interface for easier usage
- Support for SRT/subtitle file export
- Advanced subtitle positioning detection
- Multi-language subtitle support in single video 
