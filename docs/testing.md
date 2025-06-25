# Testing Guide

This document explains how to run tests for the Universal Time Tracker project.

## Running Tests Locally

### Prerequisites

Install the required testing dependencies:

```bash
pip install -r server/requirements.txt
pip install click
```

### Running Server Tests

```bash
cd server/src
pytest -v
```

### Running CLI Tests

```bash
cd cli
pytest -v
```

### Running All Tests

From the project root:

```bash
pytest -v
```

## Test Coverage

The tests include coverage reporting. To generate a coverage report:

```bash
cd server/src
pytest --cov=. --cov-report=html
```

This will create an HTML coverage report in `htmlcov/index.html`.

## Continuous Integration

GitHub Actions automatically runs tests on every push and pull request. The CI pipeline includes:

1. **Server Tests**: Tests the Flask API endpoints and functionality
2. **CLI Tests**: Tests the command-line interface
3. **Linting**: Code style checks with flake8, black, and isort
4. **Security**: Security scanning with bandit and safety

## Test Structure

### Server Tests (`server/src/test_app.py`)

- **Health Check**: Tests the `/health` endpoint
- **Page Loading**: Tests that all web pages load correctly
- **API Endpoints**: Tests all REST API endpoints
- **Error Handling**: Tests error responses for invalid requests
- **Database Operations**: Tests database interactions

### CLI Tests (`cli/test_cli.py`)

- **Command Help**: Tests that all CLI commands show help
- **Command Structure**: Tests command argument parsing
- **Configuration**: Tests project initialization and configuration

## Adding New Tests

### Server Tests

Add new test functions to `server/src/test_app.py`:

```python
def test_new_feature(client):
    """Test description"""
    response = client.get('/api/v1/new-endpoint')
    assert response.status_code == 200
    data = response.get_json()
    assert 'expected_field' in data
```

### CLI Tests

Add new test functions to `cli/test_cli.py`:

```python
def test_new_cli_command(runner):
    """Test description"""
    result = runner.invoke(cli, ['new-command'])
    assert result.exit_code == 0
    assert 'expected output' in result.output
```

## Test Fixtures

The tests use several fixtures:

- **`client`**: Flask test client with temporary database
- **`runner`**: Click test runner for CLI commands
- **`temp_project`**: Temporary project directory with configuration

## Troubleshooting

### Common Issues

1. **Import Errors**: Make sure all dependencies are installed
2. **Database Errors**: Tests use temporary databases that are cleaned up automatically
3. **Network Errors**: Server tests don't require a running server

### Running Specific Tests

```bash
# Run only server tests
pytest server/src/ -v

# Run only CLI tests
pytest cli/ -v

# Run tests matching a pattern
pytest -k "health" -v

# Run tests with specific markers
pytest -m "unit" -v
```

## Coverage Goals

- **Server Code**: Aim for >80% coverage
- **CLI Code**: Aim for >70% coverage
- **Critical Paths**: 100% coverage for core functionality

## Continuous Integration Status

Check the GitHub Actions tab to see the status of:
- Test results
- Coverage reports
- Linting results
- Security scan results 