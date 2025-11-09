# Whisper Streaming - Minimal Speech-to-Text Application

A minimal, high-performance Speech-to-Text application using Whisper Streaming with faster-whisper backend.

## Features

- **Fast Transcription**: GPU-accelerated using faster-whisper backend
- **Multiple Formats**: Support for WAV, MP3, M4A, FLAC, OGG
- **Voice Activity Detection**: Intelligent audio segmentation
- **Multiple Output Formats**: JSON, TXT, SRT subtitles
- **Real-time Streaming**: Optional streaming mode for live output
- **Automatic Language Detection**: Supports 99+ languages
- **MCP Ready**: Structure prepared for Model Context Protocol integration

## Installation

### Requirements

- Python 3.10 or higher
- CUDA-capable GPU (optional, but recommended)
- FFmpeg (for audio format conversion)

### Setup

1. Clone or download this repository

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. For GPU support, ensure you have CUDA installed:

```bash
# Check CUDA availability
python -c "import torch; print(torch.cuda.is_available())"
```

## Quick Start

### Basic Usage

```bash
# Transcribe an audio file
python -m whisper_app.main transcribe audio.wav

# Specify model and language
python -m whisper_app.main transcribe audio.mp3 --model large-v3 --language en

# Save to specific output
python -m whisper_app.main transcribe audio.wav -o transcript.json

# Generate SRT subtitles
python -m whisper_app.main transcribe audio.mp3 --format srt -o subtitles.srt
```

### Advanced Options

```bash
# Streaming mode with real-time output
python -m whisper_app.main transcribe audio.wav --streaming --verbose

# CPU-only mode
python -m whisper_app.main transcribe audio.wav --device cpu

# Disable Voice Activity Detection
python -m whisper_app.main transcribe audio.wav --no-vad

# Multiple languages auto-detection
python -m whisper_app.main transcribe multilang.wav --language auto
```

### Display Information

```bash
# Show available models and info
python -m whisper_app.main info

# Show version
python -m whisper_app.main version
```

## Command Line Options

```
transcribe [OPTIONS] INPUT_FILE

Arguments:
  INPUT_FILE    Path to audio file [required]

Options:
  -o, --output PATH       Output file path (default: input_file.json)
  -m, --model TEXT        Model size: tiny, base, small, medium, large, large-v2, large-v3
                          [default: large-v3]
  -l, --language TEXT     Language code (e.g., 'en', 'tr', 'fr') or 'auto' [default: auto]
  -d, --device TEXT       Device: 'cuda' or 'cpu' [default: cuda]
  -f, --format TEXT       Output format: json, txt, srt [default: json]
  --no-vad               Disable Voice Activity Detection
  -s, --streaming        Enable streaming mode (real-time output)
  -v, --verbose          Enable verbose logging
  --help                 Show this message and exit
```

## Available Models

| Model     | Parameters | VRAM (FP16) | Speed      | Use Case                    |
|-----------|------------|-------------|------------|-----------------------------|
| tiny      | 39M        | ~1GB        | Very Fast  | Quick drafts, testing       |
| base      | 74M        | ~1GB        | Fast       | Simple transcriptions       |
| small     | 244M       | ~2GB        | Medium     | Balanced quality/speed      |
| medium    | 769M       | ~5GB        | Slow       | High quality                |
| large     | 1550M      | ~10GB       | Very Slow  | Best quality (older)        |
| large-v2  | 1550M      | ~10GB       | Very Slow  | Best quality (improved)     |
| large-v3  | 1550M      | ~10GB       | Very Slow  | Best quality (latest)       |

## Output Formats

### JSON Format

```json
{
  "segments": [
    {
      "text": "Hello, this is a test.",
      "start": 0.0,
      "end": 2.5,
      "confidence": -0.23,
      "language": "en"
    }
  ],
  "full_text": "Hello, this is a test.",
  "language": "en",
  "duration": 10.5,
  "processing_time": 3.2,
  "model_info": {
    "model_size": "large-v3",
    "device": "cuda",
    "compute_type": "float16"
  },
  "timestamp": "2025-01-08T12:00:00"
}
```

