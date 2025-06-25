# Release Notes - Universal Time Tracker v0.2.0

**Release Date:** January 27, 2025  
**Version:** 0.2.0

## 🌟 What's New

### Historical Session Creation
- **CLI Command**: New `tt create` command for creating sessions with custom start/end times
- **API Endpoint**: New `/api/v1/sessions/create` endpoint for programmatic session creation
- **Flexible Time Formats**: Support for duration strings (e.g., "2h 30m") and specific timestamps
- **Category Support**: Assign categories to historical sessions during creation

### Enhanced Analytics Dashboard
- **Daily Variation Box Plots**: Statistical visualization showing productivity variation across weekdays
- **Interactive Charts**: Rich tooltips with detailed statistical information (min, Q1, median, Q3, max)
- **Weekly Patterns Enhancement**: Box plot overlays on existing line charts for deeper insights
- **Statistical Analysis**: Better understanding of daily productivity patterns and variations

### Session Management Improvements
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