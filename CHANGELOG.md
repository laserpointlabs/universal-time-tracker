# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.2.0] - 2025-01-27
### Added
- Historical session creation feature with CLI command `tt create`
- New API endpoint `/api/v1/sessions/create` for creating sessions with custom start/end times
- Session summary statistics showing total sessions, active sessions, and total time
- Enhanced analytics dashboard with daily variation box plots
- Support for duration-based session creation (e.g., "2h 30m")
- Improved user ID detection in Docker environments
- `TIME_TRACKER_USER_ID` environment variable for Docker containers

### Enhanced
- Session filtering with comprehensive summary statistics
- Analytics dashboard with box plot overlays showing daily productivity variation
- User ID retrieval logic for better Docker environment support
- Session statistics calculation for both filtered and unfiltered data
- Weekly patterns chart with statistical variation insights

### Fixed
- User ID display showing "unknown" in Docker environments
- Session creation and updates now correctly show user identification
- Improved error handling for session creation with invalid time formats

## [0.1.0] - 2024-06-18
### Added
- Trash can icon and delete functionality for projects and subprojects on the projects page.
- `.gitignore` and `.dockerignore` for Python, Docker, and editor files.
- `pyproject.toml` for unified tool configuration (Black, isort, mypy, pytest, coverage).
- `requirements-dev.txt` for development dependencies.
- `.pre-commit-config.yaml` for code quality hooks.
- `Makefile` for common development and Docker commands.
- `CONTRIBUTING.md` for contributing guidelines.
- `CHANGELOG.md` for tracking changes.

### Removed
- Old `pytest.ini` (moved config to `pyproject.toml`).
- Empty/unused `server/src/app_new.py`.

### Changed
- Cleaned up repository and improved project structure for maintainability. 