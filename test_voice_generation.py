"""Test script for voice generation functionality"""

from voice_generator import VoiceGeneratorAPI, generate_voice_from_script, list_available_voice_types
from pathlib import Path
import time


def test_voice_generation():
    """Test the voice generation system"""
    
    print("Testing Voice Generation System")
    print("=" * 50)
    
    # Test script for TTS
    test_script = """
    Scientists have discovered something incredible that could change everything we know about quantum physics.
    This breakthrough might revolutionize our understanding of reality itself.
    The implications are staggering and could lead to new technologies we never imagined.
    """
    
    # 1. Test available voice types
    print("\n1. Available Voice Types:")
    voice_types = list_available_voice_types()
    for voice_type, description in voice_types.items():
        print(f"   - {voice_type}: {description}")
    
    # 2. Test simple voice generation
    print("\n2. Testing Simple Voice Generation...")
    try:
        output_path = "assets/audio/test_simple.wav"
        
        audio_path = generate_voice_from_script(
            script=test_script,
            output_path=output_path,
            voice_type="english_fast"
        )
        
        if Path(audio_path).exists():
            print(f"   ✓ Voice generated successfully: {audio_path}")
            file_size = Path(audio_path).stat().st_size
            print(f"   ✓ File size: {file_size} bytes")
        else:
            print(f"   ✗ File not found: {audio_path}")
            
    except Exception as e:
        print(f"   ✗ Simple generation failed: {e}")
        print(f"   Note: This may fail if TTS is not installed. Run: pip install TTS")
    
    # 3. Test API interface
    print("\n3. Testing API Interface...")
    try:
        api = VoiceGeneratorAPI()
        
        result = api.generate_narration(
            script=test_script,
            voice_type="english_fast",
            filename="test_api.wav"
        )
        
        print(f"   API Result: {result}")
        
        if result["status"] == "success":
            print(f"   ✓ API generation successful")
            print(f"   ✓ Generation time: {result['generation_time']:.2f}s")
            print(f"   ✓ Script length: {result['script_length']} characters")
        else:
            print(f"   ✗ API generation failed: {result.get('error', 'Unknown error')}")
            
    except Exception as e:
        print(f"   ✗ API test failed: {e}")
    
    # 4. Test model info (if TTS is available)
    print("\n4. Testing Model Information...")
    try:
        from voice_generator import VoiceGenerator
        
        # This will fail gracefully if TTS is not installed
        generator = VoiceGenerator(model_name="english_fast", use_gpu=False)
        model_info = generator.get_model_info()
        
        print(f"   Model Info:")
        for key, value in model_info.items():
            print(f"     - {key}: {value}")
            
    except ImportError:
        print("   ⚠ TTS not installed - model info test skipped")
        print("   Install with: pip install TTS")
    except Exception as e:
        print(f"   ⚠ Model info test failed: {e}")
    
    # 5. Test file structure
    print("\n5. Testing File Structure...")
    assets_dir = Path("assets/audio")
    if assets_dir.exists():
        print(f"   ✓ Assets directory exists: {assets_dir}")
        audio_files = list(assets_dir.glob("*.wav"))
        print(f"   ✓ Found {len(audio_files)} audio files")
        for audio_file in audio_files:
            print(f"     - {audio_file.name}")
    else:
        print(f"   ⚠ Assets directory not found: {assets_dir}")
    
    print("\n" + "=" * 50)
    print("Voice Generation Test Complete")
    print("\nNext steps:")
    print("1. Install TTS: pip install TTS")
    print("2. Activate your virtual environment")
    print("3. Test with a real script from script_writer.py")
    print("4. Integrate with video_assembly.py")


def test_integration_example():
    """Example of how voice generation integrates with the full pipeline"""
    
    print("\nIntegration Example:")
    print("-" * 30)
    
    # Mock script from script_writer
    mock_script = """
    Did you know that black holes might not be black at all? 
    Recent discoveries suggest they could be gateways to other dimensions.
    Scientists are completely baffled by this revelation.
    """
    
    # Mock timing data that would come from Voxtral
    mock_timing = [
        {"start": 0.0, "end": 3.2, "text": "Did you know that black holes might not be black at all?"},
        {"start": 3.2, "end": 6.8, "text": "Recent discoveries suggest they could be gateways to other dimensions."},
        {"start": 6.8, "end": 9.5, "text": "Scientists are completely baffled by this revelation."}
    ]
    
    print(f"Script: {mock_script}")
    print(f"Expected timing segments: {len(mock_timing)}")
    print(f"Total duration: {mock_timing[-1]['end']} seconds")
    
    # This would be the actual integration:
    print("\nIntegration flow:")
    print("1. script_writer.py generates script")
    print("2. voice_generator.py converts script to audio")
    print("3. voice_timing.py (Mistral Voxel) provides timing data")
    print("4. image_generator.py creates 3 images")
    print("5. video_assembly.py combines everything")


if __name__ == "__main__":
    test_voice_generation()
    test_integration_example()