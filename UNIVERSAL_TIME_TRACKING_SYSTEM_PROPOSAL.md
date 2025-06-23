# Universal Time Tracking System (UTTS)
**Project**: Standalone Docker-based time tracking for all development projects  
**Date**: June 23, 2025  
**Purpose**: Universal time tracking system that works across any development environment

## Project Overview

A containerized time tracking system that can be deployed once and used across all development projects. It automatically detects the current project context and provides intelligent time logging with advanced analytics.

## Key Features

### 🐳 **Docker-First Architecture**
- Single container deployment
- Volume mounts for persistent data
- Cross-platform compatibility (Linux, macOS, Windows)
- No local dependencies (except Docker)

### 🎯 **Automatic Project Detection**
- Git repository auto-detection
- Project name inference from directory/repo
- Intelligent project context switching
- Support for multiple simultaneous projects

### 📊 **Advanced Analytics**
- Cross-project time analysis
- Technology stack detection
- Productivity insights
- Exportable reports (JSON, CSV, Markdown)

### 🚀 **Universal CLI Interface**
- Single global command: `tt` (time tracker)
- Works from any directory
- Automatic project context
- Integration with any development workflow

## Architecture Design

### Container Structure
```
universal-time-tracker/
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── src/
│   ├── app.py                 # Main Flask API
│   ├── cli.py                 # CLI interface
│   ├── detector.py            # Project detection
│   ├── tracker.py             # Time tracking logic
│   ├── analytics.py           # Reporting engine
│   └── models/
│       ├── session.py
│       ├── project.py
│       └── database.py
├── data/                      # Volume mount for persistence
│   ├── projects.db           # SQLite database
│   ├── logs/                 # JSON logs
│   └── exports/              # Generated reports
├── scripts/
│   ├── install.sh            # Global installation
│   ├── tt                    # Global CLI wrapper
│   └── hooks/                # Git hooks
└── config/
    ├── settings.yaml
    └── project_rules.yaml
```

### Data Model
```sql
-- Projects table
CREATE TABLE projects (
    id INTEGER PRIMARY KEY,
    name TEXT UNIQUE,
    path TEXT,
    git_remote TEXT,
    language TEXT,
    framework TEXT,
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);

-- Sessions table
CREATE TABLE sessions (
    id INTEGER PRIMARY KEY,
    project_id INTEGER,
    start_time TIMESTAMP,
    end_time TIMESTAMP,
    duration_minutes INTEGER,
    category TEXT,
    description TEXT,
    git_commit TEXT,
    created_at TIMESTAMP,
    FOREIGN KEY (project_id) REFERENCES projects (id)
);

-- Breaks table
CREATE TABLE breaks (
    id INTEGER PRIMARY KEY,
    session_id INTEGER,
    start_time TIMESTAMP,
    end_time TIMESTAMP,
    duration_minutes INTEGER,
    break_type TEXT,
    FOREIGN KEY (session_id) REFERENCES sessions (id)
);
```

## Installation & Setup

### 1. Repository Structure
```
universal-time-tracker/
├── README.md
├── LICENSE
├── CHANGELOG.md
├── .gitignore
├── .dockerignore
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── setup.py
├── pyproject.toml
└── [rest of structure above]
```

### 2. Global Installation Script
```bash
#!/bin/bash
# install.sh - Global installation for Universal Time Tracker

echo "🕐 Installing Universal Time Tracker..."

# Check for Docker
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is required but not installed"
    exit 1
fi

# Clone repository
INSTALL_DIR="$HOME/.universal-time-tracker"
if [ -d "$INSTALL_DIR" ]; then
    echo "📁 Updating existing installation..."
    cd "$INSTALL_DIR"
    git pull
else
    echo "📥 Downloading Universal Time Tracker..."
    git clone https://github.com/your-org/universal-time-tracker.git "$INSTALL_DIR"
    cd "$INSTALL_DIR"
fi

# Build container
echo "🔨 Building Docker container..."
docker-compose build

# Create global CLI wrapper
sudo tee /usr/local/bin/tt > /dev/null <<'EOF'
#!/bin/bash
# Universal Time Tracker CLI wrapper

UTTS_DIR="$HOME/.universal-time-tracker"
CURRENT_DIR="$(pwd)"

# Detect if we're in a git repository
GIT_ROOT=""
if git rev-parse --git-dir > /dev/null 2>&1; then
    GIT_ROOT="$(git rev-parse --show-toplevel)"
fi

# Run the container with current directory context
docker-compose -f "$UTTS_DIR/docker-compose.yml" run --rm \
    -v "$CURRENT_DIR:/workspace" \
    -v "$GIT_ROOT:/git_root" \
    -e "CURRENT_DIR=$CURRENT_DIR" \
    -e "GIT_ROOT=$GIT_ROOT" \
    time-tracker "$@"
EOF

chmod +x /usr/local/bin/tt

echo "✅ Installation complete!"
echo "Usage: tt start 'Working on new feature'"
echo "       tt status"
echo "       tt stop"
```

