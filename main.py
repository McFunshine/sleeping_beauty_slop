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
# from voice_generator import VoiceGenerator
from image_generator import ImageGenerator
# from voice_timing import VoiceTiming
# from video_assembly import VideoAssembler
import utils as ut


def main():
    parser = argparse.ArgumentParser(description='Create engaging videos from research papers')
    parser.add_argument('--query', type=str, help='arXiv search query')
    parser.add_argument('--paper-id', type=str, help='Specific arXiv paper ID')
    parser.add_argument('--output', type=str, default='output/video.mp4', help='Output video path')
    
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
    key_points = doc_processor.extract_key_points(ut.get_paper_text("article_sample.txt"))

    # 3. Generate script
    print("Generating script...")
    script_writer = ScriptWriter("assets/prompts/script_writing_prompt_genz_30_secs.txt")
    script = script_writer.generate_script(key_points)
    script_segments=script_writer.segment_script(script)
    
    # 4. Generate voice
    # TODO

    # 5. Generate images
    print("Generating images...")
    image_generator = ImageGenerator()
    image_generator.generate_images(script_segments)

    # 6. Create voice timing
    # TODO


    # 7. Assemble video
    # TODO

    print(f"Video created at: {args.output}")


if __name__ == '__main__':
    main()