"""
Whisper processor for audio transcription using openai-whisper.
"""

import logging
import numpy as np
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
import json
from datetime import datetime

try:
    import whisper
except ImportError:
    raise ImportError("Please install openai-whisper: pip install -U openai-whisper")

from .config import WhisperConfig


logger = logging.getLogger(__name__)


@dataclass
class TranscriptionSegment:
    """Represents a transcription segment with timing information."""

    text: str
    start: float
    end: float
    confidence: Optional[float] = None
    language: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)


@dataclass
class TranscriptionResult:
    """Complete transcription result with metadata."""

    segments: List[TranscriptionSegment]
    full_text: str
    language: str
    duration: float
    processing_time: float
    model_info: Dict[str, str]
    timestamp: str
    confidence: Optional[float] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "segments": [seg.to_dict() for seg in self.segments],
            "full_text": self.full_text,
            "language": self.language,
            "duration": self.duration,
            "processing_time": self.processing_time,
            "model_info": self.model_info,
            "timestamp": self.timestamp,
            "confidence": self.confidence,
        }

    def to_json(self, file_path: Optional[Path] = None, indent: int = 2) -> str:
        """Convert to JSON string or save to file."""
        json_str = json.dumps(self.to_dict(), indent=indent, ensure_ascii=False)

        if file_path:
            file_path = Path(file_path)
            file_path.parent.mkdir(parents=True, exist_ok=True)
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(json_str)
            logger.info(f"Transcription saved to {file_path}")

        return json_str

    def to_srt(self, file_path: Optional[Path] = None) -> str:
        """Convert to SRT subtitle format."""
        srt_lines = []
        for i, segment in enumerate(self.segments, 1):
            start_time = self._format_timestamp(segment.start)
            end_time = self._format_timestamp(segment.end)
            srt_lines.append(f"{i}\n{start_time} --> {end_time}\n{segment.text.strip()}\n")

        srt_content = "\n".join(srt_lines)

        if file_path:
            file_path = Path(file_path)
            file_path.parent.mkdir(parents=True, exist_ok=True)
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(srt_content)
            logger.info(f"SRT saved to {file_path}")

        return srt_content

    @staticmethod
    def _format_timestamp(seconds: float) -> str:
        """Format seconds to SRT timestamp (HH:MM:SS,mmm)."""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        millis = int((seconds % 1) * 1000)
        return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"


