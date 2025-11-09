"""
Whisper Streaming - Minimal Speech-to-Text Application
"""

__version__ = "1.0.0"
__author__ = "Whisper Streaming"

from .config import WhisperConfig, MCPConfig, AppConfig
from .processor import WhisperProcessor, TranscriptionResult, TranscriptionSegment

__all__ = [
    "WhisperConfig",
    "MCPConfig",
    "AppConfig",
    "WhisperProcessor",
    "TranscriptionResult",
    "TranscriptionSegment",
]
