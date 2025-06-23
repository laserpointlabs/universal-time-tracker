#!/usr/bin/env python3
"""
Universal Time Tracker CLI
Command line client for time tracking with .timecfg support
"""

import click
import requests
import yaml
import os
import subprocess
import sys
from pathlib import Path
from datetime import datetime

class ProjectConfig:
    """Handle .timecfg file parsing and project configuration"""
    
    def __init__(self):
        self.config_file = self._find_config_file()
        self.config = self._load_config() if self.config_file else None
    
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
            return None
            
        with open(self.config_file, 'r') as f:
            config = yaml.safe_load(f)
        
        # Set defaults
        defaults = {
            'project': {
                'name': Path.cwd().name,
                'type': 'development'
            },
            'server': {
                'url': 'http://localhost:9000',
                'api_version': 'v1'
            },
            'tracking': {
                'categories': ['development', 'research', 'documentation', 'meetings', 'testing'],
                'default_category': 'development',
                'auto_commit': True
            },
            'git': {
                'enabled': True,
                'link_commits': True
            }
        }
        
        return self._merge_config(defaults, config)
    
    def _merge_config(self, defaults, config):
        """Deep merge configuration with defaults"""
        for key, value in defaults.items():
            if key not in config:
                config[key] = value
            elif isinstance(value, dict) and isinstance(config[key], dict):
                config[key] = self._merge_config(value, config[key])
        return config
    
    def get_project_name(self):
        if not self.config:
            return "unknown-project"
        return self.config['project']['name']
    
    def get_server_url(self):
        if not self.config:
            return "http://localhost:9000/api/v1"
        return f"{self.config['server']['url']}/api/{self.config['server']['api_version']}"
    
    def get_categories(self):
        if not self.config:
            return ['development', 'research', 'documentation']
        return self.config['tracking']['categories']
    
    def get_default_category(self):
        if not self.config:
            return 'development'
        return self.config['tracking']['default_category']
    
    def get_aliases(self):
        if not self.config:
            return {}
        return self.config.get('aliases', {})

def make_request(method, url, **kwargs):
    """Make HTTP request with error handling"""
    try:
        response = requests.request(method, url, timeout=10, **kwargs)
        return response
    except requests.exceptions.ConnectionError:
        click.echo("❌ Cannot connect to time tracker server. Is it running?")
        click.echo("💡 Start with: docker-compose up -d")
        sys.exit(1)
    except requests.exceptions.Timeout:
        click.echo("❌ Request timed out")
        sys.exit(1)
    except Exception as e:
        click.echo(f"❌ Request failed: {e}")
        sys.exit(1)

@click.group()
@click.pass_context
def cli(ctx):
    """Universal Time Tracker - Track time across all your projects"""
    ctx.ensure_object(dict)
    
    # Skip config loading for init command
    if ctx.invoked_subcommand == 'init':
        return
    
    # Load project configuration
    try:
        config = ProjectConfig()
        if not config.config:
            click.echo("❌ No .timecfg found in current directory or parent directories")
            click.echo("💡 Run 'tt init' to create configuration for this project")
            ctx.exit(1)
        
        ctx.obj['config'] = config
        ctx.obj['project_name'] = config.get_project_name()
        ctx.obj['server_url'] = config.get_server_url()
    except Exception as e:
        click.echo(f"❌ Error loading configuration: {e}")
        ctx.exit(1)

@cli.command()
@click.option('--name', prompt='Project name', help='Name for this project')
@click.option('--type', default='development', help='Project type')
@click.option('--server', default='http://localhost:9000', help='Time tracker server URL')
def init(name, type, server):
    """Initialize time tracking for this project"""
    
    # Auto-detect some project info
    language = 'unknown'
    framework = 'unknown'
    
    cwd = Path.cwd()
    
    # Detect language
    if list(cwd.glob('*.py')) or (cwd / 'requirements.txt').exists():
        language = 'python'
        if (cwd / 'manage.py').exists():
            framework = 'django'
        elif (cwd / 'app.py').exists() or (cwd / 'application.py').exists():
            framework = 'flask'
    elif list(cwd.glob('*.js')) or (cwd / 'package.json').exists():
        language = 'javascript'
        if (cwd / 'package.json').exists():
            try:
                import json
                with open(cwd / 'package.json') as f:
                    pkg = json.load(f)
                    deps = {**pkg.get('dependencies', {}), **pkg.get('devDependencies', {})}
                    if 'react' in deps:
                        framework = 'react'
                    elif 'vue' in deps:
                        framework = 'vue'
                    elif 'angular' in deps:
                        framework = 'angular'
            except:
                pass
    elif list(cwd.glob('*.go')):
        language = 'go'
    elif list(cwd.glob('*.rs')):
        language = 'rust'
    elif list(cwd.glob('*.java')):
        language = 'java'
    
    config_template = f"""# Universal Time Tracker Configuration
project:
  name: "{name}"
  id: "{name.lower().replace(' ', '-').replace('_', '-')}"
  type: "{type}"
  language: "{language}"
  framework: "{framework}"

server:
  url: "{server}"
  api_version: "v1"

tracking:
  categories:
    - "development"
    - "research"
    - "documentation"
    - "meetings"
    - "testing"
    - "deployment"
  default_category: "development"
  auto_commit: true
  break_reminders: false

git:
  enabled: true
  auto_detect_branch: true
  link_commits: true

reporting:
  timezone: "America/New_York"
  weekly_summary: true
  export_formats: ["json", "csv"]

# Project-specific command aliases (optional)
aliases:
  work: "development"
  code: "development"
  docs: "documentation"
  meet: "meetings"
  test: "testing"
"""
    
    config_file = Path.cwd() / ".timecfg"
    if config_file.exists():
        if not click.confirm(f"⚠️  .timecfg already exists. Overwrite?"):
            return
    
    with open(config_file, 'w') as f:
        f.write(config_template)
    
    click.echo(f"✅ Created .timecfg for project '{name}'")
    click.echo(f"🔍 Auto-detected: {language}/{framework}")
    click.echo("💡 Add .timecfg to your .gitignore if you don't want to commit it")
    click.echo("🚀 You can now use 'tt start', 'tt stop', etc.")

