"""
Context7 Integration Client - 2025 Edition
Connect Whisper transcription service with Claude via Context7/MCP.
"""

import asyncio
import json
from typing import Dict, Any, Optional, List
from pathlib import Path
from datetime import datetime

from loguru import logger
import httpx
from anthropic import AsyncAnthropic

try:
    from dotenv import load_dotenv
    import os
    load_dotenv()
    ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
except ImportError:
    ANTHROPIC_API_KEY = None
    logger.warning("python-dotenv not installed. Set ANTHROPIC_API_KEY manually.")


class Context7WhisperClient:
    """
    Context7 client for integrating Whisper with Claude AI.
    Enables AI-powered transcription analysis and processing.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        mcp_server_url: str = "ws://localhost:8765"
    ):
        """
        Initialize Context7 client.

        Args:
            api_key: Anthropic API key (or from ANTHROPIC_API_KEY env var)
            mcp_server_url: MCP server WebSocket URL
        """
        self.api_key = api_key or ANTHROPIC_API_KEY
        self.mcp_server_url = mcp_server_url
        self.client: Optional[AsyncAnthropic] = None

        if self.api_key:
            self.client = AsyncAnthropic(api_key=self.api_key)
            logger.info("Context7 client initialized with Anthropic API")
        else:
            logger.warning("No API key provided. AI features disabled.")

    async def transcribe_with_context(
        self,
        audio_path: str,
        context: Optional[str] = None,
        model: str = "claude-sonnet-4-5-20250929"
    ) -> Dict[str, Any]:
        """
        Transcribe audio and analyze with Claude AI.

        Args:
            audio_path: Path to audio file
            context: Optional context for AI analysis
            model: Claude model to use

        Returns:
            Dict with transcription and AI analysis
        """
        if not self.client:
            raise ValueError("API key required for AI features")

        # Step 1: Transcribe via MCP
        transcription = await self._call_mcp_tool(
            "transcribe_audio",
            {"audio_path": audio_path}
        )

        if not transcription.get("success"):
            return transcription

        # Step 2: Analyze with Claude
        transcript_text = transcription["transcription"]["full_text"]

        analysis_prompt = f"""
Analyze this audio transcription:

{transcript_text}

{f'Context: {context}' if context else ''}

Provide:
1. Summary
2. Key points
3. Sentiment analysis
4. Action items (if any)
5. Topics covered
"""

        try:
            message = await self.client.messages.create(
                model=model,
                max_tokens=4096,
                messages=[{
                    "role": "user",
                    "content": analysis_prompt
                }]
            )

            analysis = message.content[0].text

            return {
                "success": True,
                "transcription": transcription["transcription"],
                "ai_analysis": {
                    "summary": analysis,
                    "model": model,
                    "timestamp": datetime.now().isoformat()
                }
            }

        except Exception as e:
            logger.error(f"Claude API error: {e}")
            return {
                "success": False,
                "error": str(e),
                "transcription": transcription["transcription"]
            }

    async def summarize_transcription(
        self,
        transcription: Dict[str, Any],
        style: str = "concise"
    ) -> str:
        """
        Summarize a transcription using Claude.

        Args:
            transcription: Transcription result dict
            style: Summary style (concise, detailed, bullet-points)

        Returns:
            Summary text
        """
        if not self.client:
            raise ValueError("API key required")

        text = transcription.get("full_text", "")

        style_prompts = {
            "concise": "Provide a brief 2-3 sentence summary.",
            "detailed": "Provide a comprehensive summary with main points.",
            "bullet-points": "Provide key points as bullet points."
        }

        prompt = f"""
Summarize this transcription.

Style: {style_prompts.get(style, style_prompts['concise'])}

Transcription:
{text}
"""

        message = await self.client.messages.create(
            model="claude-sonnet-4-5-20250929",
            max_tokens=1024,
            messages=[{"role": "user", "content": prompt}]
        )

        return message.content[0].text

    async def extract_action_items(
        self,
        transcription: Dict[str, Any]
    ) -> List[str]:
        """
        Extract action items from transcription.

        Args:
            transcription: Transcription result

        Returns:
            List of action items
        """
        if not self.client:
            raise ValueError("API key required")

        text = transcription.get("full_text", "")

        prompt = f"""
Extract all action items, tasks, or to-dos from this transcription.
Return them as a JSON array of strings.

Transcription:
{text}
"""

        message = await self.client.messages.create(
            model="claude-sonnet-4-5-20250929",
            max_tokens=1024,
            messages=[{"role": "user", "content": prompt}]
        )

        try:
            response_text = message.content[0].text
            # Try to parse JSON
            if "[" in response_text:
                json_start = response_text.index("[")
                json_end = response_text.rindex("]") + 1
                action_items = json.loads(response_text[json_start:json_end])
                return action_items
            else:
                # Fallback: split by newlines
                return [line.strip() for line in response_text.split("\n") if line.strip()]
        except Exception as e:
            logger.error(f"Failed to parse action items: {e}")
            return []

    async def translate_transcription(
        self,
        transcription: Dict[str, Any],
        target_language: str
    ) -> str:
        """
        Translate transcription to target language.

        Args:
            transcription: Transcription result
            target_language: Target language (e.g., 'Turkish', 'Spanish')

        Returns:
            Translated text
        """
        if not self.client:
            raise ValueError("API key required")

        text = transcription.get("full_text", "")

        prompt = f"""
Translate this transcription to {target_language}.
Maintain the tone and meaning.

Transcription:
{text}
"""

        message = await self.client.messages.create(
            model="claude-sonnet-4-5-20250929",
            max_tokens=4096,
            messages=[{"role": "user", "content": prompt}]
        )

        return message.content[0].text

    async def _call_mcp_tool(
        self,
        tool_name: str,
        params: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Call MCP server tool.

        Args:
            tool_name: Tool name
            params: Tool parameters

        Returns:
            Tool result
        """
        # For now, use HTTP/WebSocket MCP call
        # This would connect to the MCP server
        import websockets

        try:
            async with websockets.connect(self.mcp_server_url) as websocket:
                request = {
                    "jsonrpc": "2.0",
                    "method": tool_name,
                    "params": params,
                    "id": "1"
                }

                await websocket.send(json.dumps(request))
                response = await websocket.recv()

                return json.loads(response).get("result", {})

        except Exception as e:
            logger.error(f"MCP call failed: {e}")
            # Fallback: direct transcription
            from .processor import WhisperProcessor
            from .config import WhisperConfig

            config = WhisperConfig()
            processor = WhisperProcessor(config)

            result = await asyncio.to_thread(
                processor.transcribe,
                Path(params["audio_path"])
            )

            return {
                "success": True,
                "transcription": result.to_dict()
            }


# Example usage
async def example_usage():
    """Example of using Context7 integration."""

    # Initialize client
    client = Context7WhisperClient()

    # Transcribe with AI analysis
    result = await client.transcribe_with_context(
        audio_path="audio.wav",
        context="Meeting notes for project planning"
    )

    print("Transcription:", result["transcription"]["full_text"])
    print("\nAI Analysis:", result["ai_analysis"]["summary"])

    # Extract action items
    actions = await client.extract_action_items(result["transcription"])
    print("\nAction Items:", actions)

    # Translate
    translated = await client.translate_transcription(
        result["transcription"],
        target_language="Turkish"
    )
    print("\nTranslation:", translated)


if __name__ == "__main__":
    asyncio.run(example_usage())
