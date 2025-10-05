# Contributing to EduDub AI

Thank you for your interest in contributing to EduDub AI! This document provides guidelines and instructions for contributing.

## Code of Conduct

Be respectful, inclusive, and professional. We're all here to build something great together.

## How to Contribute

### Reporting Bugs

1. Check if the bug has already been reported in [Issues](https://github.com/yourusername/EduDubAI/issues)
2. If not, create a new issue with:
   - Clear title and description
   - Steps to reproduce
   - Expected vs actual behavior
   - System information (OS, Python version, etc.)
   - Relevant logs or screenshots

### Suggesting Features

1. Check existing issues and discussions
2. Create a new issue with:
   - Clear description of the feature
   - Use case and benefits
   - Possible implementation approach

### Pull Requests

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Write/update tests
5. Update documentation
6. Commit with clear messages (`git commit -m 'Add amazing feature'`)
7. Push to your fork (`git push origin feature/amazing-feature`)
8. Open a Pull Request

## Development Setup

```bash
# Clone your fork
git clone https://github.com/yourusername/EduDubAI.git
cd EduDubAI

# Set up backend
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install -r requirements-dev.txt  # Development dependencies

# Set up frontend
cd ../frontend
npm install

# Set up pre-commit hooks
pre-commit install
```

## Coding Standards

### Python (Backend)

- Follow PEP 8 style guide
- Use type hints
- Write docstrings for functions and classes
- Keep functions focused and small
- Add tests for new features

Example:
```python
def process_audio(audio_path: str, sample_rate: int = 16000) -> np.ndarray:
    """
    Process audio file and return normalized array.
    
    Args:
        audio_path: Path to audio file
        sample_rate: Target sample rate in Hz
        
    Returns:
        Normalized audio array
        
    Raises:
        FileNotFoundError: If audio file doesn't exist
    """
    # Implementation
    pass
```

### JavaScript (Frontend)

- Use ESLint configuration
- Follow React best practices
- Use functional components and hooks
- Add PropTypes or TypeScript types
- Write clean, readable JSX

### Commit Messages

Use conventional commits:
```
feat: add speaker diarization feature
fix: resolve audio sync issue
docs: update setup guide
test: add validation tests
refactor: improve pipeline performance
```

## Testing

### Backend Tests

```bash
cd backend
pytest tests/ -v
pytest tests/ --cov=app  # With coverage
```

### Frontend Tests

```bash
cd frontend
npm test
npm run test:coverage
```

## Documentation

- Update README.md for user-facing changes
- Update SETUP_GUIDE.md for setup changes
- Add docstrings/comments for code
- Update API documentation

## Project Structure

```
EduDubAI/
├── backend/
│   ├── app/
│   │   ├── main_v2.py          # FastAPI application
│   │   ├── pipeline.py         # Main dubbing pipeline
│   │   ├── whisperx_transcriber.py
│   │   ├── diarization.py
│   │   ├── emotion_detector.py
│   │   ├── nllb_translator.py
│   │   ├── elevenlabs_tts.py
│   │   ├── wav2lip_sync.py
│   │   └── ...
│   ├── tests/
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── pages/
│   │   ├── components/
│   │   └── ...
│   └── package.json
├── README.md
├── SETUP_GUIDE.md
└── docker-compose.yml
```

## Areas for Contribution

### High Priority
- Additional language support
- Performance optimizations
- Better error handling
- Test coverage improvements
- Documentation enhancements

### Medium Priority
- UI/UX improvements
- Additional TTS providers
- Batch processing features
- Real-time progress tracking
- Video quality presets

### Low Priority
- Alternative translation models
- Custom voice training
- Advanced lip-sync options
- Mobile app
- API client libraries

## Getting Help

- GitHub Discussions: For questions and discussions
- GitHub Issues: For bugs and feature requests
- Discord: [Join our community](https://discord.gg/edudub)

## Recognition

Contributors will be acknowledged in:
- README.md contributors section
- Release notes
- Project documentation

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

Thank you for contributing to EduDub AI! 🎉