### 3. Docker Configuration
```dockerfile
# Dockerfile
FROM python:3.11-alpine

WORKDIR /app

# Install system dependencies
RUN apk add --no-cache git sqlite

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY src/ ./src/
COPY scripts/ ./scripts/
COPY config/ ./config/

# Create data directory
RUN mkdir -p /app/data

# Set permissions
RUN chmod +x /app/scripts/*

# Default command
ENTRYPOINT ["python", "/app/src/cli.py"]
```

```yaml
# docker-compose.yml
version: '3.8'

services:
  time-tracker:
    build: .
    container_name: universal-time-tracker
    volumes:
      # Persistent data
      - ./data:/app/data
      # Current workspace (mounted at runtime)
      - /tmp:/workspace:ro
      # Git repository root (mounted at runtime)
      - /tmp:/git_root:ro
    environment:
      - TZ=America/New_York
      - PYTHONPATH=/app
    working_dir: /workspace
    network_mode: none  # No network needed for time tracking
```

## Core Implementation

### 1. Project Detector
```python
# src/detector.py
import os
import git
import json
from pathlib import Path
from typing import Optional, Dict

class ProjectDetector:
    def __init__(self):
        self.workspace_dir = os.environ.get('CURRENT_DIR', '/workspace')
        self.git_root = os.environ.get('GIT_ROOT', '')
    
    def detect_project(self) -> Dict[str, str]:
        """Automatically detect current project context"""
        project_info = {
            'name': self._get_project_name(),
            'path': self.workspace_dir,
            'git_remote': self._get_git_remote(),
            'language': self._detect_language(),
            'framework': self._detect_framework(),
            'type': self._detect_project_type()
        }
        
        return project_info
    
    def _get_project_name(self) -> str:
        """Get project name from git repo or directory"""
        if self.git_root:
            try:
                repo = git.Repo(self.git_root)
                if repo.remotes:
                    remote_url = repo.remotes.origin.url
                    # Extract repo name from URL
                    return Path(remote_url).stem.replace('.git', '')
            except:
                pass
        
        # Fallback to directory name
        return Path(self.workspace_dir).name
    
    def _get_git_remote(self) -> Optional[str]:
        """Get git remote URL if available"""
        if self.git_root:
            try:
                repo = git.Repo(self.git_root)
                if repo.remotes:
                    return repo.remotes.origin.url
            except:
                pass
        return None
    
    def _detect_language(self) -> str:
        """Detect primary programming language"""
        language_indicators = {
            'python': ['*.py', 'requirements.txt', 'pyproject.toml', 'setup.py'],
            'javascript': ['*.js', 'package.json', 'package-lock.json'],
            'typescript': ['*.ts', '*.tsx', 'tsconfig.json'],
            'java': ['*.java', 'pom.xml', 'build.gradle'],
            'go': ['*.go', 'go.mod', 'go.sum'],
            'rust': ['*.rs', 'Cargo.toml', 'Cargo.lock'],
            'cpp': ['*.cpp', '*.hpp', 'CMakeLists.txt'],
            'csharp': ['*.cs', '*.csproj', '*.sln']
        }
        
        for language, patterns in language_indicators.items():
            if self._has_files(patterns):
                return language
        
        return 'unknown'
    
    def _detect_framework(self) -> str:
        """Detect framework/platform"""
        framework_indicators = {
            'react': ['package.json', 'src/App.js', 'src/App.tsx'],
            'vue': ['package.json', 'src/App.vue'],
            'angular': ['package.json', 'angular.json'],
            'django': ['manage.py', 'settings.py'],
            'flask': ['app.py', 'requirements.txt'],
            'spring': ['pom.xml', 'application.properties'],
            'docker': ['Dockerfile', 'docker-compose.yml']
        }
        
        for framework, patterns in framework_indicators.items():
            if self._has_files(patterns):
                return framework
        
        return 'unknown'
    
    def _has_files(self, patterns: List[str]) -> bool:
        """Check if any files matching patterns exist"""
        for pattern in patterns:
            if list(Path(self.workspace_dir).glob(pattern)):
                return True
        return False
```

