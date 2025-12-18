"""Configuration management for the pipeline."""

import yaml
from typing import Dict, Any, Optional
from dataclasses import dataclass


@dataclass
class PipelineConfig:
    """Configuration for subtitle translation pipeline."""
    
    # Language settings
    target_lang: str = 'en'
    source_lang: Optional[str] = None  # Auto-detect if None
    
    # OCR settings
    ocr_lang: str = 'en'
    use_gpu: bool = False
    min_confidence: float = 0.5
    bottom_ratio: float = 0.3  # Bottom 30% of frame for subtitles
    
    # Segmentation settings
    similarity_threshold: float = 0.8
    min_segment_frames: int = 3
    max_gap_frames: int = 2
    
    # Rendering settings
    render_mode: str = 'rectangle'  # 'rectangle' or 'inpaint'
    font_path: Optional[str] = None
    font_size: int = 32
    text_color: tuple = (255, 255, 255)  # White (R, G, B)
    padding: int = 10
    
    # Video settings
    output_codec: str = 'mp4v'
    
    @classmethod
    def from_yaml(cls, yaml_path: str) -> 'PipelineConfig':
        """Load configuration from YAML file.
        
        Args:
            yaml_path: Path to YAML configuration file
            
        Returns:
            PipelineConfig object
        """
        with open(yaml_path, 'r') as f:
            config_dict = yaml.safe_load(f)
        
        return cls(**config_dict)
    
    def to_yaml(self, yaml_path: str):
        """Save configuration to YAML file.
        
        Args:
            yaml_path: Path to output YAML file
        """
        config_dict = {
            'target_lang': self.target_lang,
            'source_lang': self.source_lang,
            'ocr_lang': self.ocr_lang,
            'use_gpu': self.use_gpu,
            'min_confidence': self.min_confidence,
            'bottom_ratio': self.bottom_ratio,
            'similarity_threshold': self.similarity_threshold,
            'min_segment_frames': self.min_segment_frames,
            'max_gap_frames': self.max_gap_frames,
            'render_mode': self.render_mode,
            'font_path': self.font_path,
            'font_size': self.font_size,
            'text_color': self.text_color,
            'padding': self.padding,
            'output_codec': self.output_codec
        }
        
        with open(yaml_path, 'w') as f:
            yaml.dump(config_dict, f, default_flow_style=False)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary.
        
        Returns:
            Dictionary representation
        """
        return {
            'target_lang': self.target_lang,
            'source_lang': self.source_lang,
            'ocr_lang': self.ocr_lang,
            'use_gpu': self.use_gpu,
            'min_confidence': self.min_confidence,
            'bottom_ratio': self.bottom_ratio,
            'similarity_threshold': self.similarity_threshold,
            'min_segment_frames': self.min_segment_frames,
            'max_gap_frames': self.max_gap_frames,
            'render_mode': self.render_mode,
            'font_path': self.font_path,
            'font_size': self.font_size,
            'text_color': self.text_color,
            'padding': self.padding,
            'output_codec': self.output_codec
        }