### SRT Format

```
1
00:00:00,000 --> 00:00:02,500
Hello, this is a test.

2
00:00:02,500 --> 00:00:05,000
This is the second segment.
```

### TXT Format

Plain text transcription without timestamps.

## Programmatic Usage

You can also use the library in your Python code:

```python
from pathlib import Path
from whisper_app import WhisperProcessor, WhisperConfig

# Configure
config = WhisperConfig(
    model_size="large-v3",
    device="cuda",
    language="auto",
    vac_enabled=True
)

# Initialize processor
processor = WhisperProcessor(config)

# Transcribe
result = processor.transcribe(Path("audio.wav"))

# Access results
print(result.full_text)
print(f"Language: {result.language}")
print(f"Duration: {result.duration}s")

# Save to file
result.to_json("output.json")
result.to_srt("subtitles.srt")

# Streaming mode
for segment in processor.transcribe_streaming(Path("audio.wav")):
    print(f"[{segment.start:.2f}s] {segment.text}")
```

## Configuration

The application uses a hierarchical configuration system:

```python
from whisper_app.config import WhisperConfig, AppConfig

# Customize Whisper settings
whisper_config = WhisperConfig(
    model_size="medium",
    device="cuda",
    language="en",
    min_chunk_size=1.0,
    vac_enabled=True,
    buffer_trimming="segment",
    beam_size=5,
    temperature=0.0
)

# Application settings
app_config = AppConfig(
    whisper=whisper_config,
    log_level="INFO",
    output_dir=Path("./transcripts")
)
```

## MCP Integration (Planned)

The application is structured to support MCP (Model Context Protocol) integration:

```python
from whisper_app.config import MCPConfig

mcp_config = MCPConfig(
    enabled=True,
    endpoint="ws://localhost:8765",
    context7_compatible=True
)
```

## Performance Tips

1. **GPU Acceleration**: Use CUDA for 5-10x speedup
2. **Model Selection**: Balance quality vs speed based on your needs
3. **VAD Filtering**: Enable for better segmentation and lower memory usage
4. **Chunk Size**: Increase for better accuracy, decrease for lower latency
5. **Compute Type**: Use float16 for GPU, int8 for CPU

## Troubleshooting

### CUDA Out of Memory

- Use a smaller model (e.g., medium instead of large-v3)
- Switch to CPU mode: `--device cpu`
- Close other GPU-intensive applications

### Audio Format Not Supported

- Install FFmpeg: `sudo apt install ffmpeg` (Linux) or download from ffmpeg.org
- Convert audio: `ffmpeg -i input.mp4 -ar 16000 output.wav`

### Slow Performance

- Ensure CUDA is properly installed
- Use a smaller model
- Enable VAD: remove `--no-vad` flag

## Project Structure

```
whisper_app/
├── __init__.py          # Package initialization
├── main.py              # CLI interface
├── processor.py         # Whisper processor class
├── config.py            # Configuration dataclasses
├── requirements.txt     # Dependencies
└── README.md           # This file
```

## Technical Details

- **Backend**: faster-whisper (CTranslate2)
- **Audio Processing**: librosa, soundfile
- **CLI Framework**: Typer
- **UI Components**: Rich
- **Type Hints**: Full type annotations
- **Python Version**: 3.10+

## License

MIT License - Feel free to use and modify

## Contributing

Contributions are welcome! Please feel free to submit issues or pull requests.

## Acknowledgments

- [faster-whisper](https://github.com/guillaumekln/faster-whisper) - Fast Whisper implementation
- [whisper_streaming](https://github.com/ufal/whisper_streaming) - Streaming Whisper implementation
- [OpenAI Whisper](https://github.com/openai/whisper) - Original Whisper model

## Support

For issues and questions:
- Create an issue on GitHub
- Check existing documentation
- Review faster-whisper documentation
