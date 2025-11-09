"""
MCP (Model Context Protocol) Server - 2025 Edition
Modern async server implementation for Whisper transcription service.
"""

import asyncio
import json
import logging
from typing import Dict, Any, Optional, List, AsyncGenerator
from pathlib import Path
from datetime import datetime
import uuid

from pydantic import BaseModel, Field
from loguru import logger

try:
    import mcp
    from mcp.server import Server
    from mcp.types import Tool, Resource, Prompt
    MCP_AVAILABLE = True
except ImportError:
    MCP_AVAILABLE = False
    logger.warning("MCP not installed. Install with: pip install mcp")

from .processor import WhisperProcessor, TranscriptionResult
from .config import WhisperConfig


# Pydantic models for type safety
class TranscriptionRequest(BaseModel):
    """Request model for transcription."""
    audio_path: str = Field(..., description="Path to audio file")
    model_size: str = Field(default="base", description="Whisper model size")
    language: str = Field(default="auto", description="Language code or 'auto'")
    output_format: str = Field(default="json", description="Output format: json, txt, srt")
    device: str = Field(default="cuda", description="Device: cuda or cpu")


class TranscriptionResponse(BaseModel):
    """Response model for transcription."""
    success: bool
    transcription: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    request_id: str
    processing_time: float


class MCPWhisperServer:
    """
    MCP Server for Whisper Transcription.
    Implements the Model Context Protocol for AI agent integration.
    """

    def __init__(self, config: Optional[WhisperConfig] = None):
        """Initialize MCP server."""
        self.config = config or WhisperConfig()
        self.processor: Optional[WhisperProcessor] = None
        self.server: Optional[Server] = None

        # Session management
        self.sessions: Dict[str, Dict[str, Any]] = {}

        logger.info("MCP Whisper Server initialized")

    async def initialize(self):
        """Initialize the server and processor."""
        if not MCP_AVAILABLE:
            raise RuntimeError("MCP is not installed")

        # Initialize Whisper processor
        self.processor = WhisperProcessor(self.config)

        # Create MCP server
        self.server = Server("whisper-transcription")

        # Register tools
        self._register_tools()

        # Register resources
        self._register_resources()

        logger.info("MCP Server ready")

    def _register_tools(self):
        """Register MCP tools."""
        if not self.server:
            return

        @self.server.tool()
        async def transcribe_audio(
            audio_path: str,
            model_size: str = "base",
            language: str = "auto",
            device: str = "cuda"
        ) -> Dict[str, Any]:
            """
            Transcribe an audio file to text.

            Args:
                audio_path: Path to the audio file
                model_size: Whisper model size (tiny, base, small, medium, large-v3)
                language: Language code (e.g., 'en', 'tr') or 'auto' for detection
                device: Device to use ('cuda' or 'cpu')

            Returns:
                Transcription result with text, timestamps, and metadata
            """
            request_id = str(uuid.uuid4())
            start_time = asyncio.get_event_loop().time()

            try:
                # Update config if needed
                if (self.config.model_size != model_size or
                    self.config.device != device):
                    self.config.model_size = model_size
                    self.config.device = device
                    self.processor = WhisperProcessor(self.config)

                # Transcribe
                result = await asyncio.to_thread(
                    self.processor.transcribe,
                    Path(audio_path)
                )

                processing_time = asyncio.get_event_loop().time() - start_time

                return {
                    "success": True,
                    "transcription": result.to_dict(),
                    "request_id": request_id,
                    "processing_time": processing_time
                }

            except Exception as e:
                logger.error(f"Transcription failed: {e}")
                return {
                    "success": False,
                    "error": str(e),
                    "request_id": request_id,
                    "processing_time": asyncio.get_event_loop().time() - start_time
                }

        @self.server.tool()
        async def get_supported_languages() -> List[str]:
            """Get list of supported languages."""
            return [
                "auto", "en", "tr", "de", "fr", "es", "it", "pt", "ru", "zh",
                "ja", "ko", "ar", "hi", "nl", "pl", "sv", "no", "da", "fi"
            ]

        @self.server.tool()
        async def get_supported_models() -> Dict[str, Dict[str, Any]]:
            """Get information about available Whisper models."""
            return {
                "tiny": {"parameters": "39M", "vram": "~1GB", "speed": "fastest"},
                "base": {"parameters": "74M", "vram": "~1GB", "speed": "fast"},
                "small": {"parameters": "244M", "vram": "~2GB", "speed": "medium"},
                "medium": {"parameters": "769M", "vram": "~5GB", "speed": "slow"},
                "large-v3": {"parameters": "1550M", "vram": "~10GB", "speed": "slowest"}
            }

        @self.server.tool()
        async def get_server_status() -> Dict[str, Any]:
            """Get current server status and capabilities."""
            import torch

            return {
                "status": "running",
                "model_loaded": self.processor is not None,
                "current_model": self.config.model_size,
                "device": self.config.device,
                "cuda_available": torch.cuda.is_available(),
                "gpu_count": torch.cuda.device_count() if torch.cuda.is_available() else 0,
                "active_sessions": len(self.sessions),
                "version": "2025.1.0"
            }

    def _register_resources(self):
        """Register MCP resources."""
        if not self.server:
            return

        @self.server.resource("transcription://recent")
        async def get_recent_transcriptions() -> str:
            """Get recent transcription results."""
            recent = list(self.sessions.values())[-10:]  # Last 10
            return json.dumps(recent, indent=2)

        @self.server.resource("config://current")
        async def get_current_config() -> str:
            """Get current configuration."""
            return json.dumps({
                "model_size": self.config.model_size,
                "device": self.config.device,
                "language": self.config.language,
                "vac_enabled": self.config.vac_enabled,
                "num_workers": self.config.num_workers
            }, indent=2)

    async def run(self, host: str = "localhost", port: int = 8765):
        """Run the MCP server."""
        if not MCP_AVAILABLE:
            raise RuntimeError("MCP is not installed")

        await self.initialize()

        logger.info(f"Starting MCP server on {host}:{port}")

        # Run server
        await self.server.run(
            transport="websocket",
            host=host,
            port=port
        )

    async def shutdown(self):
        """Graceful shutdown."""
        logger.info("Shutting down MCP server")
        if self.server:
            await self.server.shutdown()


# Convenience function
async def start_mcp_server(
    host: str = "localhost",
    port: int = 8765,
    config: Optional[WhisperConfig] = None
):
    """
    Start the MCP server.

    Args:
        host: Host to bind to
        port: Port to bind to
        config: Optional WhisperConfig
    """
    server = MCPWhisperServer(config)

    try:
        await server.run(host, port)
    except KeyboardInterrupt:
        logger.info("Received shutdown signal")
    finally:
        await server.shutdown()


if __name__ == "__main__":
    # Example: Run the server
    asyncio.run(start_mcp_server())
