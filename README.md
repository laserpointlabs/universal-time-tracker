# Universal Time Tracker

A powerful, intelligent time tracking system for software projects with advanced analytics and beautiful visualizations.

## 🚀 Features

### Core Time Tracking
- **🐳 Dockerized server** - One container for all projects
- **📁 Project-based tracking** with automatic project detection  
- **🏷️ Category-based sessions** (development, testing, documentation, meetings, etc.)
- **⏸️ Break tracking** with automatic session pause/resume
- **🔗 Git integration** for linking commits to sessions
- **🌍 Cross-platform CLI** for seamless workflow integration

### Advanced Analytics & Visualization
- **🔥 GitHub-style Activity Heatmap** - Visualize your coding activity across the year
- **📊 Category Breakdown** - Understand how you spend your time with trends
- **📈 Productivity Patterns** - Discover your most productive hours and days  
- **⏱️ Session Analysis** - Get insights on session lengths and break patterns
- **💡 Smart Recommendations** - Personalized productivity suggestions

### Beautiful Dashboard
- **🎨 Interactive Web Dashboard** at http://localhost:9000/dashboard
- **📱 Responsive design** that works on all devices
- **📊 Real-time charts** powered by Chart.js
- **🎯 Multiple visualization types** (heatmaps, pie charts, bar charts, line graphs)

## 📋 Quick Start

### 1. Start the Time Tracking Server
```bash
cd universal-time-tracker
docker-compose up -d
```

### 2. Initialize a Project
```bash
cd ~/your-project
./path/to/universal-time-tracker/cli/tt init
# Edit .timecfg as needed
```

### 3. Start Tracking Time
```bash
./path/to/universal-time-tracker/cli/tt start "Working on new feature" -c development
./path/to/universal-time-tracker/cli/tt break coffee
./path/to/universal-time-tracker/cli/tt stop
```

### 4. View Analytics Dashboard
Open http://localhost:9000/dashboard in your browser and enter your project name to see:
- GitHub-style activity heatmap
- Category breakdown with trends
- Productivity patterns and insights
- Session analysis and recommendations

## 🏗️ Architecture

- **Flask Server** - RESTful API with SQLite database (port 9000)
- **Click-based CLI** - Intuitive command-line interface
- **Project Configuration** - Per-project `.timecfg` files for customization
- **Analytics Engine** - Advanced pattern recognition and insights

## 📚 Documentation

- **[CLI Cheatsheet](docs/cli_cheatsheet.md)** - Quick reference for all CLI commands
- **[API Reference](docs/api_reference.md)** - Complete REST API documentation  
- **[Configuration Guide](docs/configuration.md)** - Project configuration options
- **[Analytics Guide](docs/analytics.md)** - Understanding analytics and insights
- **[Docker Setup](docs/docker_setup.md)** - Deployment and configuration

## 🎯 Use Cases

- **Software Development** - Track coding sessions across multiple projects
- **Freelancing** - Generate detailed time reports for clients
- **Project Management** - Understand team productivity patterns
- **Personal Productivity** - Optimize your work habits and schedule
- **Research & Documentation** - Track time across different activities

## 📊 Analytics Features

### 🔥 Activity Heatmap
GitHub-style visualization showing:
- Daily activity levels (0-4 intensity scale)
- Full year calendar grid (53 weeks)
- Activity statistics and trends
- Hover details for each day

### 📊 Category Analysis
- Time distribution across categories
- Trend analysis (↗️ up, ↘️ down, → stable)
- Session count and duration metrics
- Daily breakdown for pattern recognition

### 📈 Productivity Insights
- **Best hours**: "Most productive at 10:00-11:00"
- **Peak days**: "Most productive on Wednesdays"
- **Work patterns**: Hourly and weekly breakdowns
- **Personalized tips**: Based on your actual data

### ⏱️ Session Patterns
- Session length distribution (short/medium/long)
- Break-to-work ratios and optimization
- Focus time analysis
- Workflow recommendations

## 🚀 Quick Commands

