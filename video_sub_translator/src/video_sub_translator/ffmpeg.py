"""FFmpeg wrapper for video processing operations."""

import json
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Any, Optional

import cv2
import numpy as np

from video_sub_translator.logging import get_logger

logger = get_logger("ffmpeg")


class FFmpegError(Exception):
    """FFmpeg operation error."""

    pass


def check_ffmpeg_available() -> bool:
    """Check if ffmpeg is available in PATH."""
    return shutil.which("ffmpeg") is not None and shutil.which("ffprobe") is not None


def probe_video(video_path: str | Path) -> dict[str, Any]:
    """
    Probe video file to get metadata.

    Args:
        video_path: Path to video file

    Returns:
        Dictionary with video metadata (fps, duration, width, height, audio_streams, etc.)

    Raises:
        FFmpegError: If ffprobe fails or video cannot be probed
    """
    if not check_ffmpeg_available():
        raise FFmpegError("ffmpeg/ffprobe not found in PATH. Please install ffmpeg.")

    cmd = [
        "ffprobe",
        "-v",
        "quiet",
        "-print_format",
        "json",
        "-show_format",
        "-show_streams",
        str(video_path),
    ]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        data = json.loads(result.stdout)

        # Extract video stream info
        video_stream = next(
            (s for s in data.get("streams", []) if s["codec_type"] == "video"), None
        )
        if not video_stream:
            raise FFmpegError(f"No video stream found in {video_path}")

        # Calculate FPS
        fps_parts = video_stream.get("r_frame_rate", "30/1").split("/")
        fps = float(fps_parts[0]) / float(fps_parts[1])

        # Get duration
        duration = float(data.get("format", {}).get("duration", 0))

        # Count audio streams
        audio_streams = [s for s in data.get("streams", []) if s["codec_type"] == "audio"]

        return {
            "fps": fps,
            "duration": duration,
            "width": int(video_stream.get("width", 0)),
            "height": int(video_stream.get("height", 0)),
            "audio_streams": len(audio_streams),
            "has_audio": len(audio_streams) > 0,
            "codec": video_stream.get("codec_name", "unknown"),
        }

    except subprocess.CalledProcessError as e:
        raise FFmpegError(f"ffprobe failed: {e.stderr}") from e
    except (json.JSONDecodeError, KeyError, ValueError) as e:
        raise FFmpegError(f"Failed to parse ffprobe output: {e}") from e


def extract_frames(
    video_path: str | Path,
    output_dir: str | Path,
    fps: Optional[float] = None,
    start_time: Optional[float] = None,
    end_time: Optional[float] = None,
) -> list[Path]:
    """
    Extract frames from video to a directory.

    Args:
        video_path: Path to input video
        output_dir: Directory to save frames
        fps: Target FPS for extraction (None = original fps)
        start_time: Start time in seconds (None = from beginning)
        end_time: End time in seconds (None = to end)

    Returns:
        List of extracted frame paths

    Raises:
        FFmpegError: If frame extraction fails
    """
    if not check_ffmpeg_available():
        raise FFmpegError("ffmpeg not found in PATH. Please install ffmpeg.")

    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    # Build ffmpeg command
    cmd = ["ffmpeg", "-i", str(video_path)]

    if start_time is not None:
        cmd.extend(["-ss", str(start_time)])

    if end_time is not None:
        cmd.extend(["-t", str(end_time - (start_time or 0))])

    if fps is not None:
        cmd.extend(["-vf", f"fps={fps}"])

    # Output pattern
    output_pattern = str(output_path / "frame_%06d.png")
    cmd.extend(["-qscale:v", "2", output_pattern])

    logger.info(f"Extracting frames with command: {' '.join(cmd)}")

    try:
        subprocess.run(cmd, capture_output=True, text=True, check=True)

        # Get list of extracted frames
        frames = sorted(output_path.glob("frame_*.png"))
        logger.info(f"Extracted {len(frames)} frames to {output_dir}")
        return frames

    except subprocess.CalledProcessError as e:
        raise FFmpegError(f"Frame extraction failed: {e.stderr}") from e


def create_timestamp_mapping(
    num_frames: int, fps: float, start_time: float = 0.0
) -> dict[int, float]:
    """
    Create mapping from frame index to timestamp in milliseconds.

    Args:
        num_frames: Total number of frames
        fps: Frames per second
        start_time: Start time offset in seconds

    Returns:
        Dictionary mapping frame_idx -> timestamp_ms
    """
    ms_per_frame = 1000.0 / fps
    return {i: start_time * 1000 + i * ms_per_frame for i in range(num_frames)}