@cli.command()
@click.argument('description')
@click.option('--category', '-c', help='Time category')
@click.pass_context
def start(ctx, description, category):
    """Start tracking time"""
    config = ctx.obj['config']
    
    # Resolve category (check aliases first)
    if category:
        aliases = config.get_aliases()
        category = aliases.get(category, category)
    else:
        category = config.get_default_category()
    
    # Validate category
    valid_categories = config.get_categories()
    if category not in valid_categories:
        click.echo(f"⚠️  Unknown category: {category}")
        click.echo(f"Valid categories: {', '.join(valid_categories)}")
        if not click.confirm("Continue anyway?"):
            return
    
    payload = {
        'project': ctx.obj['project_name'],
        'description': description,
        'category': category
    }
    
    response = make_request('POST', f"{ctx.obj['server_url']}/sessions/start", json=payload)
    
    if response.status_code == 200:
        data = response.json()
        click.echo(f"⏰ Started: {description}")
        click.echo(f"📁 Project: {ctx.obj['project_name']}")
        click.echo(f"🏷️  Category: {category}")
        click.echo(f"🕐 Time: {datetime.now().strftime('%H:%M:%S')}")
    else:
        click.echo(f"❌ Error: {response.text}")

@cli.command()
@click.pass_context  
def stop(ctx):
    """Stop tracking time"""
    payload = {'project': ctx.obj['project_name']}
    
    response = make_request('POST', f"{ctx.obj['server_url']}/sessions/stop", json=payload)
    
    if response.status_code == 200:
        data = response.json()
        duration = data.get('duration_minutes', 0)
        hours = duration // 60
        minutes = duration % 60
        
        click.echo(f"⏹️  Stopped: {data.get('description', 'Unknown')}")
        click.echo(f"⏱️  Duration: {hours}h {minutes}m")
        click.echo(f"🕐 Time: {datetime.now().strftime('%H:%M:%S')}")
    else:
        click.echo(f"❌ Error: {response.text}")

@cli.command()
@click.argument('break_type', default='break')
@click.pass_context
def break_cmd(ctx, break_type):
    """Start or end a break"""
    payload = {
        'project': ctx.obj['project_name'],
        'break_type': break_type
    }
    
    response = make_request('POST', f"{ctx.obj['server_url']}/sessions/break", json=payload)
    
    if response.status_code == 200:
        data = response.json()
        
        if data['action'] == 'started':
            click.echo(f"☕ Break started: {break_type}")
            click.echo("💡 Use 'tt break' again to resume")
        else:
            duration = data.get('duration_minutes', 0)
            click.echo(f"▶️  Resumed from {data['break_type']} ({duration} minutes)")
    else:
        click.echo(f"❌ Error: {response.text}")

# Add alias for break command
@cli.command()
@click.argument('break_type', default='break')
@click.pass_context
def br(ctx, break_type):
    """Alias for break command"""
    ctx.invoke(break_cmd, break_type=break_type)

