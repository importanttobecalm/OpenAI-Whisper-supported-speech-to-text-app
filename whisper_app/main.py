"""
Whisper Streaming - Minimal Speech-to-Text Application
Main CLI interface for transcribing audio files.
"""

import sys
import logging
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn
from rich.panel import Panel
from rich.table import Table

from .config import WhisperConfig, AppConfig
from .processor import WhisperProcessor, TranscriptionResult


# Initialize Typer app and Rich console
app = typer.Typer(
    name="whisper-transcribe",
    help="Minimal Speech-to-Text application using Whisper Streaming",
    add_completion=False,
)
console = Console()


def setup_logging(log_level: str = "INFO") -> None:
    """Setup logging configuration."""
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[logging.StreamHandler()],
    )


@app.command()
def transcribe(
    input_file: Path = typer.Argument(
        ...,
        exists=True,
        file_okay=True,
        dir_okay=False,
        readable=True,
        help="Path to input audio file (.wav, .mp3, .m4a, .flac, .ogg)",
    ),
    output: Optional[Path] = typer.Option(
        None,
        "--output",
        "-o",
        help="Path to output file (JSON). If not specified, uses input filename with .json extension",
    ),
    model: str = typer.Option(
        "large-v3",
        "--model",
        "-m",
        help="Whisper model size (tiny, base, small, medium, large, large-v2, large-v3)",
    ),
    language: str = typer.Option(
        "auto",
        "--language",
        "-l",
        help="Language code (e.g., 'en', 'tr', 'fr') or 'auto' for automatic detection",
    ),
    device: str = typer.Option(
        "cuda",
        "--device",
        "-d",
        help="Device to use: 'cuda' for GPU or 'cpu'",
    ),
    format: str = typer.Option(
        "json",
        "--format",
        "-f",
        help="Output format: 'json', 'txt', or 'srt'",
    ),
    no_vad: bool = typer.Option(
        False,
        "--no-vad",
        help="Disable Voice Activity Detection",
    ),
    streaming: bool = typer.Option(
        False,
        "--streaming",
        "-s",
        help="Enable streaming mode (real-time output)",
    ),
    verbose: bool = typer.Option(
        False,
        "--verbose",
        "-v",
        help="Enable verbose logging",
    ),
) -> None:
    """
    Transcribe an audio file to text using Whisper.

    Example:
        whisper-transcribe audio.wav --model large-v3 --language auto
    """
    # Setup logging
    log_level = "DEBUG" if verbose else "INFO"
    setup_logging(log_level)

    # Determine output path
    if output is None:
        output = input_file.with_suffix(f".{format}")

    # Display header
    console.print(
        Panel.fit(
            "[bold cyan]Whisper Streaming Transcription[/bold cyan]\n"
            f"Input: [yellow]{input_file}[/yellow]\n"
            f"Output: [green]{output}[/green]\n"
            f"Model: [blue]{model}[/blue] | Device: [magenta]{device}[/magenta]",
            border_style="cyan",
        )
    )

    try:
        # Configure Whisper
        config = WhisperConfig(
            model_size=model,
            device=device,
            language=language,
            vac_enabled=not no_vad,
            output_format=format,
        )

        # Initialize processor
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            TimeElapsedColumn(),
            console=console,
        ) as progress:
            # Model loading
            load_task = progress.add_task("[cyan]Loading model...", total=None)
            processor = WhisperProcessor(config)
            progress.update(load_task, completed=True)

            if streaming:
                # Streaming mode
                console.print("\n[bold green]Starting streaming transcription...[/bold green]\n")
                transcribe_task = progress.add_task(
                    "[yellow]Processing audio...", total=None
                )

                segments = []
                for segment in processor.transcribe_streaming(input_file):
                    console.print(
                        f"[{segment.start:.2f}s - {segment.end:.2f}s] {segment.text}"
                    )
                    segments.append(segment)

                progress.update(transcribe_task, completed=True)

                # Create result manually for streaming
                full_text = " ".join(seg.text.strip() for seg in segments)
                result = TranscriptionResult(
                    segments=segments,
                    full_text=full_text,
                    language=segments[0].language if segments else language,
                    duration=segments[-1].end if segments else 0,
                    processing_time=0,
                    model_info={
                        "model_size": model,
                        "device": device,
                        "compute_type": config.compute_type,
                    },
                    timestamp="",
                )
            else:
                # Standard mode with progress
                transcribe_task = progress.add_task(
                    "[yellow]Transcribing audio...", total=100
                )

                def update_progress(percent: float):
                    progress.update(transcribe_task, completed=percent)

                result = processor.transcribe(input_file, progress_callback=update_progress)
                progress.update(transcribe_task, completed=100)

        # Save output
        console.print(f"\n[bold green]Transcription completed![/bold green]\n")

        if format == "json":
            result.to_json(output)
        elif format == "srt":
            result.to_srt(output)
        else:  # txt
            with open(output, "w", encoding="utf-8") as f:
                f.write(result.full_text)
            console.print(f"Text saved to {output}")

        # Display results
        _display_results(result)

        console.print(f"\n[bold green]Output saved to:[/bold green] [yellow]{output}[/yellow]")

    except KeyboardInterrupt:
        console.print("\n[bold red]Transcription interrupted by user[/bold red]")
        sys.exit(130)
    except Exception as e:
        console.print(f"\n[bold red]Error:[/bold red] {str(e)}")
        if verbose:
            console.print_exception()
        sys.exit(1)