def encode_video(
    frames_dir: str | Path,
    output_path: str | Path,
    fps: float,
    audio_source: Optional[str | Path] = None,
    crf: int = 23,
    preset: str = "medium",
    audio_codec: str = "copy",
) -> None:
    """
    Encode video from frames directory.

    Args:
        frames_dir: Directory containing frames (frame_%06d.png pattern)
        output_path: Output video path
        fps: Target frames per second
        audio_source: Optional source video to copy audio from
        crf: Constant Rate Factor (0-51, lower=better quality)
        preset: Encoding preset (ultrafast to veryslow)
        audio_codec: Audio codec (copy to preserve original)

    Raises:
        FFmpegError: If encoding fails
    """
    if not check_ffmpeg_available():
        raise FFmpegError("ffmpeg not found in PATH. Please install ffmpeg.")

    frames_pattern = str(Path(frames_dir) / "frame_%06d.png")

    # Build ffmpeg command
    cmd = [
        "ffmpeg",
        "-y",  # Overwrite output
        "-framerate",
        str(fps),
        "-i",
        frames_pattern,
    ]

    # Add audio if source provided
    if audio_source:
        cmd.extend(["-i", str(audio_source)])
        cmd.extend(["-map", "0:v", "-map", "1:a?"])  # Map video from first input, audio from second
        cmd.extend(["-c:a", audio_codec])
    else:
        cmd.extend(["-map", "0:v"])

    # Video encoding settings
    cmd.extend(
        [
            "-c:v",
            "libx264",
            "-crf",
            str(crf),
            "-preset",
            preset,
            "-pix_fmt",
            "yuv420p",
            str(output_path),
        ]
    )

    logger.info(f"Encoding video with command: {' '.join(cmd)}")

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        logger.info(f"Video encoded successfully to {output_path}")

    except subprocess.CalledProcessError as e:
        raise FFmpegError(f"Video encoding failed: {e.stderr}") from e


class VideoFrameExtractor:
    """Context manager for extracting and managing video frames."""

    def __init__(
        self,
        video_path: str | Path,
        fps: Optional[float] = None,
        temp_dir: Optional[str | Path] = None,
    ):
        """
        Initialize frame extractor.

        Args:
            video_path: Path to input video
            fps: Target FPS (None = original fps)
            temp_dir: Temporary directory for frames (None = auto-create)
        """
        self.video_path = Path(video_path)
        self.fps = fps
        self.temp_dir = Path(temp_dir) if temp_dir else None
        self._temp_dir_obj: Optional[tempfile.TemporaryDirectory] = None
        self.frames_dir: Optional[Path] = None
        self.frames: list[Path] = []
        self.timestamp_map: dict[int, float] = {}

    def __enter__(self) -> "VideoFrameExtractor":
        """Extract frames on context entry."""
        # Create temp directory if not specified
        if self.temp_dir is None:
            self._temp_dir_obj = tempfile.TemporaryDirectory(prefix="vst_frames_")
            self.frames_dir = Path(self._temp_dir_obj.name)
        else:
            self.frames_dir = self.temp_dir
            self.frames_dir.mkdir(parents=True, exist_ok=True)

        # Probe video to get FPS if not specified
        video_info = probe_video(self.video_path)
        actual_fps = self.fps if self.fps else video_info["fps"]

        # Extract frames
        self.frames = extract_frames(self.video_path, self.frames_dir, fps=self.fps)

        # Create timestamp mapping
        self.timestamp_map = create_timestamp_mapping(len(self.frames), actual_fps)

        logger.info(
            f"Extracted {len(self.frames)} frames at {actual_fps} fps to {self.frames_dir}"
        )

        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Clean up temporary directory on context exit."""
        if self._temp_dir_obj:
            self._temp_dir_obj.cleanup()
            logger.debug("Cleaned up temporary frames directory")

    def get_frame(self, idx: int) -> Optional[np.ndarray]:
        """Load a specific frame as numpy array."""
        if idx < 0 or idx >= len(self.frames):
            return None
        return cv2.imread(str(self.frames[idx]))

    def get_timestamp(self, idx: int) -> Optional[float]:
        """Get timestamp for a frame index."""
        return self.timestamp_map.get(idx)
