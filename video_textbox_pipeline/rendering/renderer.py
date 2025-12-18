"""Subtitle renderer for applying translated subtitles to video frames."""

import cv2
import numpy as np
from typing import Tuple, Optional
from PIL import Image, ImageDraw, ImageFont


class SubtitleRenderer:
    """Render translated subtitles on video frames."""
    
    # Rendering modes
    MODE_RECTANGLE = 'rectangle'
    MODE_INPAINT = 'inpaint'
    
    def __init__(self, mode: str = MODE_RECTANGLE, font_path: Optional[str] = None,
                 font_size: int = 32):
        """Initialize subtitle renderer.
        
        Args:
            mode: Rendering mode ('rectangle' or 'inpaint')
            font_path: Path to custom font file (optional)
            font_size: Font size for rendered text
        """
        self.mode = mode
        self.font_size = font_size
        
        # Try to load font
        try:
            if font_path:
                self.font = ImageFont.truetype(font_path, font_size)
            else:
                # Try to use a default font
                self.font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", font_size)
        except (OSError, IOError):
            # Fallback to default PIL font
            self.font = ImageFont.load_default()
    
    def render_rectangle_mode(self, frame: np.ndarray, text: str, 
                             bbox: Tuple[int, int, int, int],
                             bg_color: Optional[Tuple[int, int, int]] = None,
                             text_color: Tuple[int, int, int] = (255, 255, 255),
                             padding: int = 10) -> np.ndarray:
        """Render subtitle with background-matched rectangle.
        
        Args:
            frame: Input frame (BGR format)
            text: Text to render
            bbox: Original subtitle bounding box (x, y, width, height)
            bg_color: Background color (B, G, R). If None, extracts from bbox area
            text_color: Text color (R, G, B)
            padding: Padding around text
            
        Returns:
            Frame with rendered subtitle
        """
        frame = frame.copy()
        x, y, w, h = bbox
        
        # Extract background color if not provided
        if bg_color is None:
            from ..utils.text_utils import extract_dominant_color
            bg_color = extract_dominant_color(frame, bbox)
        
        # Convert frame to PIL Image for text rendering
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        pil_image = Image.fromarray(frame_rgb)
        draw = ImageDraw.Draw(pil_image)
        
        # Calculate text size and position
        # Get text bounding box
        text_bbox = draw.textbbox((0, 0), text, font=self.font)
        text_width = text_bbox[2] - text_bbox[0]
        text_height = text_bbox[3] - text_bbox[1]
        
        # Center text in the bbox area
        text_x = x + (w - text_width) // 2
        text_y = y + (h - text_height) // 2
        
        # Draw background rectangle (convert BGR to RGB)
        bg_color_rgb = (bg_color[2], bg_color[1], bg_color[0])
        rect_x1 = text_x - padding
        rect_y1 = text_y - padding
        rect_x2 = text_x + text_width + padding
        rect_y2 = text_y + text_height + padding
        
        draw.rectangle([rect_x1, rect_y1, rect_x2, rect_y2], fill=bg_color_rgb)
        
        # Draw text
        draw.text((text_x, text_y), text, font=self.font, fill=text_color)
        
        # Convert back to OpenCV format
        frame_bgr = cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)
        
        return frame_bgr
    
    def render_inpaint_mode(self, frame: np.ndarray, text: str,
                           bbox: Tuple[int, int, int, int],
                           text_color: Tuple[int, int, int] = (255, 255, 255),
                           padding: int = 10) -> np.ndarray:
        """Render subtitle with text removal via inpainting.
        
        Args:
            frame: Input frame (BGR format)
            text: Text to render
            bbox: Original subtitle bounding box (x, y, width, height)
            text_color: Text color (R, G, B)
            padding: Padding around inpainted area
            
        Returns:
            Frame with inpainted and re-rendered subtitle
        """
        frame = frame.copy()
        x, y, w, h = bbox
        
        # Create mask for inpainting
        mask = np.zeros(frame.shape[:2], dtype=np.uint8)
        mask[y:y+h, x:x+w] = 255
        
        # Inpaint the region (remove original text)
        inpainted = cv2.inpaint(frame, mask, inpaintRadius=3, flags=cv2.INPAINT_TELEA)
        
        # Now render new text on inpainted frame
        frame_rgb = cv2.cvtColor(inpainted, cv2.COLOR_BGR2RGB)
        pil_image = Image.fromarray(frame_rgb)
        draw = ImageDraw.Draw(pil_image)
        
        # Calculate text size and position
        text_bbox = draw.textbbox((0, 0), text, font=self.font)
        text_width = text_bbox[2] - text_bbox[0]
        text_height = text_bbox[3] - text_bbox[1]
        
        # Center text in the bbox area
        text_x = x + (w - text_width) // 2
        text_y = y + (h - text_height) // 2
        
        # Draw text
        draw.text((text_x, text_y), text, font=self.font, fill=text_color)
        
        # Convert back to OpenCV format
        frame_bgr = cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)
        
        return frame_bgr
    
    def render(self, frame: np.ndarray, text: str,
              bbox: Tuple[int, int, int, int],
              **kwargs) -> np.ndarray:
        """Render subtitle on frame using configured mode.
        
        Args:
            frame: Input frame
            text: Text to render
            bbox: Bounding box (x, y, width, height)
            **kwargs: Additional arguments for specific rendering mode
            
        Returns:
            Frame with rendered subtitle
        """
        if self.mode == self.MODE_INPAINT:
            return self.render_inpaint_mode(frame, text, bbox, **kwargs)
        else:
            return self.render_rectangle_mode(frame, text, bbox, **kwargs)
