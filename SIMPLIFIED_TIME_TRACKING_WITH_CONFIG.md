# Simplified Universal Time Tracking with .timecfg
**Date**: June 23, 2025  
**Approach**: Configuration-based project time tracking with central Docker server

## Core Concept

Instead of complex auto-detection, use a simple `.timecfg` file in each project that:
- Defines project-specific settings
- Points to central Docker time tracking server
- Allows custom project naming and categorization
- Provides per-project time tracking configuration

## Architecture

### Central Time Tracking Server (Docker)
```
time-tracker-server/
├── Dockerfile
├── docker-compose.yml
├── src/
│   ├── server.py          # Flask/FastAPI server
│   ├── tracker.py         # Time tracking logic
│   ├── database.py        # SQLite/PostgreSQL
│   └── api/
│       ├── sessions.py
│       ├── projects.py
│       └── reports.py
├── data/                  # Persistent volume
│   ├── tracker.db
│   └── exports/
└── cli/
    ├── tt                 # Global CLI client
    └── tt.py              # Python CLI implementation
```

### Project Configuration (.timecfg)
```yaml
# .timecfg - Place in any project root
project:
  name: "DADM Demonstrator"           # Custom project name
  id: "dadm-2025"                     # Unique project ID
  type: "development"                 # Project type
  language: "python"                  # Primary language (optional)
  framework: "flask"                  # Framework (optional)

server:
  url: "http://localhost:8080"        # Time tracking server
  api_version: "v1"

tracking:
  categories:                         # Custom categories for this project
    - "development"
    - "research" 
    - "documentation"
    - "meetings"
    - "testing"
    - "deployment"
  
  default_category: "development"
  
  auto_commit: true                   # Auto-link git commits
  break_reminders: true               # Remind about breaks
  
git:
  enabled: true
  auto_detect_branch: true
  link_commits: true

reporting:
  timezone: "America/New_York"
  weekly_summary: true
  export_formats: ["json", "csv"]

# Project-specific aliases (optional)
aliases:
  work: "development"
  code: "development" 
  docs: "documentation"
  meet: "meetings"
```

## Simple CLI Workflow

### Setup (One-time per project)
```bash
# 1. Start central Docker server (once globally)
docker run -d -p 8080:8080 -v ~/time-data:/data time-tracker-server

# 2. In any project directory, create .timecfg
cd ~/projects/my-app
tt init                           # Creates .timecfg template
# Edit .timecfg with project details

# 3. Ready to track time!
tt start "Working on user login"
```

### Daily Usage
```bash
# From any project directory with .timecfg
tt start "Implementing authentication"    # Reads project config automatically
tt break coffee                          # Take a break
tt break                                 # Resume
tt stop                                  # Stop tracking

# Status and reports use project context
tt status                               # Shows current project status
tt report today                         # Today's report for this project
tt report week                          # Weekly report for this project
```

## Implementation

### 1. .timecfg Parser
```python
# cli/config.py
import yaml
import os
from pathlib import Path

class ProjectConfig:
    def __init__(self):
        self.config_file = self._find_config_file()
        self.config = self._load_config()
    
    def _find_config_file(self):
        """Walk up directory tree to find .timecfg"""
        current = Path.cwd()
        
        while current != current.parent:
            config_file = current / ".timecfg"
            if config_file.exists():
                return config_file
            current = current.parent
        
        return None
    
    def _load_config(self):
        """Load and validate project configuration"""
        if not self.config_file:
            raise Exception("No .timecfg found. Run 'tt init' to create one.")
        
        with open(self.config_file, 'r') as f:
            config = yaml.safe_load(f)
        
        # Set defaults
        defaults = {
            'project': {
                'name': Path.cwd().name,
                'type': 'development'
            },
            'server': {
                'url': 'http://localhost:8080',
                'api_version': 'v1'
            },
            'tracking': {
                'categories': ['development', 'research', 'documentation'],
                'default_category': 'development',
                'auto_commit': True
            }
        }
        
        return self._merge_config(defaults, config)
    
    def get_project_name(self):
        return self.config['project']['name']
    
    def get_server_url(self):
        return f"{self.config['server']['url']}/api/{self.config['server']['api_version']}"
    
    def get_categories(self):
        return self.config['tracking']['categories']
```

