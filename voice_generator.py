"""Voice generator module - Text-to-speech with Coqui TTS"""

import os
import torch
from pathlib import Path
from typing import Optional, Union, List, Dict
import tempfile
import time
import subprocess

try:
    from TTS.api import TTS
    from TTS.utils.manage import ModelManager
except ImportError:
    print("Coqui TTS not installed. Run: pip install TTS")
    TTS = None


class VoiceGenerator:
    """Generate voice narration using Coqui TTS"""
    
    # Popular models for different use cases
    DEFAULT_MODELS = {
        "english_fast": "tts_models/en/ljspeech/tacotron2-DDC",
        "english_quality": "tts_models/en/ljspeech/glow-tts",
        "multilingual": "tts_models/multilingual/multi-dataset/your_tts",
        "voice_cloning": "tts_models/multilingual/multi-dataset/your_tts",
        "bark": "tts_models/multilingual/multi-dataset/bark"
    }
    
    def __init__(self, model_name: str = "english_fast", use_gpu: bool = True):
        """
        Initialize TTS with specified model
        
        Args:
            model_name: Model to use (key from DEFAULT_MODELS or full model name)
            use_gpu: Whether to use GPU acceleration
        """
        if TTS is None:
            raise ImportError("Coqui TTS not installed. Run: pip install TTS")
        
        self.use_gpu = use_gpu and torch.cuda.is_available()
        self.device = "cuda" if self.use_gpu else "cpu"
        
        # Resolve model name
        self.model_name = self.DEFAULT_MODELS.get(model_name, model_name)
        
        # Initialize TTS
        print(f"Loading TTS model: {self.model_name}")
        print(f"Using device: {self.device}")
        
        self.tts = TTS(model_name=self.model_name, progress_bar=True)
        
        if self.use_gpu:
            self.tts = self.tts.to(self.device)
        
        print("TTS model loaded successfully!")
    
    def convert_audio_for_transcription(self, input_path: str, output_path: Optional[str] = None) -> str:
        """
        Convert audio to optimized format for transcription (16kHz mono MP4)
        
        Args:
            input_path: Path to input audio file
            output_path: Path for optimized output (auto-generated if None)
        
        Returns:
            Path to optimized audio file
        """
        input_path = Path(input_path)
        
        if output_path is None:
            # Create optimized version next to original
            output_path = input_path.with_suffix('.mp4').with_name(f"{input_path.stem}_optimized.mp4")
        else:
            output_path = Path(output_path)
        
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            # Use ffmpeg to convert to optimized format for transcription
            cmd = [
                'ffmpeg', '-y',  # -y to overwrite existing files
                '-i', str(input_path),
                '-ar', '16000',  # 16kHz sample rate
                '-ac', '1',      # Mono
                '-c:a', 'aac',   # AAC codec for MP4
                str(output_path)
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            print(f"Audio optimized for transcription: {output_path}")
            return str(output_path)
            
        except subprocess.CalledProcessError as e:
            print(f"Error converting audio: {e.stderr}")
            raise Exception(f"Audio conversion failed: {e.stderr}")
        except FileNotFoundError:
            raise Exception("ffmpeg not found. Please install ffmpeg to use audio optimization.")
    
    def generate_voice_from_script(
        self, 
        script_text: str, 
        output_path: str,
        speaker_wav: Optional[str] = None,
        speaker_idx: Optional[Union[str, int]] = None,
        language: str = "en",
        create_optimized_for_transcription: bool = True,
        **kwargs
    ) -> Dict[str, str]:
        """
        Main API: Generate voice from script text
        
        Args:
            script_text: Text to convert to speech
            output_path: Path to save the audio file
            speaker_wav: Path to reference audio for voice cloning
            speaker_idx: Speaker ID for multi-speaker models
            language: Language code (for multilingual models)
            create_optimized_for_transcription: Whether to create optimized version for transcription
            **kwargs: Additional TTS parameters
        
        Returns:
            Dict with paths to generated audio files
        """
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            if speaker_wav:
                # Voice cloning mode
                print(f"Generating voice with cloning from: {speaker_wav}")
                self.tts.tts_to_file(
                    text=script_text,
                    file_path=str(output_path),
                    speaker_wav=speaker_wav,
                    language=language,
                    **kwargs
                )
            elif speaker_idx is not None:
                # Multi-speaker mode
                print(f"Generating voice with speaker: {speaker_idx}")
                self.tts.tts_to_file(
                    text=script_text,
                    file_path=str(output_path),
                    speaker_idx=speaker_idx,
                    **kwargs
                )
            else:
                # Default single speaker mode
                print("Generating voice with default speaker")
                self.tts.tts_to_file(
                    text=script_text,
                    file_path=str(output_path),
                    **kwargs
                )
            
            print(f"Voice generated successfully: {output_path}")
            
            # Create optimized version for transcription if requested
            result = {"original": str(output_path)}
            
            if create_optimized_for_transcription:
                try:
                    optimized_path = self.convert_audio_for_transcription(str(output_path))
                    result["optimized_for_transcription"] = optimized_path
                    print(f"Optimized version created: {optimized_path}")
                except Exception as e:
                    print(f"Warning: Could not create optimized version: {e}")
                    result["optimized_for_transcription"] = None
            
            return result
            
        except Exception as e:
            print(f"Error generating voice: {e}")
            raise
    
    def clone_voice_from_sample(
        self,
        script_text: str,
        reference_audio: str,
        output_path: str,
        language: str = "en",
        create_optimized_for_transcription: bool = True
    ) -> Dict[str, str]:
        """
        Clone a voice from a reference audio sample
        
        Args:
            script_text: Text to speak
            reference_audio: Path to reference audio file
            output_path: Output audio path
            language: Language code
            create_optimized_for_transcription: Whether to create optimized version
        
        Returns:
            Dict with paths to generated audio files
        """
        return self.generate_voice_from_script(
            script_text=script_text,
            output_path=output_path,
            speaker_wav=reference_audio,
            language=language,
            create_optimized_for_transcription=create_optimized_for_transcription
        )
    
    def list_available_models(self) -> List[str]:
        """List all available TTS models"""
        try:
            manager = ModelManager()
            models = manager.list_models()
            return [model for model in models if "tts_models" in model]
        except Exception as e:
            print(f"Error listing models: {e}")
            return list(self.DEFAULT_MODELS.values())
    
    def list_speakers(self) -> Optional[List]:
        """List available speakers for multi-speaker models"""
        try:
            if hasattr(self.tts, 'speakers') and self.tts.speakers:
                return self.tts.speakers
            return None
        except Exception:
            return None
    
    def get_model_info(self) -> Dict:
        """Get information about the current model"""
        return {
            "model_name": self.model_name,
            "device": self.device,
            "is_multi_speaker": hasattr(self.tts, 'speakers') and self.tts.speakers is not None,
            "speakers": self.list_speakers(),
            "supports_voice_cloning": "your_tts" in self.model_name.lower() or "bark" in self.model_name.lower()
        }


class VoiceGeneratorAPI:
    """High-level API for voice generation"""
    
    def __init__(self):
        self.generator = None
        self.current_model = None
    
    def initialize_model(self, model_type: str = "english_fast", use_gpu: bool = True):
        """Initialize TTS model"""
        if self.current_model != model_type:
            print(f"Switching to model: {model_type}")
            self.generator = VoiceGenerator(model_name=model_type, use_gpu=use_gpu)
            self.current_model = model_type
    
    def generate_narration(
        self,
        script: str,
        output_dir: str = "assets/audio",
        filename: Optional[str] = None,
        voice_type: str = "english_fast",
        reference_voice: Optional[str] = None
    ) -> Dict[str, Union[str, float]]:
        """
        Generate narration from script
        
        Args:
            script: Text to convert to speech
            output_dir: Directory to save audio
            filename: Custom filename (auto-generated if None)
            voice_type: Type of voice to use
            reference_voice: Path to reference audio for cloning
        
        Returns:
            Dict with generation results
        """
        # Initialize model if needed
        self.initialize_model(voice_type)
        
        # Generate filename if not provided
        if not filename:
            timestamp = int(time.time())
            filename = f"narration_{timestamp}.wav"
        
        output_path = Path(output_dir) / filename
        
        start_time = time.time()
        
        try:
            if reference_voice:
                # Voice cloning
                audio_files = self.generator.clone_voice_from_sample(
                    script_text=script,
                    reference_audio=reference_voice,
                    output_path=str(output_path)
                )
            else:
                # Standard generation
                audio_files = self.generator.generate_voice_from_script(
                    script_text=script,
                    output_path=str(output_path)
                )
            
            generation_time = time.time() - start_time
            
            return {
                "status": "success",
                "audio_path": audio_files["original"],
                "optimized_audio_path": audio_files.get("optimized_for_transcription"),
                "model_used": voice_type,
                "generation_time": generation_time,
                "script_length": len(script),
                "voice_cloned": bool(reference_voice)
            }
            
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "audio_path": None,
                "generation_time": time.time() - start_time
            }


