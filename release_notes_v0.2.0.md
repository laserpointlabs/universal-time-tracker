# Release Notes - Universal Time Tracker v0.2.0

**Release Date:** June 25, 2025  
**Version:** 0.2.0

## 🌟 What's New

### Web Interface and Dashboard
- **Modern Web UI**: Complete Bootstrap 5-based interface at `http://localhost:9000/`
- **Project Management Dashboard**: Visual overview of all projects with statistics
- **Real-time Session Monitoring**: Live tracking of active sessions with elapsed time
- **Interactive Charts**: Daily activity patterns and category breakdowns using Chart.js
- **Responsive Design**: Works on desktop, tablet, and mobile devices

### API Documentation  
- **Swagger/OpenAPI Docs**: Interactive API documentation at `/docs/` endpoint
- **Organized Endpoints**: APIs grouped into logical namespaces (projects, sessions, analytics, config)
- **Request/Response Models**: Complete schema documentation with examples
- **Try It Out**: Test API endpoints directly from the documentation interface

### Enhanced Project Management
- **Web-based CRUD**: Create, read, update, and delete projects through web interface
- **Project Dashboards**: Individual project pages with detailed analytics and session history
- **Configuration Download**: Generate and download `.timecfg` files from project pages
- **Quick Actions**: Start/stop tracking sessions with one-click buttons

### Historical Session Creation
- **CLI Command**: New `tt create` command for creating sessions with custom start/end times
- **API Endpoint**: New `/api/v1/sessions/create` endpoint for programmatic session creation
- **Flexible Time Formats**: Support for duration strings (e.g., "2h 30m") and specific timestamps
- **Category Support**: Assign categories to historical sessions during creation

### Enhanced Analytics
- **Daily Activity Charts**: Line charts showing work patterns over the last 7 days
- **Category Breakdowns**: Pie charts showing time distribution across work categories  
- **Statistical Insights**: Box plots overlaying daily variation patterns
- **Time Period Filtering**: View analytics for different time ranges (day, week, month, quarter, year)
- **Real-time Updates**: Dashboard automatically refreshes every 30 seconds

## 🐛 Bug Fixes

### CLI Tool Improvements
- **Virtual Environment Support**: Fixed `--user` pip install flag causing errors in virtual environments
- **Automatic Detection**: CLI now detects virtual environments and uses appropriate pip commands
- **Better Error Messages**: Improved guidance when package installation fails
- **Dependency Management**: Streamlined installation of required packages (click, requests, pyyaml)

### Docker and Environment
- **User ID Detection**: Fixed "unknown" user display in Docker containers
- **Database Path Resolution**: Improved SQLite database path handling for different environments
- **Template Serving**: Fixed Flask template and static file serving in containerized environments
- **Environment Variables**: Better support for `TIME_TRACKER_USER_ID` in Docker

### API and Backend
- **Session Duration Calculations**: Improved accuracy of time calculations and timezone handling
- **Error Response Handling**: Better validation and error messages across all endpoints
- **Database Relationships**: Enhanced model relationships and data serialization
- **Health Check Improvements**: More reliable health check endpoints for monitoring

## 📋 Migration Guide

### From v0.1.0 to v0.2.0

#### For Existing Users
- **No Data Loss**: All existing projects and sessions remain fully compatible
- **CLI Compatibility**: All existing CLI commands continue to work unchanged
- **New Web Access**: Simply navigate to `http://localhost:9000/` to access the new web interface

#### For Docker Users
- **Updated Container**: Pull the latest image for web interface support
- **Same Volume Mounts**: No changes needed to existing Docker Compose configurations
- **New Port Access**: Web interface available on port 9000 (same as API)

#### For API Consumers
- **Backward Compatible**: All existing API endpoints remain unchanged
- **New Endpoints**: Additional REST endpoints available for enhanced functionality
- **Enhanced Documentation**: Complete API documentation now available at `/docs/`

## 🚀 Getting Started with New Features

### Accessing the Web Interface
1. Start the server: `docker-compose up` or `cd server && python src/app.py`
2. Open browser to: `http://localhost:9000/`
3. Create projects and start tracking time visually

### Using the API Documentation
1. Navigate to: `http://localhost:9000/docs/`
2. Explore available endpoints and models
3. Test API calls directly from the interface

### Creating Historical Sessions
```bash
# Create a 2.5 hour session for yesterday
tt create "2h 30m" --description "Bug fixes" --category "development"

# Create session with specific times
tt create --start "2025-06-24 09:00" --end "2025-06-24 11:30" --description "Meeting"
```

