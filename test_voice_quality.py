#!/usr/bin/env python3
"""
Test script to compare voice quality across different TTS models
"""

import time
from pathlib import Path
from voice_generator import VoiceGeneratorAPI, list_available_voice_types

def test_voice_models():
    """Test different voice models for quality comparison"""
    
    # Test script with varied content
    test_script = """
    Scientists just made a breakthrough that will blow your mind! 
    They discovered that black holes aren't actually black - they're rainbow-colored portals to other dimensions.
    This changes everything we thought we knew about physics.
    The implications are absolutely insane and could revolutionize space travel forever.
    """
    
    # Models to test (ordered from basic to high quality)
    models_to_test = [
        ("english_fast", "Fast English TTS (Tacotron2)"),
        ("english_quality", "High-quality English TTS (Glow-TTS)"),
        ("xtts_v2", "XTTS v2 - Best Quality"),
        ("bark", "Bark - Very Natural")
    ]
    
    print("🎤 Voice Quality Test")
    print("=" * 50)
    print(f"Testing script: {test_script.strip()[:50]}...")
    print()
    
    api = VoiceGeneratorAPI()
    results = []
    
    for model_name, description in models_to_test:
        print(f"🔊 Testing: {model_name} ({description})")
        
        # Create output filename
        output_file = f"voice_test_{model_name}.wav"
        output_path = Path("assets/audio") / output_file
        
        try:
            start_time = time.time()
            
            # Generate voice
            result = api.generate_narration(
                script=test_script,
                output_dir="assets/audio",
                filename=output_file,
                voice_type=model_name
            )
            
            generation_time = time.time() - start_time
            
            if result["status"] == "success":
                file_size = Path(result["audio_path"]).stat().st_size / 1024  # KB
                
                print(f"   ✅ Success!")
                print(f"   📁 File: {result['audio_path']}")
                print(f"   ⏱️  Time: {generation_time:.1f}s")
                print(f"   📊 Size: {file_size:.1f} KB")
                
                results.append({
                    "model": model_name,
                    "description": description,
                    "path": result["audio_path"],
                    "optimized_path": result.get("optimized_audio_path"),
                    "time": generation_time,
                    "size_kb": file_size,
                    "success": True
                })
                
            else:
                print(f"   ❌ Failed: {result.get('error', 'Unknown error')}")
                results.append({
                    "model": model_name,
                    "description": description,
                    "success": False,
                    "error": result.get('error')
                })
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
            results.append({
                "model": model_name,
                "description": description,
                "success": False,
                "error": str(e)
            })
        
        print()
    
    # Summary
    print("📊 Test Summary")
    print("=" * 50)
    
    successful_tests = [r for r in results if r["success"]]
    
    if successful_tests:
        print(f"✅ Successful generations: {len(successful_tests)}/{len(results)}")
        print()
        
        print("🎯 Voice Quality Ranking (Recommended):")
        
        # Recommended order based on quality
        quality_order = ["bark", "xtts_v2", "english_quality", "english_fast"]
        
        for i, model_name in enumerate(quality_order, 1):
            model_result = next((r for r in successful_tests if r["model"] == model_name), None)
            if model_result:
                print(f"   {i}. {model_result['description']}")
                print(f"      📁 {model_result['path']}")
                print(f"      ⏱️  {model_result['time']:.1f}s generation time")
                print()
        
        print("🎵 To listen to the generated audio files:")
        for result in successful_tests:
            print(f"   afplay \"{result['path']}\"")
        
        print()
        print("💡 Recommendations:")
        print("   • For highest quality: Use 'bark' or 'xtts_v2'")
        print("   • For speed: Use 'english_fast'")
        print("   • For voice cloning: Use 'xtts_v2' with reference audio")
        
    else:
        print("❌ No successful voice generations")
        print("Check that TTS is properly installed: pip install TTS")

def test_voice_cloning():
    """Test voice cloning if a reference audio exists"""
    
    print("\n🎭 Voice Cloning Test")
    print("=" * 50)
    
    # Look for existing audio files to use as reference
    audio_dir = Path("assets/audio")
    reference_files = list(audio_dir.glob("*.wav")) + list(audio_dir.glob("*.mp3"))
    
    if not reference_files:
        print("❌ No reference audio files found in assets/audio/")
        print("   Add a reference voice file to test voice cloning")
        return
    
    reference_file = reference_files[0]
    print(f"🎤 Using reference: {reference_file}")
    
    # Shorter test script for cloning
    clone_script = "This is a test of voice cloning technology. How does this sound?"
    
    try:
        api = VoiceGeneratorAPI()
        
        result = api.generate_narration(
            script=clone_script,
            output_dir="assets/audio",
            filename="voice_clone_test.wav",
            voice_type="xtts_v2",  # Best model for cloning
            reference_voice=str(reference_file)
        )
        
        if result["status"] == "success":
            print(f"✅ Voice cloning successful!")
            print(f"📁 Cloned voice: {result['audio_path']}")
            print(f"🎵 Listen: afplay \"{result['audio_path']}\"")
        else:
            print(f"❌ Voice cloning failed: {result.get('error')}")
            
    except Exception as e:
        print(f"❌ Voice cloning error: {e}")

if __name__ == "__main__":
    # Ensure output directory exists
    Path("assets/audio").mkdir(parents=True, exist_ok=True)
    
    # Test different voice models
    test_voice_models()
    
    # Test voice cloning
    test_voice_cloning()
    
    print("\n🎉 Voice quality testing complete!")
    print("Try the different generated files to hear the quality differences.")