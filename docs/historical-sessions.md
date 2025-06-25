# Historical Session Creation

The Universal Time Tracker now supports creating historical sessions for time periods that you may have missed tracking in real-time.

## Overview

The `tt create` command allows you to add sessions with custom start and end times, making it easy to backfill your time tracking data.

## Usage

### Basic Syntax

```bash
tt create "Description" --start-time "YYYY-MM-DD HH:MM" [options]
```

### Options

- `--start-time, -s`: **Required**. Start time in format `YYYY-MM-DD HH:MM` or `YYYY-MM-DDTHH:MM`
- `--end-time, -e`: End time in format `YYYY-MM-DD HH:MM` or `YYYY-MM-DDTHH:MM`
- `--duration, -d`: Duration in hours (e.g., `2.5` for 2.5 hours) - alternative to end-time
- `--category, -c`: Time category (defaults to project's default category)

### Examples

#### Create a completed session with duration
```bash
tt create "Code review and bug fixes" --start-time "2024-01-15 09:00" --duration 3.5 --category "development"
```

#### Create a completed session with end time
```bash
tt create "Team meeting" --start-time "2024-01-15 14:00" --end-time "2024-01-15 15:30" --category "meetings"
```

#### Create an active session (no end time)
```bash
tt create "Research phase" --start-time "2024-01-15 16:00" --category "research"
```

#### Create a session using ISO format
```bash
tt create "Documentation work" --start-time "2024-01-15T10:30" --duration 2.0 --category "documentation"
```

## Use Cases

- **Backfill missed sessions**: Add sessions you forgot to track
- **Batch import**: Import time data from other tools
- **Correction**: Fix incorrect session times
- **Planning**: Pre-schedule future sessions

## Notes

- Sessions are created with the specified start and end times exactly as provided
- Duration is automatically calculated when both start and end times are provided
- If no end time is provided, the session will be marked as active
- The command validates that end time is after start time
- All sessions are associated with the current project (from `.timecfg`)

## Integration

Historical sessions integrate seamlessly with all existing features:
- Appear in reports and analytics
- Can be edited via the web interface
- Included in project summaries
- Support breaks and git commits (for active sessions) 