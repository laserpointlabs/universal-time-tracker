# Configuration Guide

Complete guide to configuring the Universal Time Tracker for your projects.

## Project Configuration File (`.timecfg`)

Each project should have a `.timecfg` file in its root directory that defines project-specific settings.

### Basic Configuration

```yaml
# Universal Time Tracker Configuration
project:
  name: "My Awesome Project"
  id: "my-awesome-project"
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

## Configuration Sections

### Project Settings

```yaml
project:
  name: "Project Name"           # Display name for the project
  id: "project-slug"            # Unique identifier (auto-generated if not set)
  type: "development"           # Project type for categorization
  language: "python"            # Primary programming language
  framework: "flask"            # Primary framework/library
  description: "Optional description"  # Project description
  repository: "https://github.com/user/repo"  # Git repository URL
```

**Project Types:**
- `development` - Software development projects
- `web-development` - Web applications
- `mobile-development` - Mobile apps
- `data-science` - Data analysis/ML projects
- `research` - Research projects
- `documentation` - Documentation projects
- `infrastructure` - DevOps/Infrastructure
- `design` - UI/UX design projects

### Server Configuration

```yaml
server:
  url: "http://localhost:9000"  # Time tracker server URL
  api_version: "v1"             # API version to use
  timeout: 30                   # Request timeout in seconds
  retry_attempts: 3             # Number of retry attempts
```

### Tracking Settings

```yaml
tracking:
  categories:                   # Available time categories
    - "development"
    - "research"
    - "documentation"
    - "meetings"
    - "testing"
    - "deployment"
    - "review"
    - "planning"
    - "debugging"
  default_category: "development"  # Default category for sessions
  auto_commit: true               # Auto-link git commits to sessions
  break_reminders: false          # Enable break reminders
  min_session_duration: 1         # Minimum session duration (minutes)
  auto_stop_idle: 30              # Auto-stop after idle minutes
  session_timeout: 480            # Max session duration (minutes)
```

**Standard Categories:**
- `development` - Coding, implementation
- `research` - Investigation, learning, planning
- `documentation` - Writing docs, comments, README
- `meetings` - Standups, reviews, calls
- `testing` - Writing tests, debugging, QA
- `deployment` - CI/CD, releases, infrastructure
- `review` - Code review, design review
- `planning` - Architecture, estimates, tickets
- `debugging` - Bug fixes, troubleshooting

### Git Integration

```yaml
git:
  enabled: true                 # Enable git integration
  auto_detect_branch: true      # Auto-detect current branch
  link_commits: true            # Link commits to active sessions
  commit_message_template: "{category}: {description}"  # Commit message template
  exclude_branches:             # Branches to exclude from tracking
    - "main"
    - "master"
    - "develop"
  include_patterns:             # File patterns to include
    - "*.py"
    - "*.js"
    - "*.md"
  exclude_patterns:             # File patterns to exclude
    - "*.log"
    - "node_modules/*"
    - ".git/*"
```

### Reporting Configuration

```yaml
reporting:
  timezone: "America/New_York"  # Timezone for reports
  weekly_summary: true          # Generate weekly summaries
  daily_summary: true           # Generate daily summaries
  export_formats:               # Available export formats
    - "json"
    - "csv"
    - "pdf"
  email_reports: false          # Enable email reports
  report_email: "user@example.com"  # Email for reports
  working_hours:                # Define working hours
    start: "09:00"
    end: "17:00"
  working_days:                 # Define working days
    - "monday"
    - "tuesday"
    - "wednesday"
    - "thursday"
    - "friday"
```

### Aliases

```yaml
aliases:
  # Category aliases
  work: "development"
  code: "development"
  coding: "development"
  dev: "development"
  docs: "documentation"
  meet: "meetings"
  test: "testing"
  debug: "debugging"
  
  # Custom command aliases
  standup: "meetings"
  review: "review"
  planning: "planning"
```

## Advanced Configuration

### Environment-Specific Settings

You can have different configurations for different environments:

```yaml
# .timecfg
project:
  name: "My Project"

# Override server URL for development
environments:
  development:
    server:
      url: "http://localhost:9000"
  
  production:
    server:
      url: "https://timetracker.company.com"
  
  staging:
    server:
      url: "https://staging-timetracker.company.com"
```

Use with environment variable:
```bash
export TIME_TRACKER_ENV=production
./cli/tt start "Working on production issue"
```

### Team Configuration

For team projects, you can define team-specific settings:

```yaml
team:
  name: "Frontend Team"
  members:
    - "alice@company.com"
    - "bob@company.com"
  shared_categories:
    - "development"
    - "code-review"
    - "team-meetings"
  sprint_duration: 14           # Sprint duration in days
  standup_time: "09:00"        # Daily standup time
```

### Integration Settings

```yaml
integrations:
  jira:
    enabled: true
    server: "https://company.atlassian.net"
    project_key: "PROJ"
    auto_link_tickets: true
  
  slack:
    enabled: true
    webhook_url: "https://hooks.slack.com/..."
    notify_on_session_start: false
    notify_on_daily_summary: true
  
  github:
    enabled: true
    repository: "user/repo"
    auto_create_pr_comments: false
