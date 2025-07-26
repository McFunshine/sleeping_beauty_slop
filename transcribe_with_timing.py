#!/usr/bin/env python3
"""
Transcribe audio files with word-level timestamps using Groq's Whisper API.
This script extracts precise timing information for each word, useful for video synchronization.
"""

import os
import json
from groq import Groq
from pathlib import Path
from typing import Dict, List, Any

def transcribe_audio_with_timestamps(audio_file_path: str, groq_api_key: str = None) -> Dict[str, Any]:
    """
    Transcribe audio file with word-level timestamps using Groq's Whisper API.
    
    Args:
        audio_file_path: Path to the audio file
        groq_api_key: Groq API key (if not provided, will use GROQ_API_KEY env var)
    
    Returns:
        Dictionary containing transcription with word-level timestamps
    """
    
    # Initialize Groq client
    if groq_api_key:
        client = Groq(api_key=groq_api_key)
    else:
        client = Groq()  # Uses GROQ_API_KEY environment variable
    
    # Check if audio file exists
    audio_path = Path(audio_file_path)
    if not audio_path.exists():
        raise FileNotFoundError(f"Audio file not found: {audio_file_path}")
    
    print(f"Transcribing: {audio_file_path}")
    
    # Open and transcribe the audio file
    with open(audio_path, "rb") as file:
        transcription = client.audio.transcriptions.create(
            file=file,
            model="whisper-large-v3-turbo",  # Fast and accurate
            response_format="verbose_json",  # Required for timestamps
            timestamp_granularities=["word", "segment"],  # Get both word and segment timestamps
            language="en",  # Specify language for better accuracy
            temperature=0.0  # Deterministic output
        )
    
    return transcription

def extract_word_timings(transcription: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Extract word-level timing information from transcription response.
    
    Args:
        transcription: Groq transcription response
        
    Returns:
        List of word timing dictionaries with 'word', 'start', and 'end' keys
    """
    word_timings = []
    
    if hasattr(transcription, 'words') and transcription.words:
        for word_data in transcription.words:
            word_timings.append({
                'word': word_data.word.strip(),
                'start': word_data.start,
                'end': word_data.end
            })
    
    return word_timings

def save_timing_data(transcription: Dict[str, Any], word_timings: List[Dict[str, Any]], output_file: str):
    """
    Save transcription and timing data to JSON file.
    
    Args:
        transcription: Full transcription response
        word_timings: Extracted word timings
        output_file: Output JSON file path
    """
    output_data = {
        'text': transcription.text,
        'word_timings': word_timings,
        'segments': []
    }
    
    # Add segment information if available
    if hasattr(transcription, 'segments') and transcription.segments:
        for segment in transcription.segments:
            output_data['segments'].append({
                'text': segment.text,
                'start': segment.start,
                'end': segment.end,
                'avg_logprob': segment.avg_logprob,
                'no_speech_prob': segment.no_speech_prob
            })
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)
    
    print(f"Timing data saved to: {output_file}")

def main():
    """Main function to transcribe the test audio file."""
    
    # Path to your optimized audio file
    audio_file = "assets/audio/test_demo_optimized.mp4"
    
    # Output file for timing data
    output_file = "assets/audio/test_demo_timing.json"
    
    try:
        # Transcribe audio with timestamps
        print("Starting transcription with Groq Whisper...")
        transcription = transcribe_audio_with_timestamps(audio_file)
        
        # Extract word timings
        word_timings = extract_word_timings(transcription)
        
        # Print results
        print(f"\nTranscription: {transcription.text}")
        print(f"\nFound {len(word_timings)} words with timing data")
        
        # Show first few words as example
        if word_timings:
            print("\nFirst 10 words with timing:")
            for i, word_timing in enumerate(word_timings[:10]):
                print(f"  {i+1:2d}. '{word_timing['word']}' at {word_timing['start']:.2f}-{word_timing['end']:.2f}s")
        
        # Save timing data
        save_timing_data(transcription, word_timings, output_file)
        
        print(f"\n✅ Success! Word-level timing data extracted and saved.")
        print(f"📁 Output file: {output_file}")
        
    except FileNotFoundError as e:
        print(f"❌ Error: {e}")
        print("Make sure the audio file exists at the specified path.")
    except Exception as e:
        print(f"❌ Error during transcription: {e}")
        print("Make sure you have set the GROQ_API_KEY environment variable.")

if __name__ == "__main__":
    main()