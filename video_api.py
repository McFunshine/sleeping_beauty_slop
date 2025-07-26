"""Video generation API module"""

from typing import List, Dict, Optional
from pathlib import Path
import json
import os
from video_assembly import create_video_from_components


class VideoGenerationAPI:
    """API for generating videos from components"""
    
    def __init__(self, assets_dir: str = "assets", output_dir: str = "output"):
        self.assets_dir = Path(assets_dir)
        self.output_dir = Path(output_dir)
        
        # Ensure directories exist
        self.assets_dir.mkdir(exist_ok=True)
        self.output_dir.mkdir(exist_ok=True)
    
    def create_video(
        self,
        images: List[str],  # Paths to 3 images
        audio: str,         # Path to audio file
        timing_data: List[Dict],  # Voxtral timing segments
        output_filename: Optional[str] = None,
        duration: Optional[float] = None
    ) -> Dict[str, str]:
        """
        Create a video from components
        
        Args:
            images: List of 3 image file paths (beginning, middle, end)
            audio: Path to audio file
            timing_data: List of timing segments with format:
                [{"start": 0.0, "end": 2.5, "text": "Hello world"}, ...]
            output_filename: Optional custom filename (default: auto-generated)
            duration: Optional duration override (default: from audio)
        
        Returns:
            Dict with video_path and metadata
        """
        
        # Validate inputs
        self._validate_inputs(images, audio, timing_data)
        
        # Generate output filename if not provided
        if not output_filename:
            output_filename = f"video_{len(list(self.output_dir.glob('*.mp4'))) + 1:03d}.mp4"
        
        output_path = self.output_dir / output_filename
        
        # Determine duration from timing data if not provided
        if duration is None:
            duration = max(seg["end"] for seg in timing_data) if timing_data else 10.0
        
        try:
            # Create the video
            result_path = create_video_from_components(
                image_paths=images,
                audio_path=audio,
                timing_data=timing_data,
                output_path=str(output_path),
                duration=duration
            )
            
            return {
                "status": "success",
                "video_path": result_path,
                "duration": duration,
                "image_count": len(images),
                "text_segments": len(timing_data)
            }
            
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "video_path": None
            }
    
    def _validate_inputs(self, images: List[str], audio: str, timing_data: List[Dict]):
        """Validate input parameters"""
        
        # Check images
        if len(images) != 3:
            raise ValueError("Exactly 3 images are required (beginning, middle, end)")
        
        for img_path in images:
            if not os.path.exists(img_path):
                raise FileNotFoundError(f"Image not found: {img_path}")
        
        # Check audio
        if not os.path.exists(audio):
            raise FileNotFoundError(f"Audio file not found: {audio}")
        
        # Check timing data format
        if not timing_data:
            raise ValueError("Timing data cannot be empty")
        
        for i, segment in enumerate(timing_data):
            required_keys = ["start", "end", "text"]
            for key in required_keys:
                if key not in segment:
                    raise ValueError(f"Timing segment {i} missing required key: {key}")
            
            if segment["start"] >= segment["end"]:
                raise ValueError(f"Invalid timing in segment {i}: start >= end")
    
    def create_sample_timing_data(self, text_segments: List[str], total_duration: float) -> List[Dict]:
        """
        Create sample timing data for testing
        
        Args:
            text_segments: List of text strings
            total_duration: Total duration to distribute segments across
        
        Returns:
            List of timing segments
        """
        if not text_segments:
            return []
        
        segment_duration = total_duration / len(text_segments)
        timing_data = []
        
        for i, text in enumerate(text_segments):
            start_time = i * segment_duration
            end_time = (i + 1) * segment_duration
            
            timing_data.append({
                "start": start_time,
                "end": end_time,
                "text": text
            })
        
        return timing_data


def main():
    """Example usage of the video generation API"""
    
    api = VideoGenerationAPI()
    
    # Sample data for testing
    sample_images = [
        "assets/images/beginning.jpg",
        "assets/images/middle.jpg", 
        "assets/images/end.jpg"
    ]
    
    sample_audio = "assets/audio/narration.mp3"
    
    sample_timing = [
        {"start": 0.0, "end": 2.5, "text": "Scientists have discovered something incredible"},
        {"start": 2.5, "end": 5.0, "text": "that could change everything we know"},
        {"start": 5.0, "end": 7.5, "text": "about the universe itself"}
    ]
    
    # Create video (would work if files exist)
    try:
        result = api.create_video(
            images=sample_images,
            audio=sample_audio,
            timing_data=sample_timing
        )
        print(f"Video creation result: {result}")
    except Exception as e:
        print(f"Example would fail because sample files don't exist: {e}")


if __name__ == "__main__":
    main()