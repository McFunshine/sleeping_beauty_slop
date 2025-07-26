#!/usr/bin/env python3
"""
AI Slop for Good - Main Entry Point
Transform research papers into engaging short-form videos
"""

import argparse
import sys
from pathlib import Path

# from paper_fetcher import PaperFetcher
from doc_processor import DocProcessor
from script_writer import ScriptWriter
from voiceGenElevenLabs import ElevenLabsVoiceGeneratorAPI
from image_generator import ImageGenerator
from VoiceTiming import VoiceTiming
from video_assembly import create_video_from_components
import utils as ut
import librosa
import json


def main():
    parser = argparse.ArgumentParser(description='Create engaging videos from research papers')
    parser.add_argument('--query', type=str, help='arXiv search query')
    parser.add_argument('--paper-id', type=str, help='Specific arXiv paper ID')
    parser.add_argument('--output', type=str, default='output/video.mp4', help='Output video path')
    parser.add_argument('--quality', type=str, default='medium', choices=['low', 'medium', 'high'],
                       help='Video quality: low (fast, 540x960), medium (balanced, 720x1280), high (best, 1080x1920)')
    
    args = parser.parse_args()
    
    # Create output directories
    Path('assets/images').mkdir(parents=True, exist_ok=True)
    Path('assets/audio').mkdir(parents=True, exist_ok=True)
    Path('assets/subtitles').mkdir(parents=True, exist_ok=True)
    Path('output').mkdir(parents=True, exist_ok=True)
    
    print("Starting AI Slop for Good pipeline...")
    
    # 1. Fetch paper
    # TODO

    # 2. Process document
    print("Processing document...")
    doc_processor = DocProcessor("assets/prompts/extract_paper_info_prompt_only_abstract.txt")
    # key_points = doc_processor.extract_key_points(ut.get_paper_text("article_sample.txt"))
    key_points = doc_processor.extract_key_points(ut.get_paper_text("neurips_2023.txt"))

    # 3. Generate script
    print("Generating script...")
    script_writer = ScriptWriter("assets/prompts/script_writing_prompt_genz_30_secs.txt")
    script = script_writer.generate_script(key_points)
    script_segments=script_writer.segment_script(script)
    
    # 4. Generate voice
    print("Generating voice narration with ElevenLabs...")
    voice_api = ElevenLabsVoiceGeneratorAPI()
    voice_result = voice_api.generate_narration(
        script=script,
        output_dir="assets/audio",
        filename="narration.mp3",
        voice="rachel",  # Using ElevenLabs voice
        model="multilingual_v2"
    )
    
    if voice_result["status"] != "success":
        print(f"Voice generation failed: {voice_result['error']}")
        return
    
    audio_path = voice_result["audio_path"]
    optimized_audio_path = voice_result["optimized_audio_path"]
    print(f"Voice generated: {audio_path}")

    # 5. Generate images
    print("Generating images...")
    image_generator = ImageGenerator()
    image_generator.generate_images(script_segments)
    
    # Get generated image paths
    image_paths = [
        "assets/images/image_0.png",
        "assets/images/image_1.png", 
        "assets/images/image_2.png"
    ]

    # 6. Create voice timing
    print("Extracting word-level timing...")
    voice_timing = VoiceTiming()
    timing_result = voice_timing.extract_timing_from_audio(optimized_audio_path or audio_path)
    
    # Convert to segments for video assembly
    segments = []
    words = timing_result.get('word_timings', [])
    if words:
        # Group words into segments (every 4 words)
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
    else:
        # Fallback to segment data
        segments = timing_result.get('segments', [])
    
    print(f"Created {len(segments)} timing segments")

    # 7. Assemble video
    print("Assembling final video...")
    
    # Get audio duration
    try:
        y, sr = librosa.load(audio_path)
        duration = librosa.get_duration(y=y, sr=sr)
    except:
        duration = timing_result.get('duration', 20.0)
    
    # Create video
    final_video_path = create_video_from_components(
        image_paths=image_paths,
        audio_path=audio_path,
        timing_data=segments,
        output_path=args.output,
        duration=duration,
        quality_preset=args.quality
    )

    print(f"✅ Video created successfully at: {final_video_path}")
    print(f"📊 Duration: {duration:.1f} seconds")
    print(f"🎵 Audio: {audio_path}")
    print(f"🖼️  Images: {len(image_paths)} generated")
    print(f"📝 Text segments: {len(segments)}")
    
    # Save timing data for reference
    timing_output = "assets/audio/timing_data.json"
    with open(timing_output, 'w') as f:
        json.dump(timing_result, f, indent=2)
    print(f"📋 Timing data saved: {timing_output}")


if __name__ == '__main__':
    main()