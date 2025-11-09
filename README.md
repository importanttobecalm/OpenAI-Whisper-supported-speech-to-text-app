# 🎙️ Whisper Transcription App

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![OpenAI Whisper](https://img.shields.io/badge/OpenAI-Whisper-412991.svg)](https://github.com/openai/whisper)
[![Gradio](https://img.shields.io/badge/Gradio-UI-orange.svg)](https://gradio.app/)

Professional speech-to-text application powered by OpenAI's Whisper model with a modern web interface. Supports GPU acceleration, multiple languages, and AI-powered text enhancement.

![Whisper App Banner](https://img.shields.io/badge/🎯-Production_Ready-success)

## ✨ Features

### 🎤 Audio Processing
- **Multiple Format Support**: MP3, WAV, M4A, FLAC, OGG
- **Advanced Preprocessing**: Noise reduction, normalization, VAD
- **GPU Acceleration**: CUDA support for 5-10x faster processing
- **Real-time Transcription**: Streaming mode available

### 🤖 AI Models
- **OpenAI Whisper Models**: tiny, base, small, medium, large-v3, turbo
- **Gemini AI Enhancement**: Automatic punctuation and grammar correction
- **Multi-language Support**: 100+ languages including Turkish, English, German, French, Spanish
- **Automatic Language Detection**: Smart language identification

### 🖥️ User Interface
- **Modern Web UI**: Beautiful Gradio-based interface
- **One-Click Launch**: Desktop launcher for Mac users
- **Progress Tracking**: Real-time processing status
- **Multiple Output Formats**: TXT, JSON, SRT (subtitles)

### ⚡ Performance
- **Optimized Processing**: Multi-threaded audio handling
- **Model Caching**: Faster subsequent transcriptions
- **Batch Processing**: Handle multiple files
- **Memory Efficient**: Smart resource management

---

## 📋 Table of Contents

- [Quick Start](#-quick-start)
- [Installation](#-installation)
- [Usage](#-usage)
- [Mac Application](#-mac-application)
- [Configuration](#️-configuration)
- [API Keys](#-api-keys)
- [Examples](#-examples)
- [Performance Tips](#-performance-tips)
- [Troubleshooting](#-troubleshooting)
- [Contributing](#-contributing)
- [License](#-license)

---

## 🚀 Quick Start

### Windows

```bash
# 1. Clone the repository
git clone https://github.com/importanttobecalm/OpenAI-Whisper-supported-speech-to-text-app.git
cd OpenAI-Whisper-supported-speech-to-text-app

# 2. Install dependencies
pip install -r requirements.txt

# 3. Launch web interface
start_web_ui.bat
```

### Mac / Linux

```bash
# 1. Clone the repository
git clone https://github.com/importanttobecalm/OpenAI-Whisper-supported-speech-to-text-app.git
cd OpenAI-Whisper-supported-speech-to-text-app

# 2. Install dependencies
pip3 install -r requirements.txt

# 3. Launch web interface
./start_web_ui.sh
```

**That's it!** The web interface will open automatically in your browser at `http://127.0.0.1:7865`

---

## 📦 Installation

### Prerequisites

- **Python**: 3.8 or higher
- **FFmpeg**: Required for audio processing
- **CUDA** (Optional): For GPU acceleration

### Step 1: Install Python Dependencies

```bash
# Install all requirements
pip install -r requirements.txt

# OR install separately:
pip install -r requirements_audio.txt  # Audio processing
pip install -r requirements_gemini.txt # Gemini AI (optional)
```

### Step 2: Install FFmpeg

#### Windows
```bash
python install_ffmpeg.py
```

#### Mac
```bash
brew install ffmpeg
```

#### Linux
```bash
sudo apt update
sudo apt install ffmpeg
```

### Step 3: GPU Setup (Optional but Recommended)

#### CUDA (NVIDIA GPU)
```bash
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

#### ROCm (AMD GPU)
```bash
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/rocm5.6
```

---

## 🎯 Usage

### Web Interface (Recommended)

1. **Launch the application**:
   ```bash
   python web_ui.py
   ```

2. **Upload your audio file** via the web interface

3. **Configure settings**:
   - Select model (recommend: `small` for Turkish, `turbo` for speed)
   - Choose language (or use auto-detect)
   - Select device (GPU or CPU)
   - Choose output format

4. **Optional: Enable Gemini Enhancement**
   - Check "Gemini ile Metin İyileştir"
   - Enter your API key
   - Get improved punctuation and grammar

5. **Click "🚀 Transkribe Et"** and wait for results!

### Command Line Interface

```bash
# Basic usage
python -m whisper_app.main audio.mp3

# Specify model and language
python -m whisper_app.main audio.wav --model large-v3 --language tr

# Output to specific format
python -m whisper_app.main audio.mp3 --format srt --output subtitles.srt

# Use GPU acceleration
python -m whisper_app.main audio.wav --device cuda --model turbo

# Streaming mode
python -m whisper_app.main audio.mp3 --streaming
```

### Python API

```python
from whisper_app import WhisperProcessor, WhisperConfig
from pathlib import Path

# Configure
config = WhisperConfig(
    model_size="small",
    device="cuda",  # or "cpu"
    language="tr",  # or "auto"
    vac_enabled=True,
    include_timestamps=True
)

# Process audio
processor = WhisperProcessor(config)
result = processor.transcribe(Path("audio.mp3"))

# Access results
print(result.full_text)
print(f"Language: {result.language}")
print(f"Duration: {result.duration}s")

# Save to file
result.to_json(Path("output.json"))
result.to_srt(Path("subtitles.srt"))
```

---

## 🍎 Mac Application

For Mac users, we provide a native `.app` launcher with GUI!

### Quick Launch

```bash
cd mac_app
python3 whisper_app_launcher.py
```

### Create .app Bundle

```bash
cd mac_app
chmod +x create_mac_app.sh
./create_mac_app.sh
```

Then move `dist/Whisper Transcription.app` to your Applications folder!

**Features**:
- ✅ One-click launch
- ✅ Native Mac interface
- ✅ API key management
- ✅ Auto-opens in browser

See [Mac README](mac_app/README_MAC.md) for details.

---

## ⚙️ Configuration

### Model Selection Guide

| Model | Speed | Quality | VRAM | Best For |
|-------|-------|---------|------|----------|
| **tiny** | ⚡⚡⚡⚡⚡ | ⭐⭐ | ~1GB | Quick tests |
| **base** | ⚡⚡⚡⚡ | ⭐⭐⭐ | ~1GB | Daily use |
| **small** | ⚡⚡⚡ | ⭐⭐⭐⭐ | ~2GB | **Recommended for Turkish** |
| **medium** | ⚡⚡ | ⭐⭐⭐⭐⭐ | ~5GB | High quality |
| **large-v3** | ⚡ | ⭐⭐⭐⭐⭐ | ~10GB | Best quality |
| **turbo** | ⚡⚡⚡⚡ | ⭐⭐⭐⭐⭐ | ~6GB | **Speed + Quality** |

### Language Codes

- `auto` - Automatic detection
- `tr` - Turkish
- `en` - English
- `de` - German
- `fr` - French
- `es` - Spanish
- `ar` - Arabic
- `zh` - Chinese
- `ru` - Russian
- ...and 90+ more!

### Environment Variables

Create a `.env` file:

```env
# Gemini API (optional)
GEMINI_API_KEY=your_api_key_here

# Model settings
WHISPER_MODEL=small
WHISPER_DEVICE=cuda
WHISPER_LANGUAGE=auto

# Server settings
WEB_UI_PORT=7865
WEB_UI_HOST=127.0.0.1
```

---

## 🔑 API Keys

### Gemini API (Optional)

For AI-powered text enhancement:

1. Get API key: https://makersuite.google.com/app/apikey
2. Add to `.env` or enter in web UI
3. Enable "Gemini Enhancement" checkbox

**Benefits**:
- ✅ Automatic punctuation
- ✅ Grammar correction
- ✅ Improved readability
- ✅ Language-aware formatting

---

## 📚 Examples

### Example 1: Podcast Transcription

```bash
python -m whisper_app.main podcast.mp3 \
  --model medium \
  --language en \
  --format srt \
  --output podcast_subtitles.srt
```

### Example 2: Turkish Interview with Enhancement

```python
from whisper_app import WhisperProcessor, WhisperConfig
from gemini_enhancer import GeminiEnhancer
from pathlib import Path

# Transcribe
config = WhisperConfig(model_size="small", language="tr")
processor = WhisperProcessor(config)
result = processor.transcribe(Path("interview.mp3"))

# Enhance with Gemini
enhancer = GeminiEnhancer(api_key="your_key")
enhanced = enhancer.enhance_transcript(result.full_text, language="tr")

print(enhanced)
```

### Example 3: Batch Processing

```python
from pathlib import Path
from whisper_app import WhisperProcessor, WhisperConfig

config = WhisperConfig(model_size="turbo", device="cuda")
processor = WhisperProcessor(config)

audio_files = Path("audio_folder").glob("*.mp3")

for audio_file in audio_files:
    result = processor.transcribe(audio_file)
    output_file = audio_file.with_suffix(".txt")
    output_file.write_text(result.full_text, encoding="utf-8")
    print(f"✅ Processed: {audio_file.name}")
```

---

## ⚡ Performance Tips

### GPU Optimization

1. **Use CUDA**: 5-10x faster than CPU
2. **Choose turbo model**: Best speed/quality ratio
3. **Enable TF32**: Automatic on Ampere+ GPUs
4. **Use float16**: Reduces VRAM usage

### For Large Files

1. Use **VAD** (Voice Activity Detection) - removes silence
2. Choose **smaller model** (small/base) for 1+ hour audio
3. Enable **streaming mode** for very long files
4. Consider **splitting** audio into chunks

### Memory Management

```python
# Clear model cache
import torch
torch.cuda.empty_cache()

# Use CPU for very large files
config = WhisperConfig(device="cpu", model_size="base")
```

---

## 🔧 Troubleshooting

### Common Issues

#### "CUDA out of memory"
```bash
# Solution 1: Use smaller model
python web_ui.py  # Select "small" or "base" model

# Solution 2: Use CPU
python web_ui.py  # Select "CPU" device

# Solution 3: Clear cache
import torch; torch.cuda.empty_cache()
```

#### "FFmpeg not found"
```bash
# Windows
python install_ffmpeg.py

# Mac
brew install ffmpeg

# Linux
sudo apt install ffmpeg
```

#### "Model download fails"
```bash
# Use HuggingFace mirror
export HF_ENDPOINT=https://hf-mirror.com

# Or manually download
python -c "import whisper; whisper.load_model('small')"
```

#### "Poor transcription quality"

1. Use **at least small model** for Turkish
2. **Specify language** explicitly (don't use auto)
3. Enable **Gemini enhancement** for better punctuation
4. Check **audio quality** (minimum 16kHz sample rate)

---

## 🏗️ Project Structure

```
.
├── web_ui.py                  # Main web interface
├── whisper_app/              # Core package
│   ├── __init__.py
│   ├── config.py             # Configuration
│   ├── processor.py          # Whisper processing
│   ├── main.py               # CLI interface
│   └── README.md
├── mac_app/                  # Mac launcher
│   ├── whisper_app_launcher.py
│   ├── create_mac_app.sh
│   └── README_MAC.md
├── audio_preprocessing.py    # Audio utilities
├── gemini_enhancer.py        # AI enhancement
├── install_ffmpeg.py         # FFmpeg installer
├── start_web_ui.bat          # Windows launcher
├── start_web_ui.sh           # Unix launcher
├── requirements.txt          # Main dependencies
├── requirements_audio.txt    # Audio processing
├── requirements_gemini.txt   # Gemini API
└── README.md                 # This file
```

---

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- [OpenAI Whisper](https://github.com/openai/whisper) - The amazing speech recognition model
- [Gradio](https://gradio.app/) - Beautiful web interface framework
- [Google Gemini](https://deepmind.google/technologies/gemini/) - AI text enhancement
- [faster-whisper](https://github.com/guillaumekln/faster-whisper) - Optimized inference

---

## 📊 Stats

- **Processing Speed**: Up to 10x real-time with GPU
- **Supported Formats**: 5+ audio formats
- **Languages**: 100+ supported
- **Models**: 6 Whisper variants available
- **Accuracy**: 95%+ for clear audio

---

## 🌟 Star History

If you find this project useful, please consider giving it a star! ⭐

---

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/importanttobecalm/OpenAI-Whisper-supported-speech-to-text-app/issues)
- **Discussions**: [GitHub Discussions](https://github.com/importanttobecalm/OpenAI-Whisper-supported-speech-to-text-app/discussions)

---

<div align="center">

**Made with ❤️ for the speech recognition community**

[⬆ Back to Top](#-whisper-transcription-app)

</div>
