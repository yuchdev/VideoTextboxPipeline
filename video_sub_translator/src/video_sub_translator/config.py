"""Configuration management for video subtitle translator."""

from pathlib import Path
from typing import Any, Optional

import yaml
from pydantic import BaseModel, Field


class InputConfig(BaseModel):
    """Input configuration."""

    video_path: Optional[str] = Field(default=None, description="Input video path")


class OutputConfig(BaseModel):
    """Output configuration."""

    video_path: Optional[str] = Field(default=None, description="Output video path")
    debug_dir: Optional[str] = Field(default=None, description="Debug output directory")


class FpsSamplingConfig(BaseModel):
    """FPS sampling configuration."""

    scan_fps: float = Field(default=2.0, gt=0, description="FPS for frame sampling")
    keyframe_interval: int = Field(default=30, gt=0, description="Keyframe interval in frames")


class SubtitleRoiConfig(BaseModel):
    """Subtitle region of interest configuration."""

    bottom_percent: float = Field(
        default=0.3, gt=0, le=1.0, description="Bottom percentage of frame for subtitle detection"
    )
    min_width_ratio: float = Field(
        default=0.2, gt=0, le=1.0, description="Minimum width ratio for subtitle bbox"
    )
    max_height_ratio: float = Field(
        default=0.2, gt=0, le=1.0, description="Maximum height ratio for subtitle bbox"
    )


class TrackingConfig(BaseModel):
    """Tracking configuration."""

    redetect_interval: int = Field(
        default=10, gt=0, description="Re-detect subtitle region every N frames"
    )
    smoothing_window: int = Field(
        default=5, gt=0, description="Smoothing window size for bbox coordinates"
    )


class OcrConfig(BaseModel):
    """OCR configuration."""

    languages: list[str] = Field(
        default_factory=lambda: ["en", "ch"], description="OCR languages"
    )
    det_threshold: float = Field(
        default=0.6, ge=0, le=1.0, description="Detection threshold"
    )
    rec_threshold: float = Field(
        default=0.6, ge=0, le=1.0, description="Recognition threshold"
    )
    use_gpu: bool = Field(default=False, description="Use GPU for OCR")


class SegmenterConfig(BaseModel):
    """Segmenter configuration."""

    min_duration_frames: int = Field(
        default=3, gt=0, description="Minimum frames for valid segment"
    )
    similarity_threshold: float = Field(
        default=0.85, ge=0, le=1.0, description="Text similarity threshold for grouping"
    )
    max_gap_frames: int = Field(
        default=2, ge=0, description="Maximum gap frames between segments"
    )


class TranslationConfig(BaseModel):
    """Translation configuration."""

    backend: str = Field(default="dummy", description="Translation backend name")
    target_lang: str = Field(default="en", description="Target language code")
    source_lang: Optional[str] = Field(default=None, description="Source language (None=auto)")
    max_line_length: int = Field(default=42, gt=0, description="Maximum line length target")
    glossary_path: Optional[str] = Field(default=None, description="Glossary file path")
    openai_api_key: Optional[str] = Field(default=None, description="OpenAI API key")


class RendererConfig(BaseModel):
    """Renderer configuration."""

    mode: str = Field(default="overlay", description="Rendering mode: overlay or inpaint")
    padding: int = Field(default=10, ge=0, description="Padding around text")
    corner_radius: int = Field(default=5, ge=0, description="Corner radius for rectangles")
    opacity: float = Field(default=0.9, ge=0, le=1.0, description="Background opacity")
    outline_width: int = Field(default=2, ge=0, description="Text outline width")
    font_size: int = Field(default=32, gt=0, description="Base font size")
    font_paths: list[str] = Field(
        default_factory=lambda: [
            "/usr/share/fonts/truetype/noto/NotoSans-Regular.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
            "/System/Library/Fonts/Helvetica.ttc",
            "C:\\Windows\\Fonts\\arial.ttf",
        ],
        description="Font file paths to try",
    )
    text_color: tuple[int, int, int] = Field(
        default=(255, 255, 255), description="Text RGB color"
    )


class FfmpegConfig(BaseModel):
    """FFmpeg configuration."""

    crf: int = Field(default=23, ge=0, le=51, description="Constant Rate Factor")
    preset: str = Field(
        default="medium",
        description="Encoding preset: ultrafast, superfast, veryfast, faster, fast, medium, slow, slower, veryslow",
    )
    audio_codec: str = Field(default="copy", description="Audio codec (copy to preserve)")


class Config(BaseModel):
    """Main configuration."""

    input: InputConfig = Field(default_factory=InputConfig)
    output: OutputConfig = Field(default_factory=OutputConfig)
    fps_sampling: FpsSamplingConfig = Field(default_factory=FpsSamplingConfig)
    subtitle_roi: SubtitleRoiConfig = Field(default_factory=SubtitleRoiConfig)
    tracking: TrackingConfig = Field(default_factory=TrackingConfig)
    ocr: OcrConfig = Field(default_factory=OcrConfig)
    segmenter: SegmenterConfig = Field(default_factory=SegmenterConfig)
    translation: TranslationConfig = Field(default_factory=TranslationConfig)
    renderer: RendererConfig = Field(default_factory=RendererConfig)
    ffmpeg: FfmpegConfig = Field(default_factory=FfmpegConfig)

    @classmethod
    def from_yaml(cls, path: str | Path) -> "Config":
        """Load configuration from YAML file."""
        with open(path, "r") as f:
            data = yaml.safe_load(f)
        return cls(**data if data else {})

    def to_yaml(self, path: str | Path) -> None:
        """Save configuration to YAML file."""
        with open(path, "w") as f:
            yaml.dump(self.model_dump(mode="python"), f, default_flow_style=False, indent=2)

    def update_from_dict(self, updates: dict[str, Any]) -> None:
        """Update configuration from a dictionary."""
        for key, value in updates.items():
            if hasattr(self, key) and isinstance(value, dict):
                getattr(self, key).__dict__.update(value)
            elif hasattr(self, key):
                setattr(self, key, value)