class WhisperProcessor:
    """Whisper audio processor using openai-whisper."""

    def __init__(self, config: WhisperConfig):
        """
        Initialize Whisper processor.

        Args:
            config: WhisperConfig instance with model settings
        """
        self.config = config
        self.model = None
        self._load_model()

    def _load_model(self) -> None:
        """Load the Whisper model with GPU optimizations."""
        logger.info(
            f"Loading Whisper model: {self.config.model_size} on {self.config.device}"
        )

        # GPU optimizations
        if self.config.device == "cuda":
            try:
                import torch
                if torch.cuda.is_available():
                    # Set CUDA device
                    torch.cuda.set_device(self.config.device_index)
                    # Enable TF32 for better performance on Ampere GPUs
                    torch.backends.cuda.matmul.allow_tf32 = True
                    torch.backends.cudnn.allow_tf32 = True
                    # Set memory allocator for better performance
                    torch.cuda.empty_cache()
                    logger.info(f"GPU {self.config.device_index} initialized with TF32 enabled")
                else:
                    logger.warning("CUDA not available, falling back to CPU")
                    self.config.device = "cpu"
            except Exception as e:
                logger.warning(f"GPU optimization warning: {e}")

        try:
            # Load model using openai-whisper
            self.model = whisper.load_model(
                self.config.model_size,
                device=self.config.device
            )
            logger.info(f"Model loaded successfully: {self.config.model_size}")
        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            # Fallback to CPU if GPU fails
            if self.config.device == "cuda":
                logger.warning("Falling back to CPU")
                self.config.device = "cpu"
                self.model = whisper.load_model(
                    self.config.model_size,
                    device=self.config.device
                )
            else:
                raise

    def transcribe(
        self,
        audio_path: Path,
        progress_callback: Optional[callable] = None,
    ) -> TranscriptionResult:
        """
        Transcribe audio file.

        Args:
            audio_path: Path to audio file
            progress_callback: Optional callback function for progress updates

        Returns:
            TranscriptionResult with full transcription
        """
        import time

        start_time = time.time()
        audio_path = Path(audio_path)

        if not audio_path.exists():
            raise FileNotFoundError(f"Audio file not found: {audio_path}")

        if audio_path.suffix.lower() not in self.config.supported_formats:
            raise ValueError(
                f"Unsupported audio format: {audio_path.suffix}. "
                f"Supported formats: {self.config.supported_formats}"
            )

        logger.info(f"Starting transcription: {audio_path}")

        # Türkçe için özel prompt hazırla
        turkish_prompt = None
        detected_lang = self.config.language if self.config.language != "auto" else None

        if detected_lang == "tr" or detected_lang is None:
            # Türkçe için dilbilgisi ve noktalama kurallarını hatırlat
            turkish_prompt = (
                "Bu bir Türkçe görüşme kaydıdır. "
                "Lütfen doğru Türkçe dilbilgisi, noktalama işaretleri ve yazım kurallarını kullan. "
                "Cümle sonlarına nokta koy, virgülleri doğru kullan."
            )

        # Prepare transcription options (with AGGRESSIVE hallucination prevention)
        transcribe_options = {
            "language": None if self.config.language == "auto" else self.config.language,
            "task": "transcribe",
            "beam_size": self.config.beam_size,
            "best_of": self.config.best_of,
            "patience": self.config.patience,
            "length_penalty": self.config.length_penalty,
            "temperature": 0.0,  # Deterministic output - prevents hallucination
            "compression_ratio_threshold": 2.2,  # LOWERED: More aggressive repetition detection
            "logprob_threshold": -0.8,  # RAISED: Filter out low-confidence segments
            "no_speech_threshold": 0.7,  # RAISED: More aggressive silence detection
            "condition_on_previous_text": False,  # CHANGED: Prevents repetition from context
            "initial_prompt": turkish_prompt,  # Türkçe dilbilgisi hatırlatması
            "word_timestamps": False,  # Disabled by default for better performance
            "verbose": False,
        }

        # Transcribe with openai-whisper
        result = self.model.transcribe(str(audio_path), **transcribe_options)

        # Process segments with hallucination filtering
        transcription_segments = []
        previous_text = None
        repetition_count = 0
        MAX_REPETITIONS = 2  # Skip after 2 identical segments

        if "segments" in result:
            for segment in result["segments"]:
                text = segment["text"].strip()
                avg_logprob = segment.get("avg_logprob", 0)
                
                # Skip empty segments
                if not text:
                    continue
                
                # Skip low-confidence segments (hallucination indicator)
                if avg_logprob < -1.0:
                    logger.debug(f"Skipping low-confidence segment: {text[:50]}... (logprob: {avg_logprob:.2f})")
                    continue
                
                # Detect and skip repetitions
                if text == previous_text:
                    repetition_count += 1
                    if repetition_count > MAX_REPETITIONS:
                        logger.debug(f"Skipping repetition #{repetition_count}: {text[:50]}...")
                        continue
                else:
                    repetition_count = 0
                    previous_text = text
                
                # Check compression ratio (another hallucination indicator)
                text_length = len(text)
                duration = segment["end"] - segment["start"]
                if duration > 0:
                    chars_per_second = text_length / duration
                    # Turkish: ~10-20 chars/sec is normal, >30 is suspicious
                    if chars_per_second > 30:
                        logger.debug(f"Skipping high-compression segment: {chars_per_second:.1f} chars/sec")
                        continue
                
                trans_segment = TranscriptionSegment(
                    text=text,
                    start=segment["start"],
                    end=segment["end"],
                    confidence=avg_logprob if self.config.include_confidence else None,
                    language=result.get("language") if self.config.include_timestamps else None,
                )
                transcription_segments.append(trans_segment)

        # Get full text
        full_text = result.get("text", "").strip()

        # Calculate audio duration (estimate from segments or load audio)
        if transcription_segments:
            duration = transcription_segments[-1].end
        else:
            # Fallback: load audio to get duration
            audio = whisper.load_audio(str(audio_path))
            duration = len(audio) / whisper.audio.SAMPLE_RATE

        processing_time = time.time() - start_time

        # Calculate average confidence
        avg_confidence = None
        if self.config.include_confidence and transcription_segments:
            confidences = [seg.confidence for seg in transcription_segments if seg.confidence is not None]
            if confidences:
                avg_confidence = sum(confidences) / len(confidences)

        logger.info(
            f"Transcription completed in {processing_time:.2f}s "
            f"(language: {result.get('language', 'unknown')}, segments: {len(transcription_segments)})"
        )

        transcription_result = TranscriptionResult(
            segments=transcription_segments,
            full_text=full_text,
            language=result.get("language", "unknown"),
            duration=duration,
            processing_time=processing_time,
            confidence=avg_confidence,
            model_info={
                "model_size": self.config.model_size,
                "device": self.config.device,
            },
            timestamp=datetime.now().isoformat(),
        )

        return transcription_result

    def detect_language(self, audio_path: Path) -> Dict[str, float]:
        """
        Detect the language of an audio file.

        Args:
            audio_path: Path to audio file

        Returns:
            Dictionary of language probabilities
        """
        logger.info(f"Detecting language: {audio_path}")

        # Load audio and pad/trim to 30 seconds
        audio = whisper.load_audio(str(audio_path))
        audio = whisper.pad_or_trim(audio)

        # Make log-Mel spectrogram
        mel = whisper.log_mel_spectrogram(audio).to(self.model.device)

        # Detect language
        _, probs = self.model.detect_language(mel)

        detected_language = max(probs, key=probs.get)
        logger.info(f"Detected language: {detected_language} ({probs[detected_language]:.2%})")

        return probs

    def __del__(self):
        """Cleanup resources."""
        if hasattr(self, "model") and self.model is not None:
            del self.model
            logger.debug("Model unloaded")
