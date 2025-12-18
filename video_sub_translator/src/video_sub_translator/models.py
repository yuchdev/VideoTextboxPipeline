"""Pydantic data models for the video subtitle translation pipeline."""

from typing import Any, Optional

from pydantic import BaseModel, Field


class BBox(BaseModel):
    """Bounding box with coordinates and confidence."""

    x1: float = Field(..., description="Top-left x coordinate")
    y1: float = Field(..., description="Top-left y coordinate")
    x2: float = Field(..., description="Bottom-right x coordinate")
    y2: float = Field(..., description="Bottom-right y coordinate")
    confidence: float = Field(default=1.0, ge=0.0, le=1.0, description="Detection confidence")

    @property
    def width(self) -> float:
        """Calculate bbox width."""
        return self.x2 - self.x1

    @property
    def height(self) -> float:
        """Calculate bbox height."""
        return self.y2 - self.y1

    @property
    def center(self) -> tuple[float, float]:
        """Calculate bbox center point."""
        return ((self.x1 + self.x2) / 2, (self.y1 + self.y2) / 2)

    @property
    def area(self) -> float:
        """Calculate bbox area."""
        return self.width * self.height


class OcrToken(BaseModel):
    """Single OCR token with text, bounding box and confidence."""

    text: str = Field(..., description="Detected text")
    bbox: BBox = Field(..., description="Token bounding box")
    confidence: float = Field(..., ge=0.0, le=1.0, description="OCR confidence")


class FrameOcrResult(BaseModel):
    """OCR results for a single frame."""

    frame_idx: int = Field(..., ge=0, description="Frame index")
    ts_ms: float = Field(..., ge=0.0, description="Timestamp in milliseconds")
    tokens: list[OcrToken] = Field(default_factory=list, description="List of detected tokens")
    bbox: Optional[BBox] = Field(default=None, description="Overall subtitle region bbox")

    @property
    def text(self) -> str:
        """Get combined text from all tokens."""
        return " ".join(token.text for token in self.tokens)


class SubtitleSegment(BaseModel):
    """A subtitle segment spanning multiple frames."""

    start_ms: float = Field(..., ge=0.0, description="Segment start time in milliseconds")
    end_ms: float = Field(..., ge=0.0, description="Segment end time in milliseconds")
    bbox: BBox = Field(..., description="Representative bounding box for the segment")
    text_src: str = Field(..., description="Source text")
    lang_src: Optional[str] = Field(default=None, description="Detected source language")
    text_dst: Optional[str] = Field(default=None, description="Translated text")
    lang_dst: Optional[str] = Field(default=None, description="Target language")
    confidence: float = Field(default=1.0, ge=0.0, le=1.0, description="Segment confidence")
    frame_count: int = Field(default=1, ge=1, description="Number of frames in segment")

    @property
    def duration_ms(self) -> float:
        """Calculate segment duration in milliseconds."""
        return self.end_ms - self.start_ms


class PipelineStats(BaseModel):
    """Statistics from pipeline execution."""

    total_frames: int = Field(default=0, ge=0, description="Total frames processed")
    frames_with_text: int = Field(default=0, ge=0, description="Frames with detected text")
    segments_detected: int = Field(default=0, ge=0, description="Number of segments detected")
    segments_translated: int = Field(default=0, ge=0, description="Number of segments translated")
    total_duration_ms: float = Field(default=0.0, ge=0.0, description="Total video duration")
    processing_time_s: float = Field(default=0.0, ge=0.0, description="Total processing time")


class PipelineResult(BaseModel):
    """Complete pipeline execution result."""

    segments: list[SubtitleSegment] = Field(
        default_factory=list, description="Detected subtitle segments"
    )
    stats: PipelineStats = Field(
        default_factory=PipelineStats, description="Pipeline execution statistics"
    )
    output_paths: dict[str, str] = Field(
        default_factory=dict, description="Paths to output files"
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict, description="Additional metadata"
    )
