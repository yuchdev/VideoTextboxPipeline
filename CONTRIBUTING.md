# Contributing to VideoTextboxPipeline

Thank you for your interest in contributing to VideoTextboxPipeline! This document provides guidelines for contributing to the project.

## Development Setup

1. Clone the repository:
```bash
git clone https://github.com/yuchdev/VideoTextboxPipeline.git
cd VideoTextboxPipeline
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Install in development mode:
```bash
pip install -e .
```

## Code Structure

The project follows a modular architecture:

- `video_textbox_pipeline/` - Main package
  - `ocr/` - OCR detection module
  - `grouping/` - Frame grouping module
  - `language/` - Language detection module
  - `translation/` - Translation module with pluggable backends
  - `rendering/` - Subtitle rendering module
  - `utils/` - Utility functions

## Adding New Features

### Adding a Translation Backend

1. Create a new class that inherits from `TranslatorBackend`:

```python
from video_textbox_pipeline.translation.backends import TranslatorBackend

class MyCustomBackend(TranslatorBackend):
    def translate(self, text: str, source_lang: str, target_lang: str) -> str:
        # Your translation logic
        return translated_text
```

2. Update `translation/__init__.py` to export your backend

3. Add documentation and examples

### Adding a Rendering Mode

1. Extend `SubtitleRenderer` class in `rendering/renderer.py`
2. Add a new rendering method following the pattern of existing modes
3. Update the mode constants and render method
4. Add tests and documentation

## Code Style

- Follow PEP 8 style guidelines
- Use type hints where appropriate
- Write docstrings for all public functions and classes
- Keep functions focused and single-purpose

## Testing

Currently, the project uses manual testing. Future contributions should include:
- Unit tests for individual components
- Integration tests for the pipeline
- Example test videos with known outputs

## Documentation

- Update README.md for user-facing changes
- Update docstrings for API changes
- Add examples for new features
- Update configuration documentation

## Pull Request Process

1. Create a feature branch from `main`
2. Make your changes
3. Test your changes thoroughly
4. Update documentation
5. Submit a pull request with a clear description

## Bug Reports

When reporting bugs, please include:
- Description of the issue
- Steps to reproduce
- Expected behavior
- Actual behavior
- System information (OS, Python version, etc.)
- Sample video if relevant (or description)

## Feature Requests

We welcome feature requests! Please:
- Check if the feature already exists or is planned
- Describe the use case
- Explain why it would be valuable
- Suggest a potential implementation if possible

## Code of Conduct

- Be respectful and inclusive
- Accept constructive criticism
- Focus on what's best for the project
- Show empathy towards others

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
