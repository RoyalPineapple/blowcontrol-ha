# Contributing to BlowControl Home Assistant Integration

Thank you for your interest in contributing to the BlowControl Home Assistant Integration! This document provides guidelines and information for contributors.

## 🤝 How to Contribute

### Types of Contributions

We welcome various types of contributions:

- **🐛 Bug Reports**: Report issues you encounter
- **💡 Feature Requests**: Suggest new features or improvements
- **📝 Documentation**: Improve or add documentation
- **🔧 Code Contributions**: Submit code improvements or new features
- **🧪 Testing**: Test the integration and report findings
- **🌐 Translations**: Add or improve translations

### Before You Start

1. **Check Existing Issues**: Search existing issues to avoid duplicates
2. **Read Documentation**: Familiarize yourself with the project structure
3. **Set Up Development Environment**: Follow the development setup guide

## 🛠️ Development Setup

### Prerequisites

- Python 3.10 or higher
- Git
- Home Assistant development environment
- Code editor (VS Code recommended)

### Local Development Environment

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/RoyalPineapple/blowcontrol-ha.git
   cd blowcontrol-ha
   ```

2. **Create Virtual Environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install Development Dependencies**:
   ```bash
   pip install -r requirements-dev.txt
   ```

4. **Install Pre-commit Hooks**:
   ```bash
   pre-commit install
   ```

### Testing Setup

1. **Install Test Dependencies**:
   ```bash
   pip install pytest pytest-asyncio pytest-cov
   ```

2. **Run Tests**:
   ```bash
   pytest tests/ -v
   ```

3. **Run with Coverage**:
   ```bash
   pytest tests/ --cov=custom_components/blowcontrol --cov-report=html
   ```

## 📝 Code Style and Standards

### Python Style Guide

We follow [PEP 8](https://www.python.org/dev/peps/pep-0008/) with some modifications:

- **Line Length**: 88 characters (Black default)
- **Type Hints**: Required for all functions and methods
- **Docstrings**: Required for all public functions and classes
- **Imports**: Use absolute imports, sorted with isort

### Code Formatting

We use several tools to maintain code quality:

- **Black**: Code formatting
- **isort**: Import sorting
- **Flake8**: Linting
- **mypy**: Type checking

Run formatting:
```bash
black custom_components/blowcontrol/
isort custom_components/blowcontrol/
```

### Type Hints

All functions and methods must include type hints:

```python
from typing import Any, Dict, Optional

