# Database Management

The Universal Time Tracker now includes comprehensive database management capabilities to help you review and edit your time tracking data.

## Web-Based Database Browser

Access the database browser by navigating to `/db` in your web browser when the server is running.

### Features

- **Dashboard Overview**: View database statistics and quick access to all features
- **Project Management**: Browse, view details, and edit projects
- **Session Management**: View and edit sessions with filtering capabilities
- **Search Functionality**: Search across projects and sessions
- **Data Export**: Export all data as JSON

### Navigation

The database browser includes a sidebar with the following sections:

- **Dashboard**: Overview and statistics
- **Projects**: List and manage all projects
- **Sessions**: List and manage all sessions with filters
- **Search**: Search across all data
- **Export Data**: Download database as JSON

### Filtering Sessions

When viewing sessions, you can filter by:

- Project name
- Category (development, debugging, testing, etc.)
- Date range (from/to dates)

### Editing Data

- Click the edit button (pencil icon) next to any project or session
- Make your changes in the form
- Save to update the database

## Command-Line Database Manager

A command-line tool is also available for quick database operations.

### Installation

The CLI tool requires the `tabulate` package:

```bash
pip install tabulate
```

### Usage

```bash
python db_manager.py <command> [options]
```

### Commands

#### Show Statistics
```bash
python db_manager.py stats
```

#### List Projects
```bash
python db_manager.py projects
```

#### List Sessions
```bash
python db_manager.py sessions [--limit 20] [--project "project_name"]
```

#### Search Data
```bash
python db_manager.py search --query "search_term"
```

#### Export Data
```bash
python db_manager.py export [--output filename.json]
```

#### Show Project Details
```bash
python db_manager.py project --id <project_id>
```

### Examples

```bash
# Show database overview
python db_manager.py stats

# List recent sessions for a specific project
python db_manager.py sessions --project "my-project" --limit 10

# Search for sessions containing "bug fix"
python db_manager.py search --query "bug fix"

# Export data to a file
python db_manager.py export --output backup.json

# View details for project ID 5
python db_manager.py project --id 5
```

## Database Schema

The database contains three main tables:

### Projects
- `id`: Primary key
- `name`: Project name (unique)
- `type`: Project type (development, research, etc.)
- `language`: Programming language
- `framework`: Framework used
- `path`: Project path
- `git_remote`: Git repository URL
- `created_at`: Creation timestamp
- `last_activity`: Last activity timestamp

### Sessions
- `id`: Primary key
- `project_id`: Foreign key to projects
- `start_time`: Session start timestamp
- `end_time`: Session end timestamp (null if active)
- `duration_minutes`: Calculated duration in minutes
- `category`: Session category
- `description`: Session description
- `git_commits`: JSON string of git commits

### Breaks
- `id`: Primary key
- `session_id`: Foreign key to sessions
- `start_time`: Break start timestamp
- `end_time`: Break end timestamp
- `duration_minutes`: Calculated duration in minutes
- `break_type`: Type of break (break, lunch, coffee, etc.)

## Data Export/Import

### Export
Data can be exported in JSON format containing all projects, sessions, and breaks with their relationships intact.

### Import
While not currently implemented in the web interface, the JSON export format can be used to create import scripts if needed.

## Security Considerations

- The database browser is designed for local development and personal use
- No authentication is currently implemented
- Consider implementing authentication for production use
- Database file permissions should be restricted appropriately

## Troubleshooting

### Database Not Found
If you get a "Database not found" error:

1. Check that the database file exists at `data/timetracker.db`
2. Verify the `DATABASE_PATH` environment variable is set correctly
3. Ensure the server has been started at least once to create the database

### Permission Errors
If you get permission errors:

1. Check file permissions on the database file
2. Ensure the user running the server has read/write access
3. On Linux/Mac, you may need to adjust ownership: `chown user:group data/timetracker.db`

### Web Interface Not Loading
If the web interface doesn't load:

1. Check that the server is running
2. Verify you're accessing the correct URL (e.g., `http://localhost:5000/db`)
3. Check browser console for JavaScript errors
4. Ensure all required packages are installed

## Future Enhancements

Potential future improvements:

- User authentication and authorization
- Bulk edit operations
- Data import functionality
- Advanced analytics and reporting
- Database backup and restore
- Real-time data synchronization
- Mobile-friendly interface 