### 2. Universal CLI Interface
```python
# src/cli.py
import click
import os
from datetime import datetime
from detector import ProjectDetector
from tracker import TimeTracker
from analytics import AnalyticsEngine

@click.group()
@click.pass_context
def cli(ctx):
    """Universal Time Tracker - Track time across all your projects"""
    ctx.ensure_object(dict)
    
    # Auto-detect project
    detector = ProjectDetector()
    project_info = detector.detect_project()
    
    # Initialize tracker
    tracker = TimeTracker(project_info)
    
    ctx.obj['tracker'] = tracker
    ctx.obj['project'] = project_info

@cli.command()
@click.argument('description')
@click.option('--category', '-c', default='development', 
              help='Category: development, research, meeting, documentation, testing')
@click.pass_context
def start(ctx, description, category):
    """Start a new time tracking session"""
    tracker = ctx.obj['tracker']
    project = ctx.obj['project']
    
    session_id = tracker.start_session(description, category)
    
    click.echo(f"⏰ Started tracking: {description}")
    click.echo(f"📁 Project: {project['name']} [{project['language']}]")
    click.echo(f"🏷️  Category: {category}")
    click.echo(f"🆔 Session ID: {session_id}")

@cli.command()
@click.pass_context
def stop(ctx):
    """Stop the current time tracking session"""
    tracker = ctx.obj['tracker']
    
    session = tracker.stop_session()
    if session:
        duration = session['duration_minutes']
        click.echo(f"⏹️  Stopped tracking: {session['description']}")
        click.echo(f"⏱️  Duration: {duration // 60}h {duration % 60}m")
    else:
        click.echo("❌ No active session to stop")

@cli.command()
@click.option('--break-type', '-t', default='break',
              help='Break type: break, coffee, lunch, meeting')
@click.pass_context
def break_cmd(ctx, break_type):
    """Start or end a break"""
    tracker = ctx.obj['tracker']
    
    result = tracker.toggle_break(break_type)
    
    if result['action'] == 'started':
        click.echo(f"☕ Break started: {break_type}")
    else:
        duration = result['duration_minutes']
        click.echo(f"▶️  Resumed from {break_type} ({duration} minutes)")

@cli.command()
@click.pass_context
def status(ctx):
    """Show current tracking status"""
    tracker = ctx.obj['tracker']
    project = ctx.obj['project']
    
    status = tracker.get_status()
    
    click.echo(f"\n📊 Status for {project['name']}")
    click.echo("=" * 40)
    
    if status['active_session']:
        session = status['active_session']
        click.echo(f"🟢 Active: {session['description']}")
        click.echo(f"   Started: {session['start_time']}")
        click.echo(f"   Category: {session['category']}")
        
        if status['active_break']:
            break_info = status['active_break']
            click.echo(f"   ☕ On {break_info['type']} since {break_info['start_time']}")
    else:
        click.echo("⭕ No active session")
    
    # Daily summary
    daily = status['daily_summary']
    if daily['total_hours'] > 0:
        click.echo(f"\n📈 Today's total: {daily['total_hours']:.1f} hours")

@cli.command()
@click.option('--period', '-p', default='today',
              help='Period: today, week, month, all')
@click.option('--project', '-pr', help='Filter by project')
@click.option('--format', '-f', default='table',
              help='Output format: table, json, csv')
@click.pass_context
def report(ctx, period, project, format):
    """Generate time tracking reports"""
    analytics = AnalyticsEngine()
    
    report_data = analytics.generate_report(
        period=period,
        project_filter=project,
        format=format
    )
    
    if format == 'table':
        analytics.display_table_report(report_data)
    elif format == 'json':
        click.echo(json.dumps(report_data, indent=2))
    elif format == 'csv':
        analytics.export_csv(report_data)

@cli.command()
@click.pass_context
def commit(ctx):
    """Link current git commit to active session"""
    tracker = ctx.obj['tracker']
    
    # Get current commit info
    try:
        import git
        repo = git.Repo(os.environ.get('GIT_ROOT', '.'))
        commit_hash = repo.head.commit.hexsha
        commit_message = repo.head.commit.message.strip()
        
        tracker.add_commit(commit_hash, commit_message)
        click.echo(f"📝 Linked commit {commit_hash[:8]}: {commit_message}")
    except Exception as e:
        click.echo(f"❌ Error linking commit: {e}")

if __name__ == '__main__':
    cli()
```

## Usage Examples

### Daily Workflow
```bash
# From any project directory
cd ~/projects/my-app

# Start tracking (auto-detects project)
tt start "Implementing user authentication"

# Take a break
tt break coffee

# Resume (automatic)
tt break

# Check status
tt status

# Stop tracking
tt stop

# View today's report
tt report --period today

# Switch to another project
cd ~/projects/another-app
tt start "Bug fixing"  # Automatically switches project context
```

### Advanced Features
```bash
# Cross-project reports
tt report --period week --format json > weekly_report.json

# Project-specific analysis
tt report --project "my-app" --period month

# Export to CSV
tt report --period all --format csv

# Git integration
git commit -m "Add authentication module"
tt commit  # Links commit to active session
```

## Deployment Benefits

### 🌍 **Universal Access**
- Works from any directory on any machine
- Consistent interface across all projects
- No per-project setup required

### 🔄 **Seamless Context Switching**
- Automatic project detection
- Maintains separate time logs per project
- Cross-project analytics and reporting

### 📦 **Zero Dependencies**
- Only requires Docker
- No Python/Node/etc. installation needed
- Works on any OS with Docker support

### 🎯 **Intelligent Detection**
- Auto-detects programming language
- Identifies frameworks and tools
- Captures git context automatically

Would you like me to create the complete project structure and implementation files for this Universal Time Tracking System?
