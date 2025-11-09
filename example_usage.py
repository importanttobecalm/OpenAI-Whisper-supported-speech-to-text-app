"""
Example usage of Whisper Streaming application.

This script demonstrates how to use the WhisperProcessor programmatically.
"""

from pathlib import Path
import logging
from whisper_app import WhisperProcessor, WhisperConfig

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)


def example_basic_transcription():
    """Basic transcription example."""
    print("\n" + "="*50)
    print("Example 1: Basic Transcription")
    print("="*50 + "\n")

    # Configure (using small model for faster processing)
    config = WhisperConfig(
        model_size="base",  # Use smaller model for demo
        device="cuda",  # Change to "cpu" if no GPU
        language="auto",  # Auto-detect language
        vac_enabled=True,  # Enable Voice Activity Detection
    )

    # Initialize processor
    processor = WhisperProcessor(config)

    # Transcribe (replace with your audio file)
    audio_file = Path("sample_audio.wav")

    if not audio_file.exists():
        print(f"⚠️  Audio file not found: {audio_file}")
        print("Please provide a valid audio file path.")
        return

    result = processor.transcribe(audio_file)

    # Display results
    print(f"Language detected: {result.language}")
    print(f"Duration: {result.duration:.2f}s")
    print(f"Processing time: {result.processing_time:.2f}s")
    print(f"Real-time factor: {result.duration/result.processing_time:.2f}x")
    print(f"\nTranscription:\n{result.full_text}\n")

    # Save to JSON
    result.to_json("output.json")
    print("✓ Saved to output.json")


def example_streaming_transcription():
    """Streaming transcription example with real-time output."""
    print("\n" + "="*50)
    print("Example 2: Streaming Transcription")
    print("="*50 + "\n")

    config = WhisperConfig(
        model_size="base",
        device="cuda",
        language="auto",
    )

    processor = WhisperProcessor(config)

    audio_file = Path("sample_audio.wav")

    if not audio_file.exists():
        print(f"⚠️  Audio file not found: {audio_file}")
        return

    print("Streaming output:\n")
    for segment in processor.transcribe_streaming(audio_file):
        print(f"[{segment.start:6.2f}s - {segment.end:6.2f}s] {segment.text}")


def example_multiple_formats():
    """Example showing different output formats."""
    print("\n" + "="*50)
    print("Example 3: Multiple Output Formats")
    print("="*50 + "\n")

    config = WhisperConfig(
        model_size="base",
        device="cuda",
        language="en",
    )

    processor = WhisperProcessor(config)

    audio_file = Path("sample_audio.wav")

    if not audio_file.exists():
        print(f"⚠️  Audio file not found: {audio_file}")
        return

    result = processor.transcribe(audio_file)

    # Save in different formats
    result.to_json("transcript.json")
    print("✓ Saved JSON: transcript.json")

    result.to_srt("subtitles.srt")
    print("✓ Saved SRT: subtitles.srt")

    with open("transcript.txt", "w", encoding="utf-8") as f:
        f.write(result.full_text)
    print("✓ Saved TXT: transcript.txt")


def example_custom_configuration():
    """Example with custom configuration."""
    print("\n" + "="*50)
    print("Example 4: Custom Configuration")
    print("="*50 + "\n")

    config = WhisperConfig(
        model_size="small",
        device="cuda",
        language="en",
        vac_enabled=True,
        min_chunk_size=1.5,  # Longer chunks
        beam_size=10,  # More thorough search
        temperature=0.0,  # Deterministic output
        include_confidence=True,
        include_timestamps=True,
    )

    processor = WhisperProcessor(config)

    audio_file = Path("sample_audio.wav")

    if not audio_file.exists():
        print(f"⚠️  Audio file not found: {audio_file}")
        return

    result = processor.transcribe(audio_file)

    # Show segments with confidence scores
    print("Segments with confidence scores:\n")
    for i, segment in enumerate(result.segments[:5], 1):  # Show first 5
        conf = segment.confidence if segment.confidence else 0
        print(f"{i}. [{segment.start:.2f}s - {segment.end:.2f}s] "
              f"(conf: {conf:.3f})")
        print(f"   {segment.text}\n")


def example_error_handling():
    """Example with error handling."""
    print("\n" + "="*50)
    print("Example 5: Error Handling")
    print("="*50 + "\n")

    try:
        config = WhisperConfig(
            model_size="base",
            device="cuda",
        )

        processor = WhisperProcessor(config)

        # Try to process non-existent file
        audio_file = Path("nonexistent.wav")
        result = processor.transcribe(audio_file)

    except FileNotFoundError as e:
        print(f"✗ File error: {e}")
    except ValueError as e:
        print(f"✗ Value error: {e}")
    except Exception as e:
        print(f"✗ Unexpected error: {e}")


def main():
    """Run all examples."""
    print("\n" + "="*70)
    print(" WHISPER STREAMING - USAGE EXAMPLES ".center(70, "="))
    print("="*70)

    # Check if sample audio exists
    sample_audio = Path("sample_audio.wav")
    if not sample_audio.exists():
        print("\n⚠️  NOTE: No sample_audio.wav found.")
        print("   Please provide an audio file to run these examples.")
        print("   You can:")
        print("   1. Create a file named 'sample_audio.wav' in this directory")
        print("   2. Modify the audio_file path in the examples")
        print("   3. Use the CLI: python -m whisper_app.main transcribe your_file.wav\n")

    try:
        # Run examples
        example_basic_transcription()
        # example_streaming_transcription()
        # example_multiple_formats()
        # example_custom_configuration()
        # example_error_handling()

    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user")
    except ImportError as e:
        print(f"\n✗ Import error: {e}")
        print("\nPlease install dependencies:")
        print("  pip install -r whisper_app/requirements.txt")

    print("\n" + "="*70)
    print(" EXAMPLES COMPLETED ".center(70, "="))
    print("="*70 + "\n")


if __name__ == "__main__":
    main()