def _display_results(result: TranscriptionResult) -> None:
    """Display transcription results in a formatted table."""
    # Summary table
    table = Table(title="Transcription Summary", show_header=True, header_style="bold magenta")
    table.add_column("Metric", style="cyan", no_wrap=True)
    table.add_column("Value", style="green")

    table.add_row("Language", result.language.upper())
    table.add_row("Duration", f"{result.duration:.2f}s")
    table.add_row("Processing Time", f"{result.processing_time:.2f}s")
    table.add_row("Real-time Factor", f"{result.duration/result.processing_time:.2f}x")
    table.add_row("Segments", str(len(result.segments)))
    table.add_row("Model", result.model_info["model_size"])
    table.add_row("Device", result.model_info["device"])

    console.print(table)

    # Display first few segments
    console.print("\n[bold cyan]Transcription Preview:[/bold cyan]")
    preview_text = result.full_text[:500]
    if len(result.full_text) > 500:
        preview_text += "..."
    console.print(Panel(preview_text, border_style="green"))


@app.command()
def info() -> None:
    """Display information about available models and configuration."""
    console.print(Panel.fit("[bold cyan]Whisper Streaming Info[/bold cyan]", border_style="cyan"))

    # Models table
    models_table = Table(title="Available Models", show_header=True, header_style="bold magenta")
    models_table.add_column("Model", style="cyan")
    models_table.add_column("Parameters", style="yellow")
    models_table.add_column("VRAM (FP16)", style="green")
    models_table.add_column("Speed", style="blue")

    models = [
        ("tiny", "39M", "~1GB", "Very Fast"),
        ("base", "74M", "~1GB", "Fast"),
        ("small", "244M", "~2GB", "Medium"),
        ("medium", "769M", "~5GB", "Slow"),
        ("large", "1550M", "~10GB", "Very Slow"),
        ("large-v2", "1550M", "~10GB", "Very Slow"),
        ("large-v3", "1550M", "~10GB", "Very Slow"),
    ]

    for model, params, vram, speed in models:
        models_table.add_row(model, params, vram, speed)

    console.print(models_table)

    # Supported formats
    console.print("\n[bold cyan]Supported Audio Formats:[/bold cyan]")
    console.print("  .wav, .mp3, .m4a, .flac, .ogg")

    console.print("\n[bold cyan]Example Usage:[/bold cyan]")
    console.print("  whisper-transcribe audio.wav --model large-v3 --language auto")
    console.print("  whisper-transcribe audio.mp3 -o output.json -m medium -l en")
    console.print("  whisper-transcribe audio.wav --streaming --verbose")


@app.command()
def version() -> None:
    """Display version information."""
    console.print("[bold cyan]Whisper Streaming Transcription Tool[/bold cyan]")
    console.print("Version: 1.0.0")
    console.print("Backend: faster-whisper")


def main() -> None:
    """Main entry point."""
    app()


if __name__ == "__main__":
    main()
