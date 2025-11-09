"""
Configuration settings for Whisper Streaming application.
"""

from dataclasses import dataclass
from typing import Literal
from pathlib import Path


@dataclass
class WhisperConfig:
    """Configuration for Whisper model and processing."""

    # Model settings
    model_size: str = "large-v3"
    device: str = "cuda"  # "cuda" or "cpu"
    compute_type: str = "float16"  # "float16" for GPU, "int8" for CPU
    device_index: int = 0  # GPU device index (0 for first GPU)
    num_workers: int = 4  # Number of workers for parallel processing

    # Language settings
    language: str = "auto"  # "auto" for automatic detection or specific language code

    # Processing settings
    min_chunk_size: float = 1.0  # Minimum chunk size in seconds
    vac_enabled: bool = True  # Voice Activity Controller
    buffer_trimming: str = "segment"  # "segment" or "sentence"

    # Output settings
    output_format: Literal["json", "txt", "srt"] = "json"
    include_timestamps: bool = True
    include_confidence: bool = True

    # Performance settings
    beam_size: int = 5
    best_of: int = 5
    patience: float = 1.0
    length_penalty: float = 1.0
    temperature: float = 0.0

    # Audio settings
    sample_rate: int = 16000
    supported_formats: tuple = (".wav", ".mp3", ".m4a", ".flac", ".ogg")

    def __post_init__(self):
        """Validate configuration after initialization."""
        if self.device == "cpu":
            self.compute_type = "int8"

        # OpenAI Whisper valid models (including turbo)
        valid_models = ["tiny", "base", "small", "medium", "large", "large-v2", "large-v3", "turbo"]
        if self.model_size not in valid_models:
            raise ValueError(f"Invalid model size: {self.model_size}. Valid models: {valid_models}")


@dataclass
class MCPConfig:
    """Configuration for MCP (Model Context Protocol) integration."""

    enabled: bool = False
    endpoint: str = "ws://localhost:8765"
    protocol_version: str = "1.0"
    context7_compatible: bool = True

    # JSON-RPC settings
    jsonrpc_version: str = "2.0"
    timeout: int = 30


@dataclass
class AppConfig:
    """Main application configuration."""

    whisper: WhisperConfig = None
    mcp: MCPConfig = None

    # Logging
    log_level: str = "INFO"
    log_file: Path = None

    # Directories
    output_dir: Path = Path("./output")
    temp_dir: Path = Path("./temp")

    def __post_init__(self):
        """Initialize nested configs if not provided."""
        if self.whisper is None:
            self.whisper = WhisperConfig()
        if self.mcp is None:
            self.mcp = MCPConfig()

        # Create directories if they don't exist
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.temp_dir.mkdir(parents=True, exist_ok=True)


# Default configuration instance
default_config = AppConfig()
