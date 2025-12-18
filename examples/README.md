# Examples

This directory contains example scripts demonstrating various usage patterns of the VideoTextboxPipeline.

## Available Examples

### 1. Basic Usage (`basic_usage.py`)

The simplest way to use the pipeline with default settings.

```bash
python basic_usage.py
```

Features:
- Auto-detect source language
- Translate to English
- Rectangle rendering mode
- CPU-based OCR

### 2. Custom Backend (`custom_backend.py`)

Demonstrates how to create and integrate a custom translation backend.

```bash
python custom_backend.py
```

Features:
- Custom translation backend implementation
- Inpainting rendering mode
- Backend swapping

### 3. Component Usage (`component_usage.py`)

Shows how to use individual pipeline components separately for fine-grained control.

```bash
python component_usage.py
```

Features:
- Independent component usage
- OCR detection
- Segment grouping
- Language detection
- Translation
- Rendering

## Running Examples

1. Ensure you have installed the package and dependencies:
```bash
pip install -r ../requirements.txt
```

2. Prepare a test video with burned-in subtitles

3. Update the input/output paths in the example scripts

4. Run the desired example:
```bash
python examples/basic_usage.py
```

## Creating Your Own Examples

Feel free to modify these examples or create new ones based on your specific needs. The pipeline is designed to be flexible and extensible.