### Downloading Project Configuration
1. Visit project page: `http://localhost:9000/project/YourProjectName`
2. Click "Download .timecfg" to get configuration file
3. Place file in your project directory for CLI integration

## 🔧 Technical Details

### New Dependencies
- `flask-restx==1.3.0` - Swagger/OpenAPI documentation
- `marshmallow==3.21.0` - Enhanced data serialization

### New Endpoints
- `GET /` - Web dashboard
- `GET /project/{name}` - Project-specific dashboard  
- `GET /docs/` - Swagger API documentation
- `GET /api/v1/config/timecfg/{project}` - Project configuration
- Enhanced CRUD operations for all resources

## 🎯 What's Coming Next

Version 0.3.0 will focus on:
- Advanced reporting and export capabilities
- Team collaboration features
- Integration with popular development tools (Git, VS Code, etc.)
- Mobile app development
- Advanced analytics and productivity insights
- **Summary Statistics**: Comprehensive overview showing total sessions, active sessions, and total time
- **Filtered Data Insights**: Summary statistics for both filtered and unfiltered session data
- **Enhanced Filtering**: Better session filtering with detailed statistical breakdowns
- **User Experience**: Improved session table with percentage indicators for filtered data

### Docker Environment Support
- **User ID Detection**: Fixed user identification issues in containerized environments
- **Environment Variable**: New `TIME_TRACKER_USER_ID` configuration option for Docker containers
- **Improved Logic**: Enhanced user ID retrieval for better cross-platform compatibility

## 🐛 Bug Fixes
- **User ID Display**: Fixed "unknown" user display in Docker environments
- **Session Creation**: Improved error handling for invalid time formats
- **Data Consistency**: Enhanced user identification across all session operations
- **Error Messages**: Better validation and user feedback for session creation

## 📋 Migration Guide

### From v0.1.0 to v0.2.0
- **No Breaking Changes**: All existing functionality remains fully compatible
- **Database**: No schema changes or migrations required
- **Configuration**: Optional addition of `TIME_TRACKER_USER_ID` environment variable for Docker deployments
- **Dependencies**: No new external dependencies added

### New Features Usage

#### Historical Session Creation
```bash
# Create a session with duration
tt create "2h 30m" --category development

# Create a session with specific start/end times
tt create --start "2025-01-27 09:00" --end "2025-01-27 11:30" --category meetings

# Create a session ending now
tt create --start "2025-01-27 14:00" --category research
```

#### Docker Configuration (Optional)
```yaml
# docker-compose.yml
environment:
  - TIME_TRACKER_USER_ID=jdehart
```

## 🔧 Technical Details

### API Changes
- **New Endpoint**: `POST /api/v1/sessions/create`
- **Parameters**: `start_time`, `end_time` (optional), `category` (optional)
- **Response**: Standard session object with created session details

### CLI Enhancements
- **New Command**: `tt create` with flexible time parsing
- **Options**: `--start`, `--end`, `--category`, `--duration`
- **Validation**: Improved error handling and user feedback

### Analytics Backend
- **Statistical Calculations**: Enhanced daily variation analysis
- **Data Processing**: Improved session data aggregation for statistical insights
- **Performance**: Optimized queries for large datasets

### Frontend Improvements
- **Chart.js Integration**: Box plot visualization with statistical overlays
- **Interactive Elements**: Enhanced tooltips and user interactions
- **Responsive Design**: Better mobile and desktop experience

## 🚀 Performance Improvements
- **Query Optimization**: Enhanced database queries for analytics
- **Caching**: Improved data caching for dashboard performance
- **Memory Usage**: Optimized memory usage for large datasets

## 🔒 Security
- **Input Validation**: Enhanced validation for session creation parameters
- **Error Handling**: Improved error messages without information disclosure
- **User Authentication**: Maintained existing security model

## 📊 Compatibility
- **Python**: 3.8+ (unchanged)
- **Database**: SQLite (unchanged)
- **Docker**: Enhanced support for containerized environments
- **CLI**: New commands with backward compatibility

## 🆘 Support
For issues or questions about this release:
- Check the documentation in the `/docs` directory
- Review the changelog for detailed change history
- Test new features in a development environment first

---

**Next Release**: Planned features and improvements will be tracked in the [Unreleased] section of CHANGELOG.md 