async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the BlowControl fan platform."""
    pass
```

### Docstrings

Use Google-style docstrings:

```python
def update_from_coordinator(self, data: Dict[str, Any]) -> None:
    """Update the sensor state from coordinator data.
    
    Args:
        data: Dictionary containing coordinator data
        
    Returns:
        None
    """
    pass
```

## 🧪 Testing

### Writing Tests

1. **Test Structure**: Place tests in `tests/` directory
2. **Test Naming**: Use descriptive test names
3. **Test Coverage**: Aim for high test coverage
4. **Async Tests**: Use `pytest-asyncio` for async functions

### Example Test

```python
import pytest
from unittest.mock import AsyncMock, patch

from custom_components.blowcontrol.fan import BlowControlFan

@pytest.mark.asyncio
async def test_fan_turn_on():
    """Test turning on the fan."""
    coordinator = AsyncMock()
    fan = BlowControlFan(coordinator, "Test Fan", "test_entry_id")
    
    await fan.async_turn_on()
    
    assert fan.is_on is True
    coordinator.async_set_fan_power.assert_called_once_with(True)
```

### Running Tests

```bash
# Run all tests
pytest tests/

# Run specific test file
pytest tests/test_fan.py

# Run with verbose output
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=custom_components/blowcontrol
```

## 📚 Documentation

### Documentation Standards

- **README.md**: Main project documentation
- **Code Comments**: Inline comments for complex logic
- **Docstrings**: Function and class documentation
- **Type Hints**: Self-documenting code

### Updating Documentation

1. **README.md**: Update for user-facing changes
2. **Code Comments**: Add comments for complex logic
3. **Docstrings**: Update when changing function signatures
4. **Translations**: Update translation files for UI changes

## 🔄 Pull Request Process

### Creating a Pull Request

1. **Fork the Repository**:
   - Click "Fork" on GitHub
   - Clone your fork locally

2. **Create Feature Branch**:
   ```bash
   git checkout -b feature/your-feature-name
   ```

3. **Make Changes**:
   - Implement your changes
   - Add tests for new functionality
   - Update documentation

4. **Test Your Changes**:
   ```bash
   # Run linting
   flake8 custom_components/blowcontrol/
   
   # Run type checking
   mypy custom_components/blowcontrol/
   
   # Run tests
   pytest tests/
   ```

5. **Commit Changes**:
   ```bash
   git add .
   git commit -m "feat: add new feature description"
   ```

6. **Push to Your Fork**:
   ```bash
   git push origin feature/your-feature-name
   ```

7. **Create Pull Request**:
   - Go to your fork on GitHub
   - Click "New Pull Request"
   - Fill out the PR template

### Pull Request Guidelines

- **Title**: Use conventional commit format
- **Description**: Detailed description of changes
- **Tests**: Include tests for new functionality
- **Documentation**: Update docs if needed
- **Screenshots**: Include for UI changes

### Commit Message Format

Use [Conventional Commits](https://www.conventionalcommits.org/):

```
type(scope): description

[optional body]

[optional footer]
```

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes
- `refactor`: Code refactoring
- `test`: Test changes
- `chore`: Maintenance tasks

## 🐛 Bug Reports

### Before Reporting

1. **Search Existing Issues**: Check if the bug is already reported
2. **Reproduce the Issue**: Ensure you can consistently reproduce it
3. **Check Documentation**: Verify it's not a configuration issue

### Bug Report Template

```markdown
## Bug Description
Brief description of the issue.

## Steps to Reproduce
1. Step 1
2. Step 2
3. Step 3

## Expected Behavior
What you expected to happen.

## Actual Behavior
What actually happened.

## Environment
- Home Assistant Version: [version]
- Integration Version: [version]
- Python Version: [version]
- Operating System: [OS]

## Logs
```
[Paste relevant logs here]
```

## Additional Information
Any additional context or information.
```

## 💡 Feature Requests

### Feature Request Guidelines

1. **Check Existing Issues**: Search for similar requests
2. **Provide Use Case**: Explain why the feature is needed
3. **Consider Implementation**: Think about how it could be implemented

### Feature Request Template

```markdown
## Feature Description
Brief description of the requested feature.

## Use Case
Why is this feature needed? What problem does it solve?

## Proposed Implementation
How could this feature be implemented? (Optional)

## Additional Information
Any additional context or information.
```

## 🌐 Translations

### Adding Translations

1. **Create Translation File**:
   - Add new language file in `custom_components/blowcontrol/translations/`
   - Follow the format of `en.json`

2. **Translation Keys**:
   - Use descriptive keys
   - Keep translations concise
   - Maintain consistency across languages

### Translation Example

```json
{
  "config": {
    "step": {
      "user": {
        "title": "BlowControl Configuration",
        "description": "Enter the details for your BlowControl device",
        "data": {
          "host": "Host/IP Address",
          "name": "Device Name"
        }
      }
    }
  }
}
```

## 📋 Code Review Process

### Review Guidelines

- **Be Constructive**: Provide helpful feedback
- **Be Specific**: Point out specific issues
- **Be Respectful**: Maintain a positive tone
- **Be Thorough**: Check for security and performance issues

### Review Checklist

- [ ] Code follows style guidelines
- [ ] Type hints are included
- [ ] Docstrings are present
- [ ] Tests are included
- [ ] Documentation is updated
- [ ] No security issues
- [ ] Performance is acceptable

## 🚀 Release Process

### Version Bumping

We use [Semantic Versioning](https://semver.org/):

- **Major**: Breaking changes
- **Minor**: New features (backward compatible)
- **Patch**: Bug fixes (backward compatible)

### Release Steps

1. **Update Version**:
   - Update version in `manifest.json`
   - Update version in `README.md`

2. **Update Changelog**:
   - Add new version entry
   - List all changes

3. **Create Release**:
   - Create GitHub release
   - Tag the release
   - Write release notes

## 📞 Getting Help

### Communication Channels

- **GitHub Issues**: For bug reports and feature requests
- **GitHub Discussions**: For questions and general discussion
- **Pull Requests**: For code reviews and discussions

### Asking for Help

When asking for help:

1. **Be Specific**: Describe your issue clearly
2. **Provide Context**: Include relevant information
3. **Show Effort**: Demonstrate what you've tried
4. **Be Patient**: Allow time for responses

## 🙏 Recognition

### Contributors

All contributors will be recognized in:

- **README.md**: Contributors section
- **GitHub**: Contributors page
- **Release Notes**: For significant contributions

### Types of Recognition

- **Code Contributors**: Listed in contributors
- **Documentation**: Acknowledged in docs
- **Testing**: Recognized for bug reports
- **Community**: Appreciated for support

## 📄 License

By contributing to this project, you agree that your contributions will be licensed under the "Seems to Work" License (MIT-compatible).

---

Thank you for contributing to the BlowControl Home Assistant Integration! 🎉 