```

### Notification Settings

```yaml
notifications:
  break_reminders:
    enabled: true
    interval: 60                # Remind every 60 minutes
    message: "Time for a break!"
  
  session_limits:
    enabled: true
    max_duration: 240           # Max 4 hours
    warning_at: 180             # Warn at 3 hours
  
  daily_goals:
    enabled: true
    target_hours: 6
    notify_on_target: true
```

## Configuration Validation

### Validate Configuration
```bash
# Check configuration syntax
./cli/tt config --validate

# Show current configuration
./cli/tt config --show

# Show effective configuration (with defaults)
./cli/tt config --show --full
```

### Configuration Schema

The configuration follows a strict schema. Here are the validation rules:

**Required Fields:**
- `project.name`
- `server.url`

**Optional Fields with Defaults:**
- `server.api_version` → `"v1"`
- `tracking.default_category` → `"development"`
- `tracking.auto_commit` → `false`
- `git.enabled` → `false`
- `reporting.timezone` → System timezone

**Validation Rules:**
- Project name must be 1-200 characters
- Server URL must be valid HTTP/HTTPS URL
- Categories must be non-empty strings
- Timezone must be valid IANA timezone

## Best Practices

### 1. Consistent Category Naming
Use consistent category names across projects:
```yaml
tracking:
  categories:
    - "feature-development"    # Not just "development"
    - "bug-fixes"             # Not just "debugging"
    - "code-review"           # Not just "review"
    - "documentation"
    - "testing"
    - "meetings"
```

### 2. Meaningful Project IDs
Use descriptive project IDs:
```yaml
project:
  id: "ecommerce-frontend"    # Good
  # id: "proj1"               # Bad
```

### 3. Appropriate Aliases
Create aliases that match your workflow:
```yaml
aliases:
  bug: "bug-fixes"
  feat: "feature-development"
  docs: "documentation"
  meet: "meetings"
```

### 4. Timezone Configuration
Always set your timezone explicitly:
```yaml
reporting:
  timezone: "America/New_York"  # Explicit
  # timezone: "EST"             # Avoid abbreviations
```

### 5. Version Control
**Include `.timecfg` in version control** so team members share configuration:
```bash
git add .timecfg
git commit -m "Add time tracking configuration"
```

## Configuration Templates

### Web Development Project
```yaml
project:
  name: "E-commerce Frontend"
  type: "web-development"
  language: "javascript"
  framework: "react"

tracking:
  categories:
    - "feature-development"
    - "bug-fixes"
    - "ui-design"
    - "api-integration"
    - "testing"
    - "code-review"
    - "meetings"
  default_category: "feature-development"

aliases:
  feat: "feature-development"
  bug: "bug-fixes"
  ui: "ui-design"
  api: "api-integration"
  test: "testing"
  review: "code-review"
```

### Data Science Project
```yaml
project:
  name: "Customer Analytics"
  type: "data-science"
  language: "python"
  framework: "pandas"

tracking:
  categories:
    - "data-exploration"
    - "data-cleaning"
    - "model-development"
    - "model-evaluation"
    - "visualization"
    - "documentation"
    - "meetings"
  default_category: "data-exploration"

aliases:
  explore: "data-exploration"
  clean: "data-cleaning"
  model: "model-development"
  eval: "model-evaluation"
  viz: "visualization"
```

### Mobile App Project
```yaml
project:
  name: "Mobile Banking App"
  type: "mobile-development"
  language: "kotlin"
  framework: "android"

tracking:
  categories:
    - "feature-development"
    - "ui-implementation"
    - "api-integration"
    - "testing"
    - "performance-optimization"
    - "bug-fixes"
    - "code-review"
  default_category: "feature-development"

aliases:
  feat: "feature-development"
  ui: "ui-implementation"
  api: "api-integration"
  perf: "performance-optimization"
  bug: "bug-fixes"
```

## Environment Variables

You can override configuration using environment variables:

```bash
# Server configuration
export TIME_TRACKER_SERVER_URL="http://custom-server:9000"
export TIME_TRACKER_API_VERSION="v2"

# Project configuration
export TIME_TRACKER_PROJECT_NAME="Override Project Name"
export TIME_TRACKER_DEFAULT_CATEGORY="research"

# Reporting configuration  
export TIME_TRACKER_TIMEZONE="UTC"
export TIME_TRACKER_EXPORT_FORMAT="csv"
```

Environment variables take precedence over `.timecfg` settings.

## Troubleshooting Configuration

### Common Issues

**Invalid YAML Syntax**
```bash
./cli/tt config --validate
# Error: Invalid YAML syntax at line 15
```

**Missing Required Fields**
```bash
./cli/tt config --validate
# Error: project.name is required
```

**Invalid Server URL**
```bash
./cli/tt start "Test session"
# Error: Cannot connect to server at http://invalid-url:9000
```

**Category Not Found**
```bash
./cli/tt start "Test" -c invalid-category
# Error: Category 'invalid-category' not found in project configuration
```

### Debug Configuration
```bash
# Show effective configuration
./cli/tt config --show --debug

# Test server connection
./cli/tt status --verbose

# Validate and fix configuration
./cli/tt config --validate --fix
```
