# Contributing to Whisper Transcription App

First off, thank you for considering contributing to Whisper Transcription App! 🎉

## 📋 Table of Contents

- [Code of Conduct](#code-of-conduct)
- [How Can I Contribute?](#how-can-i-contribute)
- [Development Setup](#development-setup)
- [Pull Request Process](#pull-request-process)
- [Coding Standards](#coding-standards)
- [Testing](#testing)

## Code of Conduct

This project adheres to a code of conduct. By participating, you are expected to uphold this code. Please report unacceptable behavior to the project maintainers.

## How Can I Contribute?

### 🐛 Reporting Bugs

Before creating bug reports, please check the existing issues to avoid duplicates. When you create a bug report, include as many details as possible:

- **Clear title and description**
- **Steps to reproduce** the issue
- **Expected vs actual behavior**
- **Screenshots** if applicable
- **Environment details** (OS, Python version, GPU info)
- **Error messages and logs**

### 💡 Suggesting Enhancements

Enhancement suggestions are tracked as GitHub issues. When creating an enhancement suggestion, include:

- **Clear and descriptive title**
- **Detailed description** of the proposed functionality
- **Examples** of how it would be used
- **Why this enhancement would be useful**

### 🔧 Code Contributions

1. **Fork the repository**
2. **Create a feature branch** (`git checkout -b feature/AmazingFeature`)
3. **Make your changes**
4. **Commit your changes** (`git commit -m 'Add some AmazingFeature'`)
5. **Push to the branch** (`git push origin feature/AmazingFeature`)
6. **Open a Pull Request**

## Development Setup

### Prerequisites

- Python 3.8+
- Git
- FFmpeg

### Setup Steps

```bash
# Clone your fork
git clone https://github.com/YOUR_USERNAME/OpenAI-Whisper-supported-speech-to-text-app.git
cd OpenAI-Whisper-supported-speech-to-text-app

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On Mac/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Install development dependencies
pip install pytest black flake8 mypy

# Run tests
pytest tests/
```

## Pull Request Process

1. **Update documentation** if you're changing functionality
2. **Add tests** for new features
3. **Ensure all tests pass** before submitting
4. **Update README.md** if needed
5. **Follow the coding standards** below
6. **Write clear commit messages**

### Commit Message Guidelines

- Use present tense ("Add feature" not "Added feature")
- Use imperative mood ("Move cursor to..." not "Moves cursor to...")
- Limit first line to 72 characters
- Reference issues and pull requests after the first line

Examples:
```
Add Gemini API integration for text enhancement

- Implement GeminiEnhancer class
- Add API key configuration
- Update web UI with enhancement toggle
- Add tests for enhancement functionality

Fixes #123
```

## Coding Standards

### Python Style Guide

We follow PEP 8 with some modifications:

- **Line length**: 100 characters (not 79)
- **Indentation**: 4 spaces
- **Imports**: Grouped and sorted
- **Type hints**: Encouraged for public APIs
- **Docstrings**: Required for all public functions and classes

### Code Formatting

Use `black` for automatic formatting:

```bash
black .
```

### Linting

Use `flake8` for linting:

```bash
flake8 --max-line-length=100 --ignore=E203,W503 .
```

### Type Checking

Use `mypy` for type checking:

```bash
mypy whisper_app/
```

## Testing

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=whisper_app tests/

# Run specific test file
pytest tests/test_processor.py

# Run specific test
pytest tests/test_processor.py::test_transcribe_audio
```

### Writing Tests

- Place tests in `tests/` directory
- Name test files as `test_*.py`
- Name test functions as `test_*`
- Use descriptive names
- Include docstrings
- Test edge cases

Example:
```python
def test_transcribe_audio_with_valid_file():
    """Test transcription with a valid audio file."""
    config = WhisperConfig(model_size="tiny")
    processor = WhisperProcessor(config)
    result = processor.transcribe(Path("tests/fixtures/sample.wav"))
    
    assert result.full_text != ""
    assert result.language in ["en", "tr"]
    assert result.duration > 0
```

## Documentation

- Update README.md for user-facing changes
- Update docstrings for code changes
- Add inline comments for complex logic
- Update CHANGELOG.md for notable changes

## Areas for Contribution

We especially welcome contributions in these areas:

- 🎤 **Audio processing improvements**
- 🌍 **Language support enhancements**
- ⚡ **Performance optimizations**
- 🎨 **UI/UX improvements**
- 📚 **Documentation**
- 🧪 **Test coverage**
- 🐛 **Bug fixes**
- 🔧 **Code refactoring**

## Questions?

Feel free to:
- Open an issue for discussion
- Join our GitHub Discussions
- Contact the maintainers

## Recognition

Contributors will be recognized in:
- README.md contributors section
- Release notes
- Project documentation

---

**Thank you for contributing! 🙏**