```bash
# Project setup
./cli/tt init                               # Initialize project tracking
./cli/tt init --name "My Project"          # Initialize with custom name

# Time tracking  
./cli/tt start "Working on feature X" -c development    # Start session
./cli/tt break coffee                      # Take a coffee break
./cli/tt stop                              # Stop current session
./cli/tt status                            # Check current status

# Reporting & analytics
./cli/tt report today                      # Today's summary
./cli/tt report week                       # Weekly report
./cli/tt report month                      # Monthly report

# View analytics dashboard
open http://localhost:9000/dashboard       # Interactive analytics
```

## ⚙️ Configuration

Each project gets a `.timecfg` file for customization:

```yaml
# Universal Time Tracker Configuration
project:
  name: "My Awesome Project"
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

# Project-specific aliases
aliases:
  work: "development"
  docs: "documentation"
  meet: "meetings"
```

## 🔗 API Endpoints

### Core Tracking
- `POST /api/v1/sessions/start` - Start tracking session
- `POST /api/v1/sessions/stop` - Stop active session
- `POST /api/v1/sessions/break` - Manage breaks
- `GET /api/v1/sessions/status` - Get current status

### Analytics  
- `GET /api/v1/analytics/heatmap` - GitHub-style activity heatmap
- `GET /api/v1/analytics/category-breakdown` - Category time distribution
- `GET /api/v1/analytics/productivity-trends` - Hourly/daily patterns
- `GET /api/v1/analytics/session-patterns` - Session and break analysis

### Reports
- `GET /api/v1/reports/{period}` - Generate time reports
- `GET /dashboard` - Interactive analytics dashboard

## 📱 Example Workflows

### Daily Development
```bash
# Morning standup
./cli/tt start "Daily standup" -c meetings
./cli/tt stop

# Feature development
./cli/tt start "Implementing user authentication" -c development
./cli/tt break lunch
./cli/tt stop

# Afternoon code review
./cli/tt start "Code review for PR #123" -c review
./cli/tt stop

# Check progress
./cli/tt report today
```

### Sprint Workflow
```bash
# Sprint planning
./cli/tt start "Sprint planning session" -c planning

# Development work
./cli/tt start "User story US-001: Login page" -c development

# Testing
./cli/tt start "Testing login functionality" -c testing

# Sprint review
./cli/tt report week
```

## 🎨 Dashboard Features

Visit **http://localhost:9000/dashboard** to see:

- **🔥 Activity Heatmap**: GitHub-style year overview
- **📊 Category Pie Chart**: Time distribution visualization  
- **📈 Hourly Bar Chart**: Peak productivity hours
- **📅 Weekly Line Chart**: Daily productivity patterns
- **💡 Smart Insights**: Personalized recommendations
- **📋 Session Stats**: Focus and break analysis

## 🛠️ Installation & Setup

### Prerequisites
- Docker & Docker Compose
- Python 3.8+ (for CLI)
- Modern web browser (for dashboard)

### Quick Installation
```bash
# 1. Clone repository
git clone https://github.com/your-org/universal-time-tracker.git
cd universal-time-tracker

# 2. Start server
docker-compose up -d

# 3. Verify installation
curl http://localhost:9000/health

# 4. Initialize your first project
cd ~/your-project
/path/to/universal-time-tracker/cli/tt init
```

## 🏗️ Architecture

```
├── server/          # Flask API server (Docker)
│   ├── src/         # Python application code
│   ├── Dockerfile   # Container configuration
│   └── requirements.txt
├── cli/             # Click-based CLI client
│   ├── tt.py        # Main CLI application
│   └── tt           # Shell wrapper script
├── data/            # Persistent SQLite database
├── docs/            # Complete documentation
│   ├── cli_cheatsheet.md
│   ├── api_reference.md
│   ├── configuration.md
│   ├── analytics.md
│   └── docker_setup.md
└── docker-compose.yml
```

The system uses a centralized Flask server (port 9000) with SQLite database for data persistence, and lightweight CLI clients that read project-specific `.timecfg` configuration files.

## 🔧 Requirements

- **Server**: Docker, 1GB RAM, 500MB disk space
- **CLI**: Python 3.8+, pip packages (pyyaml, requests, click)
- **Dashboard**: Modern browser (Chrome, Firefox, Safari)
- **Network**: HTTP access to localhost:9000

## 📄 License

Open source - feel free to use and modify as needed for your time tracking requirements!
