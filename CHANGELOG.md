# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.2.0] - 2025-06-25
### Added
- **Web Interface**: Modern Bootstrap-based web dashboard for project management
- **Swagger API Documentation**: Interactive API documentation at `/docs/` endpoint  
- **Project Management UI**: Full CRUD operations for projects via web interface
- **Project Dashboards**: Individual project pages with analytics and charts
- **Real-time Session Tracking**: Live session monitoring with start/stop functionality
- **Configuration Management**: `.timecfg` file generation and download from web UI
- **Enhanced API**: Flask-RESTX integration with proper API models and namespaces
- **Visual Analytics**: Chart.js integration for daily activity and category breakdowns
- Historical session creation feature with CLI command `tt create`
- New API endpoint `/api/v1/sessions/create` for creating sessions with custom start/end times
- Session summary statistics showing total sessions, active sessions, and total time
- Enhanced analytics dashboard with daily variation box plots
- Support for duration-based session creation (e.g., "2h 30m")
- Improved user ID detection in Docker environments
- `TIME_TRACKER_USER_ID` environment variable for Docker containers

### Enhanced
- **CLI Virtual Environment Support**: Fixed CLI script to work properly in virtual environments
- **Docker Configuration**: Enhanced server setup to support web assets and templates
- **API Structure**: Organized endpoints into logical namespaces (projects, sessions, analytics, config)
- **Database Models**: Improved model relationships and data serialization
- **Error Handling**: Better error responses and validation across all endpoints
- Session filtering with comprehensive summary statistics
- Analytics dashboard with box plot overlays showing daily productivity variation
- User ID retrieval logic for better Docker environment support
- Session statistics calculation for both filtered and unfiltered data
- Weekly patterns chart with statistical variation insights

### Fixed
- **CLI Virtual Environment Issues**: Fixed `--user` flag issue when running in virtual environments
- **Database Path Resolution**: Improved path handling for local development
- **Template Serving**: Fixed Flask application template and static file serving
- **Session Calculations**: Improved duration calculations and time zone handling
- User ID display showing "unknown" in Docker environments
- Session creation and updates now correctly show user identification
- Improved error handling for session creation with invalid time formats

### Technical
- Added Flask-RESTX for automatic Swagger documentation generation
- Integrated Bootstrap 5 and Chart.js for modern UI components
- Created responsive HTML templates for dashboard and project views
- Enhanced Docker Compose configuration for development workflow
- Improved API endpoint organization and documentation

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