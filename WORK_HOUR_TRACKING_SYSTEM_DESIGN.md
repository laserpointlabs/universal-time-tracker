# Work Hour Tracking System Design
**Date**: June 23, 2025  
**Purpose**: Intelligent work hour capture and analysis system

## System Overview

A comprehensive time tracking system that integrates with your development workflow, handles interruptions intelligently, and provides detailed analytics.

## Proposed Architecture

### Option 1: JSON-Based Time Log (Recommended)
**Structure**: Daily JSON files with CLI helper scripts

```
time_logs/
├── 2025/
│   ├── 06/
│   │   ├── 2025-06-23.json
│   │   ├── 2025-06-24.json
│   │   └── week-25-summary.md
│   └── weekly_summaries/
└── scripts/
    ├── time_start.sh
    ├── time_stop.sh
    ├── time_break.sh
    └── time_summary.py
```

### Option 2: Enhanced Changelog Integration
**Structure**: Time entries embedded in changelog with metadata

### Option 3: Hybrid Approach
**Structure**: JSON for detailed logging + markdown summaries

## Detailed Design: JSON-Based System

### Daily Log Format
```json
{
  "date": "2025-06-23",
  "sessions": [
    {
      "id": "session_001",
      "start_time": "08:00:00",
      "end_time": "12:00:00",
      "duration_minutes": 240,
      "category": "development",
      "project": "DADM",
      "tasks": [
        {
          "description": "BPMN AI integration debugging",
          "git_commits": ["abc123", "def456"],
          "nre_category": "troubleshooting_debugging"
        }
      ],
      "breaks": [
        {
          "start_time": "10:15:00",
          "end_time": "10:30:00",
          "duration_minutes": 15,
          "type": "coffee_break"
        }
      ]
    },
    {
      "id": "session_002",
      "start_time": "13:00:00",
      "end_time": "17:30:00",
      "duration_minutes": 270,
      "category": "development",
      "project": "DADM",
      "tasks": [
        {
          "description": "Work hour tracking system design",
          "git_commits": [],
          "nre_category": "research_planning"
        }
      ],
      "breaks": []
    }
  ],
  "lunch_break": {
    "start_time": "12:00:00",
    "end_time": "13:00:00",
    "duration_minutes": 60
  },
  "daily_summary": {
    "total_work_minutes": 510,
    "total_break_minutes": 15,
    "total_lunch_minutes": 60,
    "net_work_hours": 8.5,
    "billable_hours": 8.5,
    "categories": {
      "development": 8.5,
      "meetings": 0,
      "research": 0
    }
  }
}
```

### CLI Helper Scripts

#### time_start.sh
```bash
#!/bin/bash
# Usage: ./time_start.sh "development" "DADM" "BPMN AI debugging"
CATEGORY=$1
PROJECT=$2
DESCRIPTION=$3
TIMESTAMP=$(date +"%H:%M:%S")
DATE=$(date +"%Y-%m-%d")

# Add start entry to today's log
python scripts/time_logger.py start "$DATE" "$TIMESTAMP" "$CATEGORY" "$PROJECT" "$DESCRIPTION"
echo "⏰ Started tracking: $DESCRIPTION at $TIMESTAMP"
```

#### time_break.sh
```bash
#!/bin/bash
# Usage: ./time_break.sh "coffee_break" or ./time_break.sh "lunch"
BREAK_TYPE=${1:-"break"}
TIMESTAMP=$(date +"%H:%M:%S")
DATE=$(date +"%Y-%m-%d")

python scripts/time_logger.py break "$DATE" "$TIMESTAMP" "$BREAK_TYPE"
echo "☕ Break started: $BREAK_TYPE at $TIMESTAMP"
```

#### time_stop.sh
```bash
#!/bin/bash
# Usage: ./time_stop.sh
TIMESTAMP=$(date +"%H:%M:%S")
DATE=$(date +"%Y-%m-%d")

python scripts/time_logger.py stop "$DATE" "$TIMESTAMP"
echo "⏹️  Stopped tracking at $TIMESTAMP"
```

## Python Time Logger Core

