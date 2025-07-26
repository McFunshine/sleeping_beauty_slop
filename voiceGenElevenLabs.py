"""Voice generator module - Text-to-speech with ElevenLabs API"""

import os
import time
import tempfile
import subprocess
from pathlib import Path
from typing import Optional, Union, List, Dict
from dotenv import load_dotenv

try:
    from elevenlabs.client import ElevenLabs
    from elevenlabs import play
except ImportError:
    print("ElevenLabs not installed. Run: pip install elevenlabs")
    ElevenLabs = None

load_dotenv()


class ElevenLabsVoiceGenerator:
    """Generate voice narration using ElevenLabs API"""
    
    # Popular voices and their IDs
    PRESET_VOICES = {
        "rachel": "21m00Tcm4TlvDq8ikWAM",      # Natural female
        "drew": "29vD33N1CtxCmqQRPOHJ",        # Well-rounded male
        "clyde": "2EiwWnXFnvU5JabPnv8n",       # War veteran male
        "bella": "EXAVITQu4vr4xnSDxMaL",       # Soft female
        "antoni": "ErXwobaYiN019PkySvjV",      # Well-rounded male
        "elli": "MF3mGyEYCl7XYWbV9V6O",       # Emotional female
        "josh": "TxGEqnHWrfWFTfGW9XjX",       # Deep male
        "arnold": "VR6AewLTigWG4xSOukaG",     # Crisp male
        "adam": "pNInz6obpgDQGcFmaJgB",       # Middle-aged male
        "sam": "yoZ06aMxZJJ28mfd3POQ",        # Raspy male
    }
    
    # High-quality models
    MODELS = {
        "multilingual_v2": "eleven_multilingual_v2",    # Best overall
        "english_v1": "eleven_monolingual_v1",          # Fast English
        "turbo_v2": "eleven_turbo_v2",                   # Fastest
        "turbo_v2_5": "eleven_turbo_v2_5"               # Latest fast model
    }
    
    def __init__(self, api_key: Optional[str] = None, default_voice: str = "rachel", default_model: str = "multilingual_v2"):
        """
        Initialize ElevenLabs client
        
        Args:
            api_key: ElevenLabs API key (if None, will use ELEVENLABS_API_KEY env var)
            default_voice: Default voice to use (key from PRESET_VOICES)
            default_model: Default model to use (key from MODELS)
        """
        if ElevenLabs is None:
            raise ImportError("ElevenLabs not installed. Run: pip install elevenlabs")
        
        # Get API key from parameter or environment
        self.api_key = api_key or os.getenv("ELEVENLABS_API_KEY")
        if not self.api_key:
            raise ValueError(
                "ElevenLabs API key required. Set ELEVENLABS_API_KEY environment variable "
                "or pass api_key parameter. Get your key at: https://elevenlabs.io/app/settings/api-keys"
            )
        
        # Initialize client
        self.client = ElevenLabs(api_key=self.api_key)
        
        # Set defaults
        self.default_voice_id = self.PRESET_VOICES.get(default_voice, default_voice)
        self.default_model_id = self.MODELS.get(default_model, default_model)
        
        print(f"ElevenLabs client initialized with voice: {default_voice}")
    
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
        voice: Optional[str] = None,
        model: Optional[str] = None,
        output_format: str = "mp3_44100_128",
        create_optimized_for_transcription: bool = True,
        **kwargs
    ) -> Dict[str, str]:
        """
        Main API: Generate voice from script text
        
        Args:
            script_text: Text to convert to speech
            output_path: Path to save the audio file
            voice: Voice to use (key from PRESET_VOICES or voice ID)
            model: Model to use (key from MODELS or model ID)
            output_format: Audio format (mp3_44100_128, mp3_22050_32, etc.)
            create_optimized_for_transcription: Whether to create optimized version
            **kwargs: Additional parameters
        
        Returns:
            Dict with paths to generated audio files
        """
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Resolve voice and model IDs
        voice_id = self.PRESET_VOICES.get(voice, voice) if voice else self.default_voice_id
        model_id = self.MODELS.get(model, model) if model else self.default_model_id
        
        try:
            print(f"Generating voice with ElevenLabs...")
            print(f"Voice: {voice or 'default'} (ID: {voice_id})")
            print(f"Model: {model or 'default'} (ID: {model_id})")
            
            # Generate audio
            audio = self.client.text_to_speech.convert(
                text=script_text,
                voice_id=voice_id,
                model_id=model_id,
                output_format=output_format,
                **kwargs
            )
            
            # Save audio to file
            with open(output_path, 'wb') as f:
                for chunk in audio:
                    if isinstance(chunk, bytes):
                        f.write(chunk)
            
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
        reference_audio_files: List[str],
        voice_name: str,
        output_path: str,
        voice_description: Optional[str] = None,
        create_optimized_for_transcription: bool = True
    ) -> Dict[str, str]:
        """
        Clone a voice from reference audio samples and use it for TTS
        
        Args:
            script_text: Text to speak
            reference_audio_files: List of paths to reference audio files
            voice_name: Name for the cloned voice
            output_path: Output audio path
            voice_description: Description of the voice
            create_optimized_for_transcription: Whether to create optimized version
        
        Returns:
            Dict with paths to generated audio files
        """
        try:
            print(f"Cloning voice '{voice_name}' from {len(reference_audio_files)} samples...")
            
            # Create cloned voice
            voice = self.client.voices.ivc.create(
                name=voice_name,
                description=voice_description or f"Cloned voice: {voice_name}",
                files=reference_audio_files
            )
            
            print(f"Voice cloned successfully with ID: {voice.voice_id}")
            
            # Generate speech with cloned voice
            return self.generate_voice_from_script(
                script_text=script_text,
                output_path=output_path,
                voice=voice.voice_id,  # Use the new voice ID
                create_optimized_for_transcription=create_optimized_for_transcription
            )
            
        except Exception as e:
            print(f"Error cloning voice: {e}")
            raise
    
    def list_available_voices(self) -> List[Dict]:
        """List all available voices"""
        try:
            response = self.client.voices.search()
            voices = []
            for voice in response.voices:
                voices.append({
                    "voice_id": voice.voice_id,
                    "name": voice.name,
                    "category": getattr(voice, 'category', 'unknown'),
                    "description": getattr(voice, 'description', ''),
                    "preview_url": getattr(voice, 'preview_url', None)
                })
            return voices
        except Exception as e:
            print(f"Error listing voices: {e}")
            return []
    
    def list_available_models(self) -> List[Dict]:
        """List all available models"""
        try:
            response = self.client.models.list()
            models = []
            for model in response.models:
                models.append({
                    "model_id": model.model_id,
                    "name": model.name,
                    "description": getattr(model, 'description', ''),
                    "languages": getattr(model, 'languages', [])
                })
            return models
        except Exception as e:
            print(f"Error listing models: {e}")
            return []
    
    def get_voice_info(self, voice_id: str) -> Dict:
        """Get information about a specific voice"""
        try:
            voice = self.client.voices.get(voice_id)
            return {
                "voice_id": voice.voice_id,
                "name": voice.name,
                "category": getattr(voice, 'category', 'unknown'),
                "description": getattr(voice, 'description', ''),
                "preview_url": getattr(voice, 'preview_url', None),
                "settings": getattr(voice, 'settings', {})
            }
        except Exception as e:
            print(f"Error getting voice info: {e}")
            return {}


