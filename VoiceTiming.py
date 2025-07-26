#!/usr/bin/env python3
"""
VoiceTiming.py - Extract word-level timing from audio using Groq Whisper API
"""

import os
import json
from groq import Groq
from pathlib import Path
from typing import Dict, List, Any, Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class VoiceTiming:
    """Extract word-level timing information from audio files using Groq Whisper API"""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize VoiceTiming with Groq API key
        
        Args:
            api_key: Groq API key (if not provided, uses GROQ_API_KEY from environment)
        """
        self.api_key = api_key or os.getenv('GROQ_API_KEY')
        if not self.api_key:
            raise ValueError("GROQ_API_KEY not found in environment variables or provided")
        
        self.client = Groq(api_key=self.api_key)
    
    def extract_timing_from_audio(self, audio_file_path: str) -> Dict[str, Any]:
        """
        Extract word-level timing from audio file
        
        Args:
            audio_file_path: Path to audio file
            
        Returns:
            Dictionary containing transcription and timing data
        """
        audio_path = Path(audio_file_path)
        if not audio_path.exists():
            raise FileNotFoundError(f"Audio file not found: {audio_file_path}")
        
        print(f"Processing audio: {audio_file_path}")
        
        with open(audio_path, "rb") as file:
            transcription = self.client.audio.transcriptions.create(
                file=file,
                model="whisper-large-v3-turbo",  # Fast and accurate
                response_format="verbose_json",  # Required for timestamps
                timestamp_granularities=["word", "segment"],  # Get both word and segment timestamps
                language="en",  # Specify language for better accuracy
                temperature=0.0  # Deterministic output
            )
        
        # Debug: print response structure
        print(f"Response type: {type(transcription)}")
        if hasattr(transcription, '__dict__'):
            print(f"Response attributes: {list(transcription.__dict__.keys())}")
        
        return self._process_transcription_response(transcription)
    
    def _process_transcription_response(self, transcription) -> Dict[str, Any]:
        """
        Process Groq transcription response into structured format
        
        Args:
            transcription: Groq API response
            
        Returns:
            Structured timing data
        """
        result = {
            "text": transcription.text,
            "word_timings": [],
            "segments": [],
            "duration": 0
        }
        
        # Extract word-level timings
        # Handle both object attributes and dictionary access
        words_data = None
        if hasattr(transcription, 'words'):
            words_data = transcription.words
        elif isinstance(transcription, dict) and 'words' in transcription:
            words_data = transcription['words']
        
        if words_data:
            for word_data in words_data:
                # Handle both object attributes and dictionary access
                if isinstance(word_data, dict):
                    word = word_data.get('word', '').strip()
                    start = float(word_data.get('start', 0))
                    end = float(word_data.get('end', 0))
                else:
                    word = word_data.word.strip()
                    start = float(word_data.start)
                    end = float(word_data.end)
                
                word_timing = {
                    "word": word,
                    "start": start,
                    "end": end,
                    "duration": float(end - start)
                }
                result["word_timings"].append(word_timing)
            
            # Calculate total duration from last word
            if result["word_timings"]:
                result["duration"] = result["word_timings"][-1]["end"]
        
        # Extract segment information
        segments_data = None
        if hasattr(transcription, 'segments'):
            segments_data = transcription.segments
        elif isinstance(transcription, dict) and 'segments' in transcription:
            segments_data = transcription['segments']
        
        if segments_data:
            for segment in segments_data:
                # Handle both object attributes and dictionary access
                if isinstance(segment, dict):
                    text = segment.get('text', '').strip()
                    start = float(segment.get('start', 0))
                    end = float(segment.get('end', 0))
                    avg_logprob = float(segment.get('avg_logprob', 0))
                    no_speech_prob = float(segment.get('no_speech_prob', 0))
                else:
                    text = segment.text.strip()
                    start = float(segment.start)
                    end = float(segment.end)
                    avg_logprob = float(segment.avg_logprob)
                    no_speech_prob = float(segment.no_speech_prob)
                
                segment_info = {
                    "text": text,
                    "start": start,
                    "end": end,
                    "duration": float(end - start),
                    "avg_logprob": avg_logprob,
                    "no_speech_prob": no_speech_prob
                }
                result["segments"].append(segment_info)
        
        return result
    
    def save_timing_data(self, timing_data: Dict[str, Any], output_file: str):
        """
        Save timing data to JSON file
        
        Args:
            timing_data: Timing data dictionary
            output_file: Output JSON file path
        """
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(timing_data, f, indent=2, ensure_ascii=False)
        
        print(f"Timing data saved to: {output_file}")
    
    def print_timing_summary(self, timing_data: Dict[str, Any]):
        """
        Print a summary of the timing data
        
        Args:
            timing_data: Timing data dictionary
        """
        print(f"\n📝 Transcription: {timing_data['text']}")
        print(f"⏱️  Total duration: {timing_data['duration']:.2f} seconds")
        print(f"📊 Words found: {len(timing_data['word_timings'])}")
        print(f"📑 Segments: {len(timing_data['segments'])}")
        
        if timing_data['word_timings']:
            print("\n🔤 First 10 words with timing:")
            for i, word_timing in enumerate(timing_data['word_timings'][:10]):
                print(f"  {i+1:2d}. '{word_timing['word']}' at {word_timing['start']:.2f}-{word_timing['end']:.2f}s")
        
        if len(timing_data['word_timings']) > 10:
            print(f"  ... and {len(timing_data['word_timings']) - 10} more words")


def process_audio_file(audio_file: str, output_file: Optional[str] = None) -> Dict[str, Any]:
    """
    Convenience function to process an audio file and get timing data
    
    Args:
        audio_file: Path to audio file
        output_file: Optional output JSON file path
        
    Returns:
        Timing data dictionary
    """
    # Initialize voice timing processor
    voice_timing = VoiceTiming()
    
    # Extract timing data
    timing_data = voice_timing.extract_timing_from_audio(audio_file)
    
    # Save to file if specified
    if output_file:
        voice_timing.save_timing_data(timing_data, output_file)
    
    # Print summary
    voice_timing.print_timing_summary(timing_data)
    
    return timing_data


if __name__ == "__main__":
    # Test with the demo audio file
    audio_file = "assets/audio/test_demo_optimized.mp4"
    output_file = "assets/audio/test_demo_timing.json"
    
    try:
        print("🎵 Starting voice timing extraction...")
        timing_data = process_audio_file(audio_file, output_file)
        print("\n✅ Voice timing extraction completed successfully!")
        
    except FileNotFoundError as e:
        print(f"❌ Error: {e}")
        print("Make sure the audio file exists at the specified path.")
    except ValueError as e:
        print(f"❌ Error: {e}")
        print("Make sure GROQ_API_KEY is set in your .env file.")
    except Exception as e:
        print(f"❌ Error during processing: {e}")