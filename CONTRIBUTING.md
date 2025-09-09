# Contributing to CodeSentinel

Thank you for your interest in contributing to CodeSentinel! This document provides guidelines and information for contributors.

## 🚀 Getting Started

### Prerequisites
- Python 3.8 or higher
- Git
- GitHub account

### Setup Development Environment
1. Fork the repository
2. Clone your fork:
   ```bash
   git clone https://github.com/your-username/CodeSentinel.git
   cd CodeSentinel
   ```
3. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
4. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## 📝 How to Contribute

### Reporting Bugs
- Use the bug report template
- Include detailed reproduction steps
- Provide environment information

### Suggesting Features
- Use the feature request template
- Explain the use case and benefits
- Consider implementation complexity

### Code Contributions
1. Create a new branch for your feature:
   ```bash
   git checkout -b feature/your-feature-name
   ```
2. Make your changes
3. Add tests for new functionality
4. Ensure all tests pass:
   ```bash
   python -m pytest tests/
   ```
5. Commit your changes:
   ```bash
   git commit -m "Add feature: description of changes"
   ```
6. Push to your fork:
   ```bash
   git push origin feature/your-feature-name
   ```
7. Create a Pull Request

## 🧪 Testing

### Running Tests
```bash
# Run all tests
python -m pytest tests/

# Run specific test file
python -m pytest tests/test_phase1.py

# Run with coverage
python -m pytest tests/ --cov=src/
```

### Adding Tests
- Add unit tests for new functions
- Include integration tests for new features
- Test both success and error cases

## 📋 Code Style

### Python Style Guide
- Follow PEP 8
- Use type hints where possible
- Add docstrings for all functions and classes
- Maximum line length: 100 characters

### Documentation
- Update README.md for user-facing changes
- Add docstrings for new functions
- Update relevant documentation in `docs/`

## 🔍 Pull Request Guidelines

### Before Submitting
- [ ] Code follows style guidelines
- [ ] Tests pass
- [ ] Documentation is updated
- [ ] Commit messages are descriptive
- [ ] Branch is up to date with main

### PR Description
Include:
- Summary of changes
- Related issue numbers
- Testing performed
- Breaking changes (if any)

## 🏗️ Project Structure

```
CodeSentinel/
├── src/              # Core source code
│   ├── github_analyzer.py
│   ├── llm_analyzer.py
│   └── ...
├── prompts/          # LLM prompts
├── tests/            # Test files
├── docs/             # Documentation
├── examples/         # Example scripts
└── cli.py           # Command-line interface
```

## 🤝 Code of Conduct

### Our Standards
- Be respectful and inclusive
- Welcome newcomers and questions
- Focus on constructive feedback
- Help others learn and grow

### Unacceptable Behavior
- Harassment or discrimination
- Trolling or inflammatory comments
- Publishing private information
- Unprofessional conduct

## 📞 Getting Help

- Create an issue for questions
- Check existing documentation in `docs/`
- Review examples in `examples/`

## 🎯 Development Phases

Understanding the project structure:

### Phase 1: GitHub Integration ✅
- Repository analysis and manifest generation

### Phase 2.5: Multi-LLM Analysis ✅  
- OpenAI and AWS Bedrock integration

### Phase 3: Vulnerability Scanning ✅
- Semgrep and Bandit integration

### Phase 4: Risk Assessment (Planned)
- Weighted risk calculation algorithms

## 🏷️ Issue Labels

- `bug`: Something isn't working
- `enhancement`: New feature or request
- `documentation`: Improvements to docs
- `good first issue`: Good for newcomers
- `help wanted`: Extra attention needed
- `phase-1`, `phase-2`, etc.: Phase-specific issues

Thank you for contributing to CodeSentinel! 🎉