class ElevenLabsVoiceGeneratorAPI:
    """High-level API for ElevenLabs voice generation"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.generator = None
        self.api_key = api_key
    
    def initialize_generator(self, voice: str = "rachel", model: str = "multilingual_v2"):
        """Initialize ElevenLabs generator"""
        print(f"Initializing ElevenLabs with voice: {voice}, model: {model}")
        self.generator = ElevenLabsVoiceGenerator(
            api_key=self.api_key,
            default_voice=voice,
            default_model=model
        )
    
    def generate_narration(
        self,
        script: str,
        output_dir: str = "assets/audio",
        filename: Optional[str] = None,
        voice: str = "rachel",
        model: str = "multilingual_v2"
    ) -> Dict[str, Union[str, float]]:
        """
        Generate narration from script
        
        Args:
            script: Text to convert to speech
            output_dir: Directory to save audio
            filename: Custom filename (auto-generated if None)
            voice: Voice to use
            model: Model to use
        
        Returns:
            Dict with generation results
        """
        # Initialize generator if needed
        if not self.generator:
            self.initialize_generator(voice, model)
        
        # Generate filename if not provided
        if not filename:
            timestamp = int(time.time())
            filename = f"narration_{timestamp}.mp3"
        
        output_path = Path(output_dir) / filename
        
        start_time = time.time()
        
        try:
            audio_files = self.generator.generate_voice_from_script(
                script_text=script,
                output_path=str(output_path),
                voice=voice,
                model=model
            )
            
            generation_time = time.time() - start_time
            
            return {
                "status": "success",
                "audio_path": audio_files["original"],
                "optimized_audio_path": audio_files.get("optimized_for_transcription"),
                "voice_used": voice,
                "model_used": model,
                "generation_time": generation_time,
                "script_length": len(script)
            }
            
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "audio_path": None,
                "generation_time": time.time() - start_time
            }


# Convenience functions
def generate_voice_from_script_elevenlabs(
    script: str,
    output_path: str = "assets/audio/narration.mp3",
    voice: str = "rachel",
    model: str = "multilingual_v2",
    api_key: Optional[str] = None
) -> Dict[str, str]:
    """
    Simple function to generate voice from script using ElevenLabs
    
    Args:
        script: Text to convert to speech
        output_path: Where to save the audio
        voice: Voice to use (rachel, drew, etc.)
        model: Model to use (multilingual_v2, turbo_v2, etc.)
        api_key: ElevenLabs API key
    
    Returns:
        Dict with paths to generated audio files
    """
    api = ElevenLabsVoiceGeneratorAPI(api_key=api_key)
    result = api.generate_narration(
        script=script,
        output_dir=str(Path(output_path).parent),
        filename=Path(output_path).name,
        voice=voice,
        model=model
    )
    
    if result["status"] == "success":
        return {
            "original": result["audio_path"],
            "optimized_for_transcription": result["optimized_audio_path"]
        }
    else:
        raise Exception(f"Voice generation failed: {result['error']}")


def list_available_elevenlabs_voices() -> Dict[str, str]:
    """List available preset voices and their descriptions"""
    return {
        "rachel": "Natural female voice",
        "drew": "Well-rounded male voice", 
        "clyde": "War veteran male voice",
        "bella": "Soft female voice",
        "antoni": "Well-rounded male voice",
        "elli": "Emotional female voice",
        "josh": "Deep male voice",
        "arnold": "Crisp male voice",
        "adam": "Middle-aged male voice",
        "sam": "Raspy male voice"
    }


if __name__ == "__main__":
    # Example usage
    test_script = """
    Scientists just made a breakthrough that will blow your mind! 
    They discovered that black holes aren't actually black - they're rainbow-colored portals to other dimensions.
    This changes everything we thought we knew about physics.
    """
    
    try:
        # Test basic voice generation
        audio_files = generate_voice_from_script_elevenlabs(
            script=test_script,
            output_path="test_elevenlabs_narration.mp3",
            voice="rachel",
            model="multilingual_v2"
        )
        print(f"ElevenLabs voice generated: {audio_files}")
        
        # Test API
        api = ElevenLabsVoiceGeneratorAPI()
        result = api.generate_narration(test_script, voice="drew")
        print(f"API result: {result}")
        
    except Exception as e:
        print(f"Test failed: {e}")
        print("Make sure to:")
        print("1. Install ElevenLabs: pip install elevenlabs")
        print("2. Set ELEVENLABS_API_KEY in your .env file")
        print("3. Get API key from: https://elevenlabs.io/app/settings/api-keys")