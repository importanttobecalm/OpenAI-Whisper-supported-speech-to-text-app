"""
Setup script for Whisper Streaming application.
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read README
readme_file = Path(__file__).parent / "whisper_app" / "README.md"
long_description = readme_file.read_text(encoding="utf-8") if readme_file.exists() else ""

# Read requirements
requirements_file = Path(__file__).parent / "whisper_app" / "requirements.txt"
requirements = []
if requirements_file.exists():
    with open(requirements_file, "r", encoding="utf-8") as f:
        requirements = [
            line.strip()
            for line in f
            if line.strip() and not line.startswith("#")
        ]

setup(
    name="whisper-streaming-app",
    version="1.0.0",
    description="Minimal Speech-to-Text application using Whisper Streaming",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Whisper Streaming",
    python_requires=">=3.8, <3.12",  # Match OpenAI Whisper official compatibility
    packages=find_packages(),
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "whisper-transcribe=whisper_app.main:main",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Multimedia :: Sound/Audio :: Speech",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    keywords="whisper speech-to-text transcription ai faster-whisper",
)
