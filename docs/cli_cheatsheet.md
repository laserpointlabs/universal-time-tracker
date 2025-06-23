# Time Tracker CLI Cheatsheet

Quick reference for all Universal Time Tracker CLI commands.

## 🚀 Getting Started

### Install Dependencies
```bash
# Install Python dependencies (if not using wrapper script)
pip install pyyaml requests click
```

### Start Server
```bash
# Start the time tracking server
docker-compose up -d

# Check server health
curl http://localhost:9000/health
```

## 📁 Project Management

### Initialize Project
```bash
# Initialize tracking in current directory
./cli/tt init

# Initialize with custom project name
./cli/tt init --name "My Awesome Project"

# Initialize with project type
./cli/tt init --name "Web App" --type "web-development" --language "javascript"
```

### Project Configuration (`.timecfg`)
```yaml
# Universal Time Tracker Configuration
project:
  name: "My Project"
  id: "my-project-id"
  type: "development"
  language: "python"
  framework: "flask"

server:
  url: "http://localhost:9000"
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
```

## ⏱️ Time Tracking

### Start Session
```bash
# Basic session start
./cli/tt start "Working on user authentication"

# Start with specific category
./cli/tt start "Writing unit tests" -c testing
./cli/tt start "Code review" --category research

# Start with category alias (from .timecfg)
./cli/tt start "Morning standup" -c meet
```

### Stop Session
```bash
# Stop active session
./cli/tt stop

# Stop with additional notes
./cli/tt stop --notes "Completed login functionality"
```

### Manage Breaks
```bash
# Start a break
./cli/tt break

# Start specific break type
./cli/tt break lunch
./cli/tt break coffee
./cli/tt break meeting

# End break (resume session)
./cli/tt break --end
```

### Session Status
```bash
# Check current status
./cli/tt status

# Check status with details
./cli/tt status --verbose
```

## 📊 Reporting & Analytics

### Generate Reports
```bash
# Today's activity
./cli/tt report today

# This week's activity
./cli/tt report week

# This month's activity
./cli/tt report month

# Custom date range
./cli/tt report --start 2025-06-01 --end 2025-06-23

# Export report to file
./cli/tt report week --export csv
./cli/tt report month --export json
```

### View Analytics
```bash
# Open dashboard in browser
./cli/tt dashboard

# Or manually visit:
# http://localhost:9000/dashboard
```

## 🔗 Git Integration

### Link Commits
```bash
# Automatic commit linking (if enabled in .timecfg)
git commit -m "Add user authentication"
# Commit automatically linked to active session

# Manual commit linking
./cli/tt commit abc123 "Add user authentication"
```

## 🛠️ Advanced Usage

### Multiple Projects
```bash
# Switch between projects
cd ~/project-a
./cli/tt start "Working on feature A" -c development

cd ~/project-b  
./cli/tt start "Fixing bug B" -c debugging
# Previous session auto-stopped, new session started
```

### Categories
Common categories you can use:
- `development` - Coding, implementation
- `research` - Investigation, learning, planning
- `documentation` - Writing docs, comments, README
- `meetings` - Standups, reviews, calls
- `testing` - Writing tests, debugging, QA
- `deployment` - CI/CD, releases, infrastructure
- `review` - Code review, design review
- `planning` - Architecture, estimates, tickets

### Session Management
```bash
# List recent sessions
./cli/tt sessions

# List sessions for specific period
./cli/tt sessions --days 7
./cli/tt sessions --week
./cli/tt sessions --month

# Session details
./cli/tt session <session-id>
```

## 🌐 Server API Commands

### Direct API Calls
```bash
# Get projects
curl http://localhost:9000/api/v1/projects

# Get session status
curl "http://localhost:9000/api/v1/sessions/status?project=My%20Project"

# Get analytics heatmap
curl "http://localhost:9000/api/v1/analytics/heatmap?project=My%20Project&year=2025"

# Get category breakdown
curl "http://localhost:9000/api/v1/analytics/category-breakdown?project=My%20Project"

# Get productivity trends
curl "http://localhost:9000/api/v1/analytics/productivity-trends?project=My%20Project&days=30"

# Get session patterns
curl "http://localhost:9000/api/v1/analytics/session-patterns?project=My%20Project"
```

## 🐛 Troubleshooting

### Common Issues

**Server Not Running**
```bash
# Check if container is running
docker-compose ps

# Start server
docker-compose up -d

# Check logs
docker-compose logs -f
```

**Permission Issues**
```bash
# Make CLI executable
chmod +x ./cli/tt

# Install dependencies
pip install pyyaml requests click
```

**Configuration Issues**
```bash
# Validate .timecfg
./cli/tt config --validate

# Show current configuration
./cli/tt config --show

# Reset configuration
./cli/tt init --force
```

**No Active Session**
```bash
# Check status
./cli/tt status

# Start a new session
./cli/tt start "Current task" -c development
```

## 📱 Workflow Examples

### Daily Workflow
```bash
# Morning - start work
./cli/tt start "Daily standup" -c meetings
./cli/tt stop

./cli/tt start "Working on user dashboard" -c development

# Lunch break
./cli/tt break lunch
# Resume automatically when break ends

# Afternoon
./cli/tt start "Code review" -c review
./cli/tt stop

# End of day - check progress
./cli/tt report today
./cli/tt status
```

### Sprint Planning
```bash
# Planning session
./cli/tt start "Sprint planning" -c planning
./cli/tt stop

# Development work
./cli/tt start "Implement user stories 1-3" -c development
./cli/tt break coffee
./cli/tt stop

# Review progress
./cli/tt report week
```

### Bug Fixing
```bash
# Investigation
./cli/tt start "Investigating login bug" -c research
./cli/tt stop

# Implementation  
./cli/tt start "Fix authentication issue" -c development
./cli/tt stop

# Testing
./cli/tt start "Test login fix" -c testing
./cli/tt stop
```

## 🎯 Pro Tips

1. **Use descriptive session names** - Help analytics understand your work patterns
2. **Leverage categories** - Get better insights into time distribution
3. **Take regular breaks** - Use break tracking to maintain productivity
4. **Check the dashboard regularly** - Understand your productivity patterns
5. **Use aliases** - Define shortcuts in `.timecfg` for common categories
6. **Enable git integration** - Automatically link commits to sessions
7. **Generate weekly reports** - Track progress and plan improvements

## 🔗 Quick Links

- **Dashboard**: http://localhost:9000/dashboard
- **API Health**: http://localhost:9000/health
- **Configuration**: `.timecfg` in your project root
- **Server Logs**: `docker-compose logs -f`

## 📚 Related Documentation

- [README.md](../README.md) - Full documentation
- [API Reference](api_reference.md) - REST API details  
- [Configuration Guide](configuration.md) - Advanced configuration
- [Analytics Guide](analytics.md) - Understanding insights