### 2. CLI Client
```python
# cli/tt.py
import click
import requests
from config import ProjectConfig

@click.group()
@click.pass_context
def cli(ctx):
    """Time Tracker - Project-aware time tracking"""
    try:
        config = ProjectConfig()
        ctx.obj = {
            'config': config,
            'project_name': config.get_project_name(),
            'server_url': config.get_server_url()
        }
    except Exception as e:
        if ctx.invoked_subcommand != 'init':
            click.echo(f"❌ {e}")
            ctx.exit(1)

@cli.command()
@click.option('--name', prompt='Project name', help='Name for this project')
@click.option('--type', default='development', help='Project type')
def init(name, type):
    """Initialize time tracking for this project"""
    config_template = f"""# Time Tracking Configuration
project:
  name: "{name}"
  id: "{name.lower().replace(' ', '-')}"
  type: "{type}"

server:
  url: "http://localhost:8080"
  api_version: "v1"

tracking:
  categories:
    - "development"
    - "research"
    - "documentation"
    - "meetings"
    - "testing"
  default_category: "development"
  auto_commit: true

git:
  enabled: true
  link_commits: true
"""
    
    config_file = Path.cwd() / ".timecfg"
    if config_file.exists():
        if not click.confirm(f"⚠️  .timecfg already exists. Overwrite?"):
            return
    
    with open(config_file, 'w') as f:
        f.write(config_template)
    
    click.echo(f"✅ Created .timecfg for project '{name}'")
    click.echo("💡 Add .timecfg to your .gitignore if you don't want to commit it")

@cli.command()
@click.argument('description')
@click.option('--category', '-c', help='Time category')
@click.pass_context
def start(ctx, description, category):
    """Start tracking time"""
    config = ctx.obj['config']
    category = category or config.config['tracking']['default_category']
    
    payload = {
        'project': ctx.obj['project_name'],
        'description': description,
        'category': category
    }
    
    response = requests.post(f"{ctx.obj['server_url']}/sessions/start", json=payload)
    
    if response.status_code == 200:
        click.echo(f"⏰ Started: {description}")
        click.echo(f"📁 Project: {ctx.obj['project_name']}")
        click.echo(f"🏷️  Category: {category}")
    else:
        click.echo(f"❌ Error: {response.text}")

@cli.command()
@click.pass_context  
def stop(ctx):
    """Stop tracking time"""
    payload = {'project': ctx.obj['project_name']}
    
    response = requests.post(f"{ctx.obj['server_url']}/sessions/stop", json=payload)
    
    if response.status_code == 200:
        data = response.json()
        duration = data.get('duration_minutes', 0)
        click.echo(f"⏹️  Stopped: {data.get('description', 'Unknown')}")
        click.echo(f"⏱️  Duration: {duration // 60}h {duration % 60}m")
    else:
        click.echo(f"❌ Error: {response.text}")

@cli.command()
@click.pass_context
def status(ctx):
    """Show current status"""
    response = requests.get(f"{ctx.obj['server_url']}/sessions/status", 
                           params={'project': ctx.obj['project_name']})
    
    if response.status_code == 200:
        data = response.json()
        click.echo(f"\n📊 Status for {ctx.obj['project_name']}")
        click.echo("=" * 40)
        
        if data.get('active_session'):
            session = data['active_session']
            click.echo(f"🟢 Active: {session['description']}")
            click.echo(f"   Started: {session['start_time']}")
            click.echo(f"   Category: {session['category']}")
        else:
            click.echo("⭕ No active session")

if __name__ == '__main__':
    cli()
```

## Benefits of This Approach

### ✅ **Simplicity**
- Just add `.timecfg` to any project
- No complex auto-detection logic
- Predictable, explicit configuration

### ✅ **Flexibility** 
- Custom project names and categories
- Per-project time tracking preferences
- Override global settings per project

### ✅ **Central Management**
- One Docker server for all projects
- Cross-project reporting and analytics
- Centralized data storage

### ✅ **Developer Friendly**
- Familiar config file pattern (like `.gitconfig`, `.eslintrc`)
- Version controllable (or gitignored)
- Easy to share team settings

## Example Usage

### Project Setup
```bash
# New project
cd ~/projects/new-react-app
tt init --name "E-commerce Frontend" --type "frontend"

# Existing project
cd ~/projects/existing-api
tt init
# Edit .timecfg as needed
```

### Daily Workflow
```bash
cd ~/projects/new-react-app
tt start "Building product catalog"     # Uses "E-commerce Frontend" project
tt break
tt stop

cd ~/projects/existing-api  
tt start "API optimization"             # Switches to different project automatically
```

This approach is much cleaner and more practical! Would you like me to implement this simplified version?