### time_logger.py
```python
#!/usr/bin/env python3
import json
import sys
import os
from datetime import datetime, timedelta
from pathlib import Path

class TimeLogger:
    def __init__(self):
        self.log_dir = Path("time_logs")
        self.log_dir.mkdir(exist_ok=True)
        
    def get_log_file(self, date):
        year, month = date.split('-')[:2]
        year_dir = self.log_dir / year
        month_dir = year_dir / month
        month_dir.mkdir(parents=True, exist_ok=True)
        return month_dir / f"{date}.json"
    
    def load_daily_log(self, date):
        log_file = self.get_log_file(date)
        if log_file.exists():
            with open(log_file, 'r') as f:
                return json.load(f)
        else:
            return {
                "date": date,
                "sessions": [],
                "lunch_break": None,
                "daily_summary": {}
            }
    
    def save_daily_log(self, date, log_data):
        log_file = self.get_log_file(date)
        with open(log_file, 'w') as f:
            json.dump(log_data, f, indent=2)
    
    def start_session(self, date, time, category, project, description):
        log_data = self.load_daily_log(date)
        
        session = {
            "id": f"session_{len(log_data['sessions']) + 1:03d}",
            "start_time": time,
            "end_time": None,
            "duration_minutes": None,
            "category": category,
            "project": project,
            "tasks": [{
                "description": description,
                "git_commits": [],
                "nre_category": ""
            }],
            "breaks": []
        }
        
        log_data['sessions'].append(session)
        self.save_daily_log(date, log_data)
    
    def stop_session(self, date, time):
        log_data = self.load_daily_log(date)
        
        if log_data['sessions']:
            last_session = log_data['sessions'][-1]
            if last_session['end_time'] is None:
                last_session['end_time'] = time
                
                # Calculate duration
                start = datetime.strptime(last_session['start_time'], "%H:%M:%S")
                end = datetime.strptime(time, "%H:%M:%S")
                duration = end - start
                
                # Subtract break time
                break_minutes = sum(b['duration_minutes'] for b in last_session['breaks'])
                net_minutes = int(duration.total_seconds() / 60) - break_minutes
                
                last_session['duration_minutes'] = net_minutes
                
                self.save_daily_log(date, log_data)
                self.update_daily_summary(date)

# CLI Interface
if __name__ == "__main__":
    logger = TimeLogger()
    command = sys.argv[1] if len(sys.argv) > 1 else "help"
    
    if command == "start":
        logger.start_session(sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5], sys.argv[6])
    elif command == "stop":
        logger.stop_session(sys.argv[2], sys.argv[3])
    elif command == "break":
        logger.add_break(sys.argv[2], sys.argv[3], sys.argv[4])
    else:
        print("Usage: time_logger.py [start|stop|break] ...")
```

## Weekly Summary Generator

### weekly_summary.py
```python
#!/usr/bin/env python3
import json
import glob
from datetime import datetime, timedelta
from pathlib import Path

class WeeklySummaryGenerator:
    def __init__(self):
        self.log_dir = Path("time_logs")
    
    def generate_week_summary(self, year, week_number):
        # Load all daily logs for the week
        week_data = self.load_week_data(year, week_number)
        
        # Generate summary
        summary = self.calculate_week_totals(week_data)
        
        # Create markdown report
        markdown = self.create_markdown_summary(year, week_number, summary)
        
        # Save summary file
        self.save_week_summary(year, week_number, markdown)
        
        return summary
    
    def create_markdown_summary(self, year, week_number, summary):
        return f"""# Work Hours Summary - Week {week_number}, {year}
**Period**: {summary['start_date']} to {summary['end_date']}
**Total Hours**: {summary['total_hours']:.1f}

## Daily Breakdown
{self.format_daily_breakdown(summary['daily_data'])}

## Category Summary
{self.format_category_summary(summary['categories'])}

## NRE Analysis
{self.format_nre_analysis(summary['nre_breakdown'])}

## Git Activity
{self.format_git_activity(summary['git_commits'])}

## Notes
{summary.get('notes', 'No additional notes')}
"""

# Usage example
if __name__ == "__main__":
    generator = WeeklySummaryGenerator()
    current_week = datetime.now().isocalendar()[1]
    summary = generator.generate_week_summary(2025, current_week)
    print(f"Generated summary for week {current_week}")
```

## Git Integration

### git-time-hook.sh
```bash
#!/bin/bash
# Git post-commit hook to automatically link commits to time entries

COMMIT_HASH=$(git rev-parse HEAD)
COMMIT_MESSAGE=$(git log -1 --pretty=%B)
DATE=$(date +"%Y-%m-%d")

# Add commit to current time session
python scripts/time_logger.py add_commit "$DATE" "$COMMIT_HASH" "$COMMIT_MESSAGE"
```

## Usage Workflow

### Daily Workflow
```bash
# Start your day
./time_start.sh "development" "DADM" "BPMN AI integration debugging"

# Take a coffee break
./time_break.sh "coffee_break"

# Resume work (automatically handled)
./time_resume.sh

# Lunch break
./time_break.sh "lunch"

# Afternoon session
./time_start.sh "development" "DADM" "Documentation updates"

# End of day
./time_stop.sh

# Generate daily summary
python scripts/time_summary.py today
```

### Weekly Workflow
```bash
# Generate weekly summary
python scripts/weekly_summary.py

# Update changelog with weekly hours
python scripts/update_changelog.py week
```

## Benefits of This System

### 1. **Intelligent Automation**
- Automatic duration calculation
- Git commit linking
- Break time tracking
- Smart session management

### 2. **Detailed Analytics**
- NRE category breakdown
- Project time allocation
- Weekly/monthly trends
- Productivity patterns

### 3. **Easy Integration**
- Simple CLI commands
- Git hook integration
- Changelog automation
- Export capabilities

### 4. **Flexible Reporting**
- Daily summaries
- Weekly reports
- Monthly analytics
- Custom time periods

Would you like me to implement this system? I can start with the basic JSON structure and CLI scripts, then add the Python automation layer.
