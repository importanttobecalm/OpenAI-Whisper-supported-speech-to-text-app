"""
MCP (Model Context Protocol) adapter for Whisper Streaming.
Provides JSON-RPC compatible interface for context7 integration.
"""

import json
import logging
from typing import Dict, Any, Optional, List
from pathlib import Path
from dataclasses import dataclass, asdict
from datetime import datetime

from .processor import WhisperProcessor, TranscriptionResult
from .config import WhisperConfig, MCPConfig


logger = logging.getLogger(__name__)


@dataclass
class MCPRequest:
    """MCP JSON-RPC request structure."""

    jsonrpc: str = "2.0"
    method: str = ""
    params: Dict[str, Any] = None
    id: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {k: v for k, v in asdict(self).items() if v is not None}


@dataclass
class MCPResponse:
    """MCP JSON-RPC response structure."""

    jsonrpc: str = "2.0"
    result: Optional[Dict[str, Any]] = None
    error: Optional[Dict[str, Any]] = None
    id: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {k: v for k, v in asdict(self).items() if v is not None}

    def to_json(self) -> str:
        """Convert to JSON string."""
        return json.dumps(self.to_dict(), ensure_ascii=False)


@dataclass
class MCPError:
    """MCP error structure."""

    code: int
    message: str
    data: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {k: v for k, v in asdict(self).items() if v is not None}


# MCP Error Codes
class MCPErrorCodes:
    PARSE_ERROR = -32700
    INVALID_REQUEST = -32600
    METHOD_NOT_FOUND = -32601
    INVALID_PARAMS = -32602
    INTERNAL_ERROR = -32603


class MCPAdapter:
    """
    MCP adapter for Whisper transcription.
    Provides JSON-RPC compatible interface.
    """

    def __init__(self, whisper_config: WhisperConfig, mcp_config: MCPConfig):
        """
        Initialize MCP adapter.

        Args:
            whisper_config: Whisper configuration
            mcp_config: MCP configuration
        """
        self.whisper_config = whisper_config
        self.mcp_config = mcp_config
        self.processor = WhisperProcessor(whisper_config)

        logger.info(f"MCP Adapter initialized (protocol: {mcp_config.protocol_version})")

    def handle_request(self, request_data: str) -> str:
        """
        Handle MCP JSON-RPC request.

        Args:
            request_data: JSON-RPC request string

        Returns:
            JSON-RPC response string
        """
        try:
            # Parse request
            request_dict = json.loads(request_data)
            request = MCPRequest(**request_dict)

            # Validate JSON-RPC version
            if request.jsonrpc != "2.0":
                return self._error_response(
                    MCPErrorCodes.INVALID_REQUEST,
                    "Invalid JSON-RPC version",
                    request.id,
                )

            # Route to method handler
            method_name = request.method
            if not hasattr(self, f"_handle_{method_name}"):
                return self._error_response(
                    MCPErrorCodes.METHOD_NOT_FOUND,
                    f"Method not found: {method_name}",
                    request.id,
                )

            # Execute method
            handler = getattr(self, f"_handle_{method_name}")
            result = handler(request.params or {})

            # Success response
            response = MCPResponse(
                jsonrpc="2.0",
                result=result,
                id=request.id,
            )

            return response.to_json()

        except json.JSONDecodeError as e:
            return self._error_response(
                MCPErrorCodes.PARSE_ERROR,
                f"Parse error: {str(e)}",
            )
        except Exception as e:
            logger.error(f"Error handling request: {e}", exc_info=True)
            return self._error_response(
                MCPErrorCodes.INTERNAL_ERROR,
                f"Internal error: {str(e)}",
            )

    def _handle_transcribe(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle transcribe method.

        Params:
            audio_path: Path to audio file
            output_path: Optional output path
            format: Optional output format (json, txt, srt)

        Returns:
            Transcription result
        """
        # Validate params
        if "audio_path" not in params:
            raise ValueError("Missing required parameter: audio_path")

        audio_path = Path(params["audio_path"])
        output_path = params.get("output_path")
        output_format = params.get("format", "json")

        # Transcribe
        result = self.processor.transcribe(audio_path)

        # Save if output path specified
        if output_path:
            if output_format == "json":
                result.to_json(Path(output_path))
            elif output_format == "srt":
                result.to_srt(Path(output_path))
            else:
                with open(output_path, "w", encoding="utf-8") as f:
                    f.write(result.full_text)

        # Return result
        return {
            "success": True,
            "transcription": result.to_dict(),
            "output_path": str(output_path) if output_path else None,
        }

    def _handle_get_status(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle get_status method.

        Returns:
            Current status information
        """
        return {
            "status": "ready",
            "model": self.whisper_config.model_size,
            "device": self.whisper_config.device,
            "language": self.whisper_config.language,
            "mcp_version": self.mcp_config.protocol_version,
            "context7_compatible": self.mcp_config.context7_compatible,
            "timestamp": datetime.now().isoformat(),
        }

    def _handle_get_capabilities(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle get_capabilities method.

        Returns:
            Supported capabilities
        """
        return {
            "methods": [
                "transcribe",
                "get_status",
                "get_capabilities",
                "get_supported_formats",
            ],
            "audio_formats": list(self.whisper_config.supported_formats),
            "output_formats": ["json", "txt", "srt"],
            "features": {
                "vad": self.whisper_config.vac_enabled,
                "streaming": True,
                "auto_language_detection": True,
                "timestamps": True,
                "confidence_scores": True,
            },
        }

    def _handle_get_supported_formats(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle get_supported_formats method.

        Returns:
            Supported audio and output formats
        """
        return {
            "audio_formats": list(self.whisper_config.supported_formats),
            "output_formats": ["json", "txt", "srt"],
        }

    def _error_response(
        self,
        code: int,
        message: str,
        request_id: Optional[str] = None,
    ) -> str:
        """
        Create error response.

        Args:
            code: Error code
            message: Error message
            request_id: Optional request ID

        Returns:
            JSON-RPC error response string
        """
        error = MCPError(code=code, message=message)
        response = MCPResponse(
            jsonrpc="2.0",
            error=error.to_dict(),
            id=request_id,
        )
        return response.to_json()


# Example usage
if __name__ == "__main__":
    # Configure
    whisper_config = WhisperConfig(model_size="base", device="cpu")
    mcp_config = MCPConfig(enabled=True, context7_compatible=True)

    # Initialize adapter
    adapter = MCPAdapter(whisper_config, mcp_config)

    # Example request: get_status
    request = {
        "jsonrpc": "2.0",
        "method": "get_status",
        "id": "1",
    }

    response = adapter.handle_request(json.dumps(request))
    print("Status Response:")
    print(json.dumps(json.loads(response), indent=2))

    # Example request: get_capabilities
    request = {
        "jsonrpc": "2.0",
        "method": "get_capabilities",
        "id": "2",
    }

    response = adapter.handle_request(json.dumps(request))
    print("\nCapabilities Response:")
    print(json.dumps(json.loads(response), indent=2))
