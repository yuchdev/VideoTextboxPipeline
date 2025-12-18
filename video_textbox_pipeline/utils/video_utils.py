"""Video utilities for reading and writing video files."""

import cv2
import numpy as np
from typing import Iterator, Tuple, Optional


class VideoReader:
    """Read video frames using OpenCV."""
    
    def __init__(self, video_path: str):
        """Initialize video reader.
        
        Args:
            video_path: Path to input video file
        """
        self.video_path = video_path
        self.cap = cv2.VideoCapture(video_path)
        
        if not self.cap.isOpened():
            raise ValueError(f"Failed to open video: {video_path}")
        
        self.fps = self.cap.get(cv2.CAP_PROP_FPS)
        self.width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        self.frame_count = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
    
    def read_frames(self) -> Iterator[Tuple[int, np.ndarray]]:
        """Iterate over video frames.
        
        Yields:
            Tuple of (frame_number, frame_array)
        """
        frame_num = 0
        while True:
            ret, frame = self.cap.read()
            if not ret:
                break
            yield frame_num, frame
            frame_num += 1
    
    def get_frame(self, frame_num: int) -> Optional[np.ndarray]:
        """Get a specific frame by number.
        
        Args:
            frame_num: Frame number to retrieve
            
        Returns:
            Frame array or None if frame doesn't exist
        """
        self.cap.set(cv2.CAP_PROP_POS_FRAMES, frame_num)
        ret, frame = self.cap.read()
        return frame if ret else None
    
    def close(self):
        """Release video capture resources."""
        self.cap.release()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


class VideoWriter:
    """Write video frames using OpenCV."""
    
    def __init__(self, output_path: str, fps: float, width: int, height: int, 
                 codec: str = 'mp4v'):
        """Initialize video writer.
        
        Args:
            output_path: Path to output video file
            fps: Frames per second
            width: Frame width
            height: Frame height
            codec: Video codec (default: mp4v)
        """
        self.output_path = output_path
        fourcc = cv2.VideoWriter_fourcc(*codec)
        self.writer = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
        
        if not self.writer.isOpened():
            raise ValueError(f"Failed to create video writer: {output_path}")
    
    def write_frame(self, frame: np.ndarray):
        """Write a single frame to video.
        
        Args:
            frame: Frame array to write
        """
        self.writer.write(frame)
    
    def close(self):
        """Release video writer resources."""
        self.writer.release()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