@cli.command()
@click.pass_context
def status(ctx):
    """Show current tracking status"""
    response = make_request('GET', f"{ctx.obj['server_url']}/sessions/status", 
                           params={'project': ctx.obj['project_name']})
    
    if response.status_code == 200:
        data = response.json()
        
        click.echo(f"\n📊 Status for {ctx.obj['project_name']}")
        click.echo("=" * 50)
        
        if data.get('active_session'):
            session = data['active_session']
            start_time = datetime.fromisoformat(session['start_time']).strftime('%H:%M:%S')
            
            click.echo(f"🟢 Active: {session['description']}")
            click.echo(f"   Started: {start_time}")
            click.echo(f"   Category: {session['category']}")
            
            if data.get('active_break'):
                break_info = data['active_break']
                break_start = datetime.fromisoformat(break_info['start_time']).strftime('%H:%M:%S')
                click.echo(f"   ☕ On {break_info['type']} since {break_start}")
        else:
            click.echo("⭕ No active session")
        
        # Daily summary
        daily = data.get('daily_summary', {})
        if daily.get('total_hours', 0) > 0:
            click.echo(f"\n📈 Today's total: {daily['total_hours']:.1f} hours ({daily['sessions']} sessions)")
    else:
        click.echo(f"❌ Error: {response.text}")

@cli.command()
@click.argument('period', default='today')
@click.option('--format', '-f', default='table', help='Output format: table, json')
@click.pass_context
def report(ctx, period, format):
    """Generate time tracking reports (today, week, month)"""
    
    if period not in ['today', 'week', 'month']:
        click.echo("❌ Invalid period. Use: today, week, month")
        return
    
    params = {'project': ctx.obj['project_name'], 'format': format}
    response = make_request('GET', f"{ctx.obj['server_url']}/reports/{period}", params=params)
    
    if response.status_code == 200:
        data = response.json()
        
        if format == 'json':
            import json
            click.echo(json.dumps(data, indent=2))
            return
        
        # Table format
        click.echo(f"\n📊 {period.title()} Report for {ctx.obj['project_name']}")
        click.echo("=" * 60)
        click.echo(f"Period: {data['start_date']} to {data['end_date']}")
        click.echo(f"Total Hours: {data['total_hours']:.1f}")
        click.echo(f"Total Sessions: {data['total_sessions']}")
        
        if data.get('category_breakdown'):
            click.echo(f"\n📋 Category Breakdown:")
            for category, hours in data['category_breakdown'].items():
                click.echo(f"   {category:15}: {hours:5.1f}h")
        
        if len(data.get('sessions', [])) > 0:
            click.echo(f"\n📝 Recent Sessions:")
            for session in data['sessions'][-5:]:  # Show last 5
                start = datetime.fromisoformat(session['start_time']).strftime('%m/%d %H:%M')
                duration = session['duration_minutes']
                hours = duration // 60
                minutes = duration % 60
                click.echo(f"   {start} - {session['description'][:40]:40} ({hours}h {minutes}m)")
    else:
        click.echo(f"❌ Error: {response.text}")

@cli.command()
@click.pass_context
def commit(ctx):
    """Link current git commit to active session"""
    
    # Check if git is available and we're in a repo
    try:
        result = subprocess.run(['git', 'rev-parse', '--git-dir'], 
                              capture_output=True, text=True, check=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        click.echo("❌ Not in a git repository or git not available")
        return
    
    # Get current commit info
    try:
        result = subprocess.run(['git', 'rev-parse', 'HEAD'], 
                              capture_output=True, text=True, check=True)
        commit_hash = result.stdout.strip()
        
        result = subprocess.run(['git', 'log', '-1', '--pretty=%B'], 
                              capture_output=True, text=True, check=True)
        commit_message = result.stdout.strip()
        
        payload = {
            'project': ctx.obj['project_name'],
            'commit_hash': commit_hash,
            'commit_message': commit_message
        }
        
        response = make_request('POST', f"{ctx.obj['server_url']}/sessions/commit", json=payload)
        
        if response.status_code == 200:
            data = response.json()
            click.echo(f"📝 Linked commit {data['commit_hash']}: {commit_message.split()[0] if commit_message else 'No message'}")
        else:
            click.echo(f"❌ Error: {response.text}")
            
    except subprocess.CalledProcessError:
        click.echo("❌ Error getting git commit information")

@cli.command()
@click.pass_context
def projects(ctx):
    """List all tracked projects"""
    response = make_request('GET', f"{ctx.obj['server_url']}/projects")
    
    if response.status_code == 200:
        projects = response.json()
        
        if not projects:
            click.echo("📭 No projects found")
            return
        
        click.echo(f"\n📁 Tracked Projects ({len(projects)})")
        click.echo("=" * 60)
        
        for project in projects:
            last_activity = "Never"
            if project.get('last_activity'):
                last_activity = datetime.fromisoformat(project['last_activity']).strftime('%Y-%m-%d %H:%M')
            
            click.echo(f"{project['name']:30} {project.get('type', 'unknown'):12} {last_activity}")
    else:
        click.echo(f"❌ Error: {response.text}")

if __name__ == '__main__':
    # Add break as an alias since it's a Python keyword
    cli.add_command(break_cmd, name='break')
    cli()
