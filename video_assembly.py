"""Video assembly module - Compose final video with FFmpeg"""

import ffmpeg
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from typing import List, Dict, Tuple
import tempfile
import os
import json


class TimingSegment:
    """Data class for transcript timing segments"""
    def __init__(self, start: float, end: float, text: str):
        self.start = start
        self.end = end 
        self.text = text


class VideoAssembler:
    """Assemble video from components using FFmpeg"""
    
    def __init__(self):
        self.width = 1080
        self.height = 1920  # Vertical video
        self.fps = 30
        self.transition_duration = 0.5  # Crossfade duration in seconds
    
    def create_video_with_timed_text(
        self,
        image_paths: List[str],  # 3 images: beginning, middle, end
        audio_path: str,
        timing_segments: List[Dict],  # Voxtral timing data
        output_path: str,
        duration: float
    ):
        """Create portrait video with 3 images, audio, and timed text"""
        
        # Convert timing data to TimingSegment objects
        segments = [
            TimingSegment(seg["start"], seg["end"], seg["text"]) 
            for seg in timing_segments
        ]
        
        # Create frames with text overlays
        temp_dir = tempfile.mkdtemp()
        frame_pattern = os.path.join(temp_dir, "frame_%06d.png")
        
        try:
            self._generate_frames_with_text(
                image_paths, segments, duration, frame_pattern
            )
            
            # Combine frames with audio using FFmpeg
            self._combine_frames_and_audio(frame_pattern, audio_path, output_path, duration)
            
        finally:
            # Cleanup temp files
            self._cleanup_temp_files(temp_dir)
    
    def _generate_frames_with_text(
        self, 
        image_paths: List[str], 
        segments: List[TimingSegment], 
        duration: float, 
        frame_pattern: str
    ):
        """Generate video frames with image transitions and text overlays"""
        
        total_frames = int(duration * self.fps)
        
        # Load and resize images
        images = []
        for img_path in image_paths:
            img = Image.open(img_path)
            img = self._resize_and_crop_image(img)
            images.append(img)
        
        # Calculate image timing (3 equal segments)
        segment_duration = duration / 3
        
        for frame_idx in range(total_frames):
            current_time = frame_idx / self.fps
            
            # Determine which image(s) to use and blend factor
            base_image, overlay_image, blend_factor = self._get_current_images(
                images, current_time, segment_duration
            )
            
            # Create frame with potential image blending
            if overlay_image and blend_factor > 0:
                frame = Image.blend(base_image, overlay_image, blend_factor)
            else:
                frame = base_image.copy()
            
            # Add text overlay for current time
            frame = self._add_text_overlay(frame, segments, current_time)
            
            # Save frame
            frame_path = frame_pattern % (frame_idx + 1)
            frame.save(frame_path)
    
    def _resize_and_crop_image(self, img: Image.Image) -> Image.Image:
        """Resize and crop image to vertical video format"""
        # Calculate crop dimensions to maintain aspect ratio
        aspect_ratio = self.width / self.height
        img_width, img_height = img.size
        img_aspect = img_width / img_height
        
        if img_aspect > aspect_ratio:
            # Image is wider, crop horizontally
            new_height = img_height
            new_width = int(img_height * aspect_ratio)
            left = (img_width - new_width) // 2
            img = img.crop((left, 0, left + new_width, new_height))
        else:
            # Image is taller, crop vertically
            new_width = img_width
            new_height = int(img_width / aspect_ratio)
            top = (img_height - new_height) // 2
            img = img.crop((0, top, new_width, top + new_height))
        
        return img.resize((self.width, self.height), Image.Resampling.LANCZOS)
    
    def _get_current_images(
        self, 
        images: List[Image.Image], 
        current_time: float, 
        segment_duration: float
    ) -> Tuple[Image.Image, Image.Image, float]:
        """Get current image(s) and blend factor for transitions"""
        
        # Determine which segment we're in
        segment_idx = int(current_time // segment_duration)
        segment_idx = min(segment_idx, len(images) - 1)
        
        # Calculate time within current segment
        time_in_segment = current_time % segment_duration
        
        base_image = images[segment_idx]
        overlay_image = None
        blend_factor = 0.0
        
        # Check if we're in a transition period
        if (segment_idx < len(images) - 1 and 
            time_in_segment >= segment_duration - self.transition_duration):
            # Transition to next image
            overlay_image = images[segment_idx + 1]
            transition_progress = (time_in_segment - (segment_duration - self.transition_duration)) / self.transition_duration
            blend_factor = transition_progress
        
        return base_image, overlay_image, blend_factor
    
    def _add_text_overlay(
        self, 
        frame: Image.Image, 
        segments: List[TimingSegment], 
        current_time: float
    ) -> Image.Image:
        """Add text overlay to frame based on current time"""
        
        # Find current segment
        current_segment = None
        for segment in segments:
            if segment.start <= current_time <= segment.end:
                current_segment = segment
                break
        
        if not current_segment:
            return frame
        
        # Calculate fade effect - quick fade in/out
        segment_progress = (current_time - current_segment.start) / (current_segment.end - current_segment.start)
        fade_duration = 0.1  # 10% of segment for fade in/out
        
        if segment_progress < fade_duration:
            # Fade in
            alpha = int((segment_progress / fade_duration) * 255)
        elif segment_progress > (1 - fade_duration):
            # Fade out
            fade_out_progress = (segment_progress - (1 - fade_duration)) / fade_duration
            alpha = int((1 - fade_out_progress) * 255)
        else:
            alpha = 255  # Full opacity
        
        # Create text overlay
        return self._draw_text_with_outline(frame, current_segment.text, alpha)
    
    def _draw_text_with_outline(
        self, 
        frame: Image.Image, 
        text: str, 
        alpha: int
    ) -> Image.Image:
        """Draw text with outline similar to Kotlin implementation"""
        
        draw = ImageDraw.Draw(frame)
        
        # Calculate optimal font size and wrap text
        max_width = int(self.width * 0.8)
        max_height = int(self.height * 0.4)
        
        wrapped_text, font_size = self._calculate_font_and_wrap_text(
            text, max_width, max_height
        )
        
        try:
            font = ImageFont.truetype("Impact", font_size)
        except:
            try:
                font = ImageFont.truetype("Arial Black", font_size)
            except:
                font = ImageFont.load_default()
        
        # Position text in bottom third of frame
        y_start = int(self.height * 0.7)
        
        for i, line in enumerate(wrapped_text):
            if not line.strip():
                continue
                
            # Calculate text position (centered)
            bbox = draw.textbbox((0, 0), line, font=font)
            text_width = bbox[2] - bbox[0]
            x = (self.width - text_width) // 2
            y = y_start + (i * (font_size + 10))
            
            # Draw text with multiple outline layers (like Kotlin version)
            outline_color = (0, 0, 0, alpha)
            text_color = (255, 255, 255, alpha)
            
            # Outer outline
            for adj in [(-3, -3), (-3, 3), (3, -3), (3, 3), (-3, 0), (3, 0), (0, -3), (0, 3)]:
                draw.text((x + adj[0], y + adj[1]), line, font=font, fill=outline_color)
            
            # Inner outline
            for adj in [(-2, -2), (-2, 2), (2, -2), (2, 2), (-2, 0), (2, 0), (0, -2), (0, 2)]:
                draw.text((x + adj[0], y + adj[1]), line, font=font, fill=outline_color)
            
            # Main text
            draw.text((x, y), line, font=font, fill=text_color)
        
        return frame
    
    def _calculate_font_and_wrap_text(
        self, 
        text: str, 
        max_width: int, 
        max_height: int
    ) -> Tuple[List[str], int]:
        """Calculate optimal font size and wrap text"""
        
        initial_font_size = max(int(self.height * 0.05), 20)
        min_font_size = max(int(initial_font_size * 0.4), 12)
        
        for font_size in range(initial_font_size, min_font_size - 1, -1):
            try:
                font = ImageFont.truetype("Impact", font_size)
            except:
                try:
                    font = ImageFont.truetype("Arial Black", font_size)
                except:
                    font = ImageFont.load_default()
            
            wrapped_text = self._wrap_text(text, font, max_width)
            
            # Check if text fits in available height
            total_height = len(wrapped_text) * (font_size + 10)
            if total_height <= max_height:
                return wrapped_text, font_size
        
        # Fallback to minimum font size
        try:
            font = ImageFont.truetype("Impact", min_font_size)
        except:
            try:
                font = ImageFont.truetype("Arial Black", min_font_size)
            except:
                font = ImageFont.load_default()
        
        return self._wrap_text(text, font, max_width), min_font_size
    
    def _wrap_text(self, text: str, font: ImageFont.ImageFont, max_width: int) -> List[str]:
        """Wrap text to fit within max_width"""
        words = text.split()
        lines = []
        current_line = []
        
        for word in words:
            test_line = current_line + [word]
            test_text = " ".join(test_line)
            
            # Create a temporary image to measure text
            temp_img = Image.new('RGB', (1, 1))
            temp_draw = ImageDraw.Draw(temp_img)
            bbox = temp_draw.textbbox((0, 0), test_text, font=font)
            text_width = bbox[2] - bbox[0]
            
            if text_width <= max_width:
                current_line = test_line
            else:
                if current_line:
                    lines.append(" ".join(current_line))
                current_line = [word]
        
        if current_line:
            lines.append(" ".join(current_line))
        
        return lines
    
    def _combine_frames_and_audio(
        self, 
        frame_pattern: str, 
        audio_path: str, 
        output_path: str, 
        duration: float
    ):
        """Combine frames and audio using FFmpeg"""
        
        try:
            # Create video from frames
            video_input = ffmpeg.input(frame_pattern, pattern_type='sequence', framerate=self.fps)
            audio_input = ffmpeg.input(audio_path)
            
            # Combine video and audio
            output = ffmpeg.output(
                video_input,
                audio_input,
                output_path,
                vcodec='libx264',
                acodec='aac',
                pix_fmt='yuv420p',
                t=duration,
                r=self.fps
            )
            
            # Run FFmpeg
            ffmpeg.run(output, overwrite_output=True, quiet=True)
            
        except ffmpeg.Error as e:
            print(f"FFmpeg error: {e}")
            raise
    
    def _cleanup_temp_files(self, temp_dir: str):
        """Clean up temporary files"""
        import shutil
        try:
            shutil.rmtree(temp_dir)
        except Exception as e:
            print(f"Warning: Could not clean up temp files: {e}")


def create_video_from_components(
    image_paths: List[str],
    audio_path: str, 
    timing_data: List[Dict],
    output_path: str,
    duration: float
) -> str:
    """Main API function to create video from components"""
    
    assembler = VideoAssembler()
    assembler.create_video_with_timed_text(
        image_paths=image_paths,
        audio_path=audio_path,
        timing_segments=timing_data,
        output_path=output_path,
        duration=duration
    )
    
    return output_path