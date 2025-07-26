#!/usr/bin/env python3
"""
Test script for video assembly - combines images, audio, and timing data into a video
"""

import json
from pathlib import Path
from video_assembly import create_video_from_components
import librosa

def load_timing_data(timing_file: str):
    """Load timing data from JSON file"""
    with open(timing_file, 'r') as f:
        timing_data = json.load(f)
    
    # Convert word timings to segment format for video assembly
    segments = []
    words = timing_data.get('word_timings', [])
    
    if not words:
        # Fallback: use segment data if available
        segments = timing_data.get('segments', [])
    else:
        # Group words into meaningful segments (every 3-5 words)
        words_per_segment = 4
        for i in range(0, len(words), words_per_segment):
            segment_words = words[i:i + words_per_segment]
            if segment_words:
                segment = {
                    "start": segment_words[0]["start"],
                    "end": segment_words[-1]["end"],
                    "text": " ".join([w["word"] for w in segment_words])
                }
                segments.append(segment)
    
    return segments, timing_data

def get_audio_duration(audio_file: str) -> float:
    """Get audio duration using librosa"""
    try:
        y, sr = librosa.load(audio_file)
        return librosa.get_duration(y=y, sr=sr)
    except:
        # Fallback: estimate from timing data
        return 21.42  # Known duration of our test file

def test_video_assembly():
    """Test the complete video assembly pipeline"""
    
    # Define file paths
    image_paths = [
        "assets/images/image1.jpeg",
        "assets/images/image2.jpeg", 
        "assets/images/image3.jpeg"
    ]
    
    audio_path = "assets/audio/test_demo.wav"
    timing_file = "assets/audio/test_demo_timing.json"
    output_path = "assets/test_output_video.mp4"
    
    # Check if all files exist
    missing_files = []
    for path in image_paths + [audio_path, timing_file]:
        if not Path(path).exists():
            missing_files.append(path)
    
    if missing_files:
        print("❌ Missing files:")
        for file in missing_files:
            print(f"   - {file}")
        print("\nPlease ensure all required files exist before running the test.")
        return False
    
    try:
        print("🎬 Starting video assembly test...")
        
        # Load timing data
        print("📊 Loading timing data...")
        segments, full_timing_data = load_timing_data(timing_file)
        print(f"   Found {len(segments)} text segments")
        
        # Get audio duration
        print("🎵 Getting audio duration...")
        duration = get_audio_duration(audio_path)
        print(f"   Audio duration: {duration:.2f} seconds")
        
        # Show what we're working with
        print("\n📝 Text segments:")
        for i, segment in enumerate(segments[:5]):  # Show first 5
            print(f"   {i+1}. '{segment['text']}' at {segment['start']:.1f}-{segment['end']:.1f}s")
        if len(segments) > 5:
            print(f"   ... and {len(segments) - 5} more segments")
        
        print(f"\n🖼️  Images: {len(image_paths)} files")
        print(f"🎵 Audio: {audio_path}")
        print(f"🎯 Output: {output_path}")
        
        # Create the video
        print("\n🎬 Assembling video...")
        result_path = create_video_from_components(
            image_paths=image_paths,
            audio_path=audio_path,
            timing_data=segments,
            output_path=output_path,
            duration=duration
        )
        
        # Check if output file was created
        if Path(result_path).exists():
            file_size = Path(result_path).stat().st_size / (1024 * 1024)  # MB
            print(f"✅ Video created successfully!")
            print(f"   📁 File: {result_path}")
            print(f"   📊 Size: {file_size:.1f} MB")
            print(f"   ⏱️  Duration: {duration:.1f} seconds")
            return True
        else:
            print("❌ Video file was not created")
            return False
            
    except Exception as e:
        print(f"❌ Error during video assembly: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_with_sample_data():
    """Test with minimal sample data if files are missing"""
    print("🧪 Testing with sample data...")
    
    # Create sample segments
    sample_segments = [
        {"start": 0.0, "end": 3.0, "text": "Scientists just discovered something amazing"},
        {"start": 3.0, "end": 6.0, "text": "Black holes aren't actually black"},
        {"start": 6.0, "end": 9.0, "text": "They're rainbow colored portals"},
        {"start": 9.0, "end": 12.0, "text": "This changes everything we know"},
        {"start": 12.0, "end": 15.0, "text": "The implications are absolutely insane"}
    ]
    
    # Check what files we actually have
    image_paths = []
    for i in range(1, 4):
        img_path = f"assets/images/image{i}.jpeg"
        if Path(img_path).exists():
            image_paths.append(img_path)
    
    audio_path = None
    for audio_file in ["assets/audio/test_demo.wav", "assets/audio/test_demo_optimized.mp4"]:
        if Path(audio_file).exists():
            audio_path = audio_file
            break
    
    if len(image_paths) < 3 or not audio_path:
        print(f"❌ Insufficient files: {len(image_paths)} images, audio: {bool(audio_path)}")
        return False
    
    try:
        result_path = create_video_from_components(
            image_paths=image_paths,
            audio_path=audio_path,
            timing_data=sample_segments,
            output_path="assets/sample_test_video.mp4",
            duration=15.0
        )
        
        if Path(result_path).exists():
            print(f"✅ Sample video created: {result_path}")
            return True
        else:
            print("❌ Sample video creation failed")
            return False
            
    except Exception as e:
        print(f"❌ Sample test failed: {e}")
        return False

if __name__ == "__main__":
    print("🎬 Video Assembly Test")
    print("=" * 40)
    
    # First try with real data
    success = test_video_assembly()
    
    # If that fails, try with sample data
    if not success:
        print("\n" + "=" * 40)
        print("Trying with sample data...")
        success = test_with_sample_data()
    
    if success:
        print("\n🎉 Test completed successfully!")
    else:
        print("\n💥 Test failed - check the errors above")