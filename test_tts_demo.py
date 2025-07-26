#!/usr/bin/env python3
"""
Simple test script to verify TTS voice generation works
Tests our voice_generator.py with a hardcoded 30-second script
"""

from voice_generator import generate_voice_from_script, VoiceGeneratorAPI
from pathlib import Path
import time


def main():
    """Test TTS with a hardcoded attention-grabbing script"""
    
    print("🎙️  Testing TTS Voice Generation")
    print("=" * 50)
    
    # Hardcoded 30-second script (approximately 300-400 characters for 30 seconds)
    test_script = """
    Scientists just discovered something that will blow your mind. 
    Black holes aren't actually black - they're rainbow colored portals to other dimensions! 
    This changes everything we thought we knew about physics. 
    The implications are absolutely insane and could revolutionize space travel forever.
    """
    
    print(f"Script to convert:")
    print(f'"{test_script.strip()}"')
    print(f"\nScript length: {len(test_script)} characters")
    print(f"Estimated duration: ~30 seconds\n")
    
    # Test 1: Simple function call
    print("🔥 Test 1: Simple voice generation")
    try:
        start_time = time.time()
        
        audio_path = generate_voice_from_script(
            script=test_script,
            output_path="assets/audio/test_demo.wav",
            voice_type="english_fast"
        )
        
        generation_time = time.time() - start_time
        
        if Path(audio_path).exists():
            file_size = Path(audio_path).stat().st_size
            print(f"✅ SUCCESS! Audio generated in {generation_time:.2f}s")
            print(f"📁 File: {audio_path}")
            print(f"📊 Size: {file_size:,} bytes")
        else:
            print(f"❌ FAILED: File not created at {audio_path}")
            
    except Exception as e:
        print(f"❌ FAILED: {e}")
        print("💡 Make sure you have TTS installed: pip install TTS")
        return
    
    # Test 2: API interface
    print(f"\n🚀 Test 2: API interface")
    try:
        api = VoiceGeneratorAPI()
        
        result = api.generate_narration(
            script=test_script,
            voice_type="english_fast",
            filename="test_api_demo.wav"
        )
        
        print(f"📋 API Result:")
        for key, value in result.items():
            if key == "generation_time":
                print(f"   {key}: {value:.2f}s")
            else:
                print(f"   {key}: {value}")
                
    except Exception as e:
        print(f"❌ API Test failed: {e}")
    
    # Test 3: Different voice types (if time permits)
    print(f"\n🎭 Test 3: Different voice types")
    voice_types = ["english_fast", "english_quality"]
    
    for voice_type in voice_types:
        try:
            print(f"   Testing {voice_type}...")
            result = generate_voice_from_script(
                script="This is a quick test of the voice.",
                output_path=f"assets/audio/test_{voice_type}.wav",
                voice_type=voice_type
            )
            print(f"   ✅ {voice_type}: SUCCESS")
        except Exception as e:
            print(f"   ❌ {voice_type}: {e}")
    
    print(f"\n" + "=" * 50)
    print("🎉 TTS Testing Complete!")
    print(f"\n📂 Check the 'assets/audio/' folder for generated files")
    print(f"🎧 Play the audio files to verify voice quality")


if __name__ == "__main__":
    main()