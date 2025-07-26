# AI Slop for Good

Transform boring research papers into engaging short-form video content using AI.

## Overview

This project creates TikTok/YouTube Shorts style videos from academic papers by:
1. Fetching papers from arXiv
2. Generating engaging scripts using LLMs
3. Creating cartoon visuals with AI image generation
4. Synthesizing voice narration
5. Assembling everything into a vertical video

## Architecture

```
[1] Paper Source (arXiv MCP)
          ↓
[2] Document Processing (Mistral)
          ↓
[3] Script Generation (Mistral LLM)
          ↓
[4] Asset Creation
   ├─ [4a] Image Generation (Flux via FAL.AI)
   └─ [4b] Voice Generation (elevenlabs / Coqui TTS)
          ↓
[5] Voice Timing (Groq Whisper)
          ↓
[6] Video Assembly (FFmpeg)
          ↓
[7] Output (MP4 vertical video)
```

## Project Structure

```
sleeping_beauty_slop/
├── main.py                    # Entry script
├── paper_fetcher.py           # arXiv MCP interface
├── doc_processor.py           # Mistral document processing
├── script_writer.py           # Mistral LLM script generation
├── voice_generator.py         # Coqui TTS interface
├── voiceGen_elevenlabs.py     # elevenlabs
├── image_generator.py         # Flux model via FAL.AI
├── VoiceTiming.py             # Groq Whisper for word-level timing
├── video_assembly.py          # FFmpeg composition
├── assets/
│   ├── images/
│   ├── audio/
│   └── subtitles/
├── output/
└── README.md
```

## Tools & APIs

| Stage | Tool/API | Purpose |
|-------|----------|---------|
| Paper Fetching | arXiv MCP | Fetch research papers |
| Document Processing | Mistral | Process and understand papers |
| Script Generation | Mistral LLM | Create 30-60 second engaging scripts |
| Voice Generation | ElevenLabs | High-quality AI voice synthesis |
| Voice Timing | Groq Whisper | Get word-level timing for captions |
| Image Generation | Black Forest Labs Flux (FAL.AI) | Create cartoon visuals |
| Video Assembly | FFmpeg | Combine all assets into video |

## Script Generation Prompt

```
You're an AI scriptwriter for TikTok videos. 
You take boring research and turn it into short, dramatic, or funny monologues that sound like something a curious and slightly unhinged narrator would say. 

Here's the research abstract:
{{RESEARCH_ABSTRACT}}

Now turn that into a 30–60 second video script with:
- A dramatic or funny hook (first line)
- A surprising twist
- A weird fact
- A closing line with flair
```

## Implementation Details

1. **Paper Selection**: Use arXiv MCP to search and select papers
2. **Document Processing**: Mistral processes the full paper content
3. **Script Writing**: Mistral LLM generates engaging 30-60 second scripts
4. **Voice Generation**: ElevenLabs API creates high-quality narration
5. **Voice Timing**: Groq Whisper provides precise word-level timestamps for caption sync
6. **Image Generation**: Flux model generates cartoon-style images via FAL.AI
7. **Video Assembly**: FFmpeg combines voice, images, and timed captions
8. **Output**: 1080x1920 vertical MP4 video ready for TikTok/YouTube Shorts

## Getting Started

```bash
# Clone the repository
git clone https://github.com/McFunshine/sleeping_beauty_slop.git
cd sleeping_beauty_slop

# Install dependencies
pip install -r requirements.txt

# Set up API keys in .env file
cat > .env << EOF
GROQ_API_KEY=your_groq_api_key
ELEVENLABS_API_KEY=your_elevenlabs_api_key
FAL_KEY=your_fal_ai_key
MISTRAL_API_KEY=your_mistral_api_key
EOF

# Test the pipeline
python test_video_assembly.py

# Run the main script
python main.py
```

## Current Status ✅

The complete video generation pipeline is now **fully functional** with:

- **✅ Voice Generation**: ElevenLabs API for high-quality AI voices
- **✅ Word-Level Timing**: Groq Whisper API integration for precise timestamp extraction  
- **✅ Video Assembly**: FFmpeg-based video creation with synchronized text overlays
- **✅ End-to-End Testing**: Working demo that creates videos from audio + images + timing data

**Test it yourself**: Run `python test_video_assembly.py` to see the complete pipeline in action!

## Output Specifications

- Format: MP4
- Resolution: 1080x1920 (vertical)
- Duration: 30-60 seconds
- Features: Voice narration, cartoon visuals, synchronized captions

## License

[License information to be added]
