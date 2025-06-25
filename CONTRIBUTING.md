# Contributing to Universal Time Tracker

Thank you for your interest in contributing to Universal Time Tracker! This document provides guidelines and information for contributors.

## Development Setup

### Prerequisites
- Python 3.8 or higher
- Docker and Docker Compose
- Git

### Quick Start
1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd universal-time-tracker
   ```

2. Setup development environment:
   ```bash
   make setup
   ```

3. Start the application:
   ```bash
   make docker-up
   ```

4. Access the application at http://localhost:9000

## Development Workflow

### Code Style
We use several tools to maintain code quality:

- **Black**: Code formatting
- **isort**: Import sorting
- **flake8**: Linting
- **mypy**: Type checking
- **bandit**: Security analysis

Run all checks:
```bash
make check
```

### Testing
Run tests:
```bash
make test
```

Run tests with coverage:
```bash
make test-cov
```

### Pre-commit Hooks
We use pre-commit hooks to ensure code quality. They will run automatically on commit, but you can also run them manually:
```bash
pre-commit run --all-files
```

## Project Structure

```
universal-time-tracker/
├── server/                 # Flask application
│   ├── src/               # Source code
│   │   ├── app.py         # Main Flask app
│   │   ├── db_browser.py  # Database browser routes
│   │   ├── models.py      # Data models
│   │   ├── static/        # Static files (CSS, JS, images)
│   │   └── templates/     # HTML templates
│   ├── requirements.txt   # Production dependencies
│   ├── requirements-dev.txt # Development dependencies
│   └── Dockerfile         # Docker configuration
├── cli/                   # Command-line interface
├── data/                  # Database files (gitignored)
├── docs/                  # Documentation
└── scripts/               # Utility scripts
```

## Database Schema

The application uses SQLite with the following main tables:
- `projects`: Project information
- `sessions`: Time tracking sessions
- `breaks`: Break periods within sessions

## API Endpoints

### Projects
- `GET /api/v1/projects` - List all projects
- `POST /api/v1/projects` - Create a new project

### Database Browser
- `GET /db/projects` - View projects page
- `GET /db/projects/<id>` - View project details
- `GET /db/projects/<id>/edit` - Edit project
- `POST /db/projects/<id>/delete` - Delete project

## Making Changes

1. Create a feature branch:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. Make your changes and ensure they pass all checks:
   ```bash
   make check
   ```

3. Commit your changes with a descriptive message:
   ```bash
   git commit -m "Add feature: description of changes"
   ```

4. Push your branch and create a pull request.

## Commit Message Guidelines

Use conventional commit format:
- `feat:` New features
- `fix:` Bug fixes
- `docs:` Documentation changes
- `style:` Code style changes (formatting, etc.)
- `refactor:` Code refactoring
- `test:` Adding or updating tests
- `chore:` Maintenance tasks

Example:
```
feat: add project deletion functionality

- Add delete button to projects page
- Implement delete project API endpoint
- Add confirmation dialog for deletion
```

## Testing Guidelines

- Write tests for new features
- Ensure existing tests pass
- Aim for good test coverage
- Use descriptive test names
- Test both success and error cases

## Documentation

- Update documentation for new features
- Include examples where appropriate
- Keep README.md up to date
- Document any configuration changes

## Questions or Issues?

If you have questions or encounter issues:
1. Check existing issues and documentation
2. Create a new issue with detailed information
3. Join our community discussions

Thank you for contributing to Universal Time Tracker! 