# Convenience functions for easy usage
def generate_voice_from_script(
    script: str,
    output_path: str = "assets/audio/narration.wav",
    voice_type: str = "english_fast",
    reference_voice: Optional[str] = None
) -> Dict[str, str]:
    """
    Simple function to generate voice from script
    
    Args:
        script: Text to convert to speech
        output_path: Where to save the audio
        voice_type: Type of voice model to use
        reference_voice: Optional reference audio for voice cloning
    
    Returns:
        Dict with paths to generated audio files
    """
    api = VoiceGeneratorAPI()
    result = api.generate_narration(
        script=script,
        output_dir=str(Path(output_path).parent),
        filename=Path(output_path).name,
        voice_type=voice_type,
        reference_voice=reference_voice
    )
    
    if result["status"] == "success":
        return {
            "original": result["audio_path"],
            "optimized_for_transcription": result["optimized_audio_path"]
        }
    else:
        raise Exception(f"Voice generation failed: {result['error']}")


def list_available_voice_types() -> Dict[str, str]:
    """List available voice types and their descriptions"""
    return {
        "english_fast": "Fast English TTS (Tacotron2)",
        "english_quality": "High-quality English TTS (Glow-TTS)",
        "multilingual": "Multilingual TTS with voice cloning",
        "voice_cloning": "Advanced voice cloning (YourTTS)",
        "bark": "Bark model with natural speech patterns"
    }


if __name__ == "__main__":
    # Example usage
    test_script = """
    Scientists have made an incredible discovery that could change everything we know about the universe. 
    This breakthrough might revolutionize our understanding of reality itself.
    """
    
    try:
        # Test basic voice generation
        audio_path = generate_voice_from_script(
            script=test_script,
            output_path="test_narration.wav",
            voice_type="english_fast"
        )
        print(f"Voice generated: {audio_path}")
        
        # Test API
        api = VoiceGeneratorAPI()
        result = api.generate_narration(test_script)
        print(f"API result: {result}")
        
    except Exception as e:
        print(f"Test failed: {e}")
        print("Make sure to install TTS: pip install TTS")