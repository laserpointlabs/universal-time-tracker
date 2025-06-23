#!/usr/bin/env python3
"""
Universal Time Tracker Server
Flask API for centralized time tracking across projects
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
import os
import logging
from collections import defaultdict
from dateutil import parser

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Database configuration
DATABASE_PATH = os.environ.get('DATABASE_PATH', '/app/data/timetracker.db')
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DATABASE_PATH}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize database
db = SQLAlchemy(app)

# Import and create models
from models import create_models
Project, Session, Break = create_models(db)

# Create tables
with app.app_context():
    db.create_all()
    logger.info("Database tables created/verified")

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'version': '1.0.0',
        'database': 'connected' if db.engine.dialect.has_table(db.engine.connect(), 'projects') else 'disconnected'
    })

@app.route('/api/v1/projects', methods=['GET'])
def get_projects():
    """Get all projects"""
    projects = Project.query.all()
    return jsonify([{
        'id': p.id,
        'name': p.name,
        'type': p.type,
        'language': p.language,
        'framework': p.framework,
        'created_at': p.created_at.isoformat(),
        'last_activity': p.last_activity.isoformat() if p.last_activity else None
    } for p in projects])

@app.route('/api/v1/projects', methods=['POST'])
def create_or_update_project():
    """Create or update a project"""
    data = request.get_json()
    
    project_name = data.get('name')
    if not project_name:
        return jsonify({'error': 'Project name is required'}), 400
    
    # Check if project exists
    project = Project.query.filter_by(name=project_name).first()
    
    if project:
        # Update existing project
        project.type = data.get('type', project.type)
        project.language = data.get('language', project.language)
        project.framework = data.get('framework', project.framework)
        project.path = data.get('path', project.path)
        project.git_remote = data.get('git_remote', project.git_remote)
        project.last_activity = datetime.now()
    else:
        # Create new project
        project = Project(
            name=project_name,
            type=data.get('type', 'development'),
            language=data.get('language'),
            framework=data.get('framework'),
            path=data.get('path'),
            git_remote=data.get('git_remote'),
            created_at=datetime.now(),
            last_activity=datetime.now()
        )
        db.session.add(project)
    
    db.session.commit()
    logger.info(f"Project {'updated' if project.id else 'created'}: {project_name}")
    
    return jsonify({
        'id': project.id,
        'name': project.name,
        'message': 'Project created successfully' if not project.id else 'Project updated successfully'
    })

@app.route('/api/v1/sessions/start', methods=['POST'])
def start_session():
    """Start a new tracking session"""
    data = request.get_json()
    
    project_name = data.get('project')
    description = data.get('description')
    category = data.get('category', 'development')
    
    if not project_name or not description:
        return jsonify({'error': 'Project name and description are required'}), 400
    
    # Get or create project
    project = Project.query.filter_by(name=project_name).first()
    if not project:
        project = Project(
            name=project_name,
            type='development',
            created_at=datetime.now(),
            last_activity=datetime.now()
        )
        db.session.add(project)
        db.session.flush()  # Get project.id
    
    # Stop any active sessions for this project
    active_sessions = Session.query.filter_by(
        project_id=project.id,
        end_time=None
    ).all()
    
    for session in active_sessions:
        session.end_time = datetime.now()
        session.duration_minutes = int((session.end_time - session.start_time).total_seconds() / 60)
        logger.info(f"Auto-stopped session: {session.description}")
    
    # Create new session
    session = Session(
        project_id=project.id,
        start_time=datetime.now(),
        category=category,
        description=description
    )
    
    db.session.add(session)
    project.last_activity = datetime.now()
    db.session.commit()
    
    logger.info(f"Started session: {description} for project {project_name}")
    
    return jsonify({
        'session_id': session.id,
        'project': project_name,
        'description': description,
        'category': category,
        'start_time': session.start_time.isoformat(),
        'message': 'Session started successfully'
    })

@app.route('/api/v1/sessions/stop', methods=['POST'])
def stop_session():
    """Stop the active session for a project"""
    data = request.get_json()
    project_name = data.get('project')
    
    if not project_name:
        return jsonify({'error': 'Project name is required'}), 400
    
    # Find project
    project = Project.query.filter_by(name=project_name).first()
    if not project:
        return jsonify({'error': 'Project not found'}), 404
    
    # Find active session
    session = Session.query.filter_by(
        project_id=project.id,
        end_time=None
    ).first()
    
    if not session:
        return jsonify({'error': 'No active session found'}), 404
    
    # Stop session
    session.end_time = datetime.now()
    
    # Calculate duration (subtract break time)
    total_minutes = int((session.end_time - session.start_time).total_seconds() / 60)
    break_minutes = sum(b.duration_minutes or 0 for b in session.breaks if b.end_time)
    session.duration_minutes = max(0, total_minutes - break_minutes)
    
    project.last_activity = datetime.now()
    db.session.commit()
    
    logger.info(f"Stopped session: {session.description} ({session.duration_minutes} minutes)")
    
    return jsonify({
        'session_id': session.id,
        'description': session.description,
        'duration_minutes': session.duration_minutes,
        'start_time': session.start_time.isoformat(),
        'end_time': session.end_time.isoformat(),
        'message': 'Session stopped successfully'
    })

@app.route('/api/v1/sessions/break', methods=['POST'])
def toggle_break():
    """Start or end a break for the active session"""
    data = request.get_json()
    project_name = data.get('project')
    break_type = data.get('break_type', 'break')
    
    if not project_name:
        return jsonify({'error': 'Project name is required'}), 400
    
    # Find project and active session
    project = Project.query.filter_by(name=project_name).first()
    if not project:
        return jsonify({'error': 'Project not found'}), 404
    
    session = Session.query.filter_by(
        project_id=project.id,
        end_time=None
    ).first()
    
    if not session:
        return jsonify({'error': 'No active session found'}), 404
    
    # Check for active break
    active_break = Break.query.filter_by(
        session_id=session.id,
        end_time=None
    ).first()
    
    if active_break:
        # End the active break
        active_break.end_time = datetime.now()
        active_break.duration_minutes = int((active_break.end_time - active_break.start_time).total_seconds() / 60)
        
        db.session.commit()
        
        return jsonify({
            'action': 'ended',
            'break_type': active_break.break_type,
            'duration_minutes': active_break.duration_minutes,
            'message': f'Break ended: {active_break.break_type}'
        })
    else:
        # Start a new break
        new_break = Break(
            session_id=session.id,
            start_time=datetime.now(),
            break_type=break_type
        )
        
        db.session.add(new_break)
        db.session.commit()
        
        return jsonify({
            'action': 'started',
            'break_type': break_type,
            'start_time': new_break.start_time.isoformat(),
            'message': f'Break started: {break_type}'
        })

@app.route('/api/v1/sessions/status', methods=['GET'])
def get_status():
    """Get current status for a project"""
    project_name = request.args.get('project')
    
    if not project_name:
        return jsonify({'error': 'Project name is required'}), 400
    
    # Find project
    project = Project.query.filter_by(name=project_name).first()
    if not project:
        return jsonify({
            'project': project_name,
            'active_session': None,
            'active_break': None,
            'daily_summary': {'total_hours': 0, 'sessions': 0}
        })
    
    # Get active session
    active_session = Session.query.filter_by(
        project_id=project.id,
        end_time=None
    ).first()
    
    # Get active break
    active_break = None
    if active_session:
        active_break = Break.query.filter_by(
            session_id=active_session.id,
            end_time=None
        ).first()
    
    # Calculate daily summary
    today = datetime.now().date()
    today_sessions = Session.query.filter(
        Session.project_id == project.id,
        Session.start_time >= today,
        Session.start_time < today + timedelta(days=1)
    ).all()
    
    total_minutes = sum(s.duration_minutes or 0 for s in today_sessions if s.duration_minutes)
    
    return jsonify({
        'project': project_name,
        'active_session': {
            'id': active_session.id,
            'description': active_session.description,
            'category': active_session.category,
            'start_time': active_session.start_time.isoformat()
        } if active_session else None,
        'active_break': {
            'type': active_break.break_type,
            'start_time': active_break.start_time.isoformat()
        } if active_break else None,
        'daily_summary': {
            'total_hours': round(total_minutes / 60, 2),
            'sessions': len(today_sessions)
        }
    })

@app.route('/api/v1/sessions/commit', methods=['POST'])
def add_commit():
    """Add git commit to active session"""
    data = request.get_json()
    project_name = data.get('project')
    commit_hash = data.get('commit_hash')
    commit_message = data.get('commit_message')
    
    if not all([project_name, commit_hash, commit_message]):
        return jsonify({'error': 'Project, commit hash, and message are required'}), 400
    
    # Find project and active session
    project = Project.query.filter_by(name=project_name).first()
    if not project:
        return jsonify({'error': 'Project not found'}), 404
    
    session = Session.query.filter_by(
        project_id=project.id,
        end_time=None
    ).first()
    
    if not session:
        return jsonify({'error': 'No active session found'}), 404
    
    # Add commit to session
    if not session.git_commits:
        session.git_commits = []
    
    session.git_commits.append({
        'hash': commit_hash,
        'message': commit_message,
        'timestamp': datetime.now().isoformat()
    })
    
    db.session.commit()
    
    return jsonify({
        'message': 'Commit linked to session',
        'commit_hash': commit_hash[:8],
        'session_id': session.id
    })

@app.route('/api/v1/reports/<period>', methods=['GET'])
def get_report(period):
    """Generate time tracking reports"""
    project_name = request.args.get('project')
    format_type = request.args.get('format', 'json')
    
    # Date range calculation
    now = datetime.now()
    if period == 'today':
        start_date = now.date()
        end_date = start_date + timedelta(days=1)
    elif period == 'week':
        start_date = now.date() - timedelta(days=now.weekday())
        end_date = start_date + timedelta(days=7)
    elif period == 'month':
        start_date = now.date().replace(day=1)
        next_month = start_date.replace(month=start_date.month + 1) if start_date.month < 12 else start_date.replace(year=start_date.year + 1, month=1)
        end_date = next_month
    else:
        return jsonify({'error': 'Invalid period. Use: today, week, month'}), 400
    
    # Build query
    query = Session.query.filter(
        Session.start_time >= start_date,
        Session.start_time < end_date,
        Session.duration_minutes.isnot(None)
    )
    
    if project_name:
        project = Project.query.filter_by(name=project_name).first()
        if project:
            query = query.filter(Session.project_id == project.id)
    
    sessions = query.all()
    
    # Calculate summary
    total_minutes = sum(s.duration_minutes for s in sessions)
    category_breakdown = {}
    project_breakdown = {}
    
    for session in sessions:
        # Category breakdown
        cat = session.category
        category_breakdown[cat] = category_breakdown.get(cat, 0) + session.duration_minutes
        
        # Project breakdown
        proj_name = session.project.name
        project_breakdown[proj_name] = project_breakdown.get(proj_name, 0) + session.duration_minutes
    
    report_data = {
        'period': period,
        'start_date': start_date.isoformat(),
        'end_date': (end_date - timedelta(days=1)).isoformat(),
        'total_hours': round(total_minutes / 60, 2),
        'total_sessions': len(sessions),
        'category_breakdown': {k: round(v / 60, 2) for k, v in category_breakdown.items()},
        'project_breakdown': {k: round(v / 60, 2) for k, v in project_breakdown.items()},
        'sessions': [{
            'id': s.id,
            'project': s.project.name,
            'description': s.description,
            'category': s.category,
            'start_time': s.start_time.isoformat(),
            'end_time': s.end_time.isoformat() if s.end_time else None,
            'duration_minutes': s.duration_minutes
        } for s in sessions]
    }
    
    return jsonify(report_data)

# Analytics and Visualization Endpoints
@app.route('/api/v1/analytics/heatmap', methods=['GET'])
def get_activity_heatmap():
    """Get GitHub-style activity heatmap data"""
    project = request.args.get('project')
    year = request.args.get('year', datetime.now().year, type=int)
    
    if not project:
        return jsonify({'error': 'Project parameter required'}), 400
    
    try:
        # Get start and end dates for the year
        start_date = datetime(year, 1, 1)
        end_date = datetime(year, 12, 31, 23, 59, 59)
        
        # Query sessions for the year
        project_obj = Project.query.filter_by(name=project).first()
        if not project_obj:
            return jsonify({'error': 'Project not found'}), 404
        
        sessions = Session.query.filter(
            Session.project_id == project_obj.id,
            Session.start_time >= start_date,
            Session.end_time <= end_date,
            Session.end_time.isnot(None)
        ).all()
        
        # Group sessions by date and calculate daily hours
        daily_hours = defaultdict(float)
        for session in sessions:
            date_key = session.start_time.strftime('%Y-%m-%d')
            duration = (session.end_time - session.start_time).total_seconds() / 3600
            daily_hours[date_key] += duration
        
        # Generate complete year grid (52-53 weeks)
        heatmap_data = []
        current_date = start_date
        
        # Start from the first Sunday before or on January 1st
        days_back = current_date.weekday()
        if current_date.weekday() != 6:  # If not Sunday
            days_back = (current_date.weekday() + 1) % 7
        grid_start = current_date - timedelta(days=days_back)
        
        # Generate 53 weeks worth of data
        for week in range(53):
            week_data = []
            for day in range(7):  # Sunday to Saturday
                date = grid_start + timedelta(weeks=week, days=day)
                date_str = date.strftime('%Y-%m-%d');
                
                if date.year == year:
                    hours = daily_hours.get(date_str, 0);
                    # Determine intensity level (0-4 like GitHub)
                    if hours == 0:
                        level = 0
                    elif hours < 2:
                        level = 1
                    elif hours < 4:
                        level = 2
                    elif hours < 6:
                        level = 3
                    else:
                        level = 4;
                    
                    week_data.append({
                        'date': date_str,
                        'hours': round(hours, 2),
                        'level': level,
                        'day_of_week': day,
                        'month': date.month,
                        'in_year': True
                    });
                else:
                    # Outside the target year
                    week_data.append({
                        'date': date.strftime('%Y-%m-%d'),
                        'hours': 0,
                        'level': 0,
                        'day_of_week': day,
                        'month': date.month,
                        'in_year': False
                    });
            
            heatmap_data.append(week_data);
        
        # Calculate summary stats
        total_hours = sum(daily_hours.values());
        active_days = len([h for h in daily_hours.values() if h > 0]);
        avg_hours_per_active_day = total_hours / active_days if active_days > 0 else 0;
        
        return jsonify({
            'year': year,
            'project': project,
            'heatmap': heatmap_data,
            'stats': {
                'total_hours': round(total_hours, 2),
                'active_days': active_days,
                'avg_hours_per_active_day': round(avg_hours_per_active_day, 2),
                'max_daily_hours': round(max(daily_hours.values()) if daily_hours else 0, 2)
            }
        });
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/v1/analytics/category-breakdown', methods=['GET'])
def get_category_breakdown():
    """Get detailed category breakdown with trends"""
    project = request.args.get('project')
    period = request.args.get('period', 'month')  # week, month, quarter, year
    
    if not project:
        return jsonify({'error': 'Project parameter required'}), 400
    
    try:
        # Calculate date range based on period
        now = datetime.now()
        if period == 'week':
            start_date = now - timedelta(days=7)
        elif period == 'month':
            start_date = now - timedelta(days=30)
        elif period == 'quarter':
            start_date = now - timedelta(days=90)
        elif period == 'year':
            start_date = now - timedelta(days=365)
        else:
            start_date = now - timedelta(days=30)
        
        project_obj = Project.query.filter_by(name=project).first()
        if not project_obj:
            return jsonify({'error': 'Project not found'}), 404
        
        sessions = Session.query.filter(
            Session.project_id == project_obj.id,
            Session.start_time >= start_date,
            Session.end_time.isnot(None)
        ).all()
        
        # Calculate category totals and trends
        category_data = {}
        
        for session in sessions:
            category = session.category
            duration = (session.end_time - session.start_time).total_seconds() / 3600
            date_key = session.start_time.strftime('%Y-%m-%d')
            
            if category not in category_data:
                category_data[category] = {
                    'hours': 0.0,
                    'sessions': 0,
                    'daily_breakdown': {}
                }
            
            category_data[category]['hours'] += duration
            category_data[category]['sessions'] += 1
            
            if date_key not in category_data[category]['daily_breakdown']:
                category_data[category]['daily_breakdown'][date_key] = 0.0
            category_data[category]['daily_breakdown'][date_key] += duration
        
        # Format response
        breakdown = []
        total_hours = sum(data['hours'] for data in category_data.values())
        
        for category, data in category_data.items():
            percentage = (data['hours'] / total_hours * 100) if total_hours > 0 else 0;
            
            # Calculate trend (compare first half vs second half of period)
            daily_data = list(data['daily_breakdown'].values())
            mid_point = len(daily_data) // 2;
            
            if len(daily_data) >= 2:
                first_half_avg = sum(daily_data[:mid_point]) / max(mid_point, 1);
                second_half_avg = sum(daily_data[mid_point:]) / max(len(daily_data) - mid_point, 1);
                trend = 'up' if second_half_avg > first_half_avg else 'down' if second_half_avg < first_half_avg else 'stable';
            else:
                trend = 'stable';
            
            breakdown.append({
                'category': category,
                'hours': round(data['hours'], 2),
                'sessions': data['sessions'],
                'percentage': round(percentage, 1),
                'avg_session_duration': round(data['hours'] / data['sessions'], 2) if data['sessions'] > 0 else 0,
                'trend': trend,
                'daily_breakdown': dict(data['daily_breakdown'])
            })
        
        # Sort by hours descending
        breakdown.sort(key=lambda x: x['hours'], reverse=True)
        
        return jsonify({
            'period': period,
            'project': project,
            'total_hours': round(total_hours, 2),
            'categories': breakdown
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/v1/analytics/productivity-trends', methods=['GET'])
def get_productivity_trends():
    """Get productivity trends and patterns"""
    project = request.args.get('project')
    days = request.args.get('days', 30, type=int)
    
    if not project:
        return jsonify({'error': 'Project parameter required'}), 400
    
    try:
        start_date = datetime.now() - timedelta(days=days)
        
        project_obj = Project.query.filter_by(name=project).first()
        if not project_obj:
            return jsonify({'error': 'Project not found'}), 400
        
        sessions = Session.query.filter(
            Session.project_id == project_obj.id,
            Session.start_time >= start_date,
            Session.end_time.isnot(None)
        ).all()
        
        # Daily productivity data
        daily_data = {}
        hourly_data = defaultdict(float)  # Hour of day analysis
        weekday_data = defaultdict(float)  # Day of week analysis
        
        for session in sessions:
            date_key = session.start_time.strftime('%Y-%m-%d')
            hour_key = session.start_time.hour
            weekday_key = session.start_time.strftime('%A')
            
            duration = (session.end_time - session.start_time).total_seconds() / 3600
            
            if date_key not in daily_data:
                daily_data[date_key] = {
                    'hours': 0.0,
                    'sessions': 0,
                    'categories': set()
                }
            
            daily_data[date_key]['hours'] += duration
            daily_data[date_key]['sessions'] += 1
            daily_data[date_key]['categories'].add(session.category)
            
            hourly_data[hour_key] += duration
            weekday_data[weekday_key] += duration
        
        # Calculate trends and insights
        daily_hours = [data['hours'] for data in daily_data.values()]
        avg_daily_hours = sum(daily_hours) / len(daily_hours) if daily_hours else 0
        
        # Find most productive time patterns
        best_hour = max(hourly_data.items(), key=lambda x: x[1]) if hourly_data else (9, 0)
        best_weekday = max(weekday_data.items(), key=lambda x: x[1]) if weekday_data else ('Monday', 0)
        
        # Calculate productivity insights
        insights = []
        if avg_daily_hours > 4:
            insights.append("High productivity - averaging over 4 hours per day")
        elif avg_daily_hours > 2:
            insights.append("Moderate productivity - good daily engagement")
        else:
            insights.append("Consider increasing daily coding time")
        
        if best_hour[1] > 0:
            insights.append(f"Most productive at {best_hour[0]:02d}:00 - {best_hour[0]+1:02d}:00")
        
        if best_weekday[1] > 0:
            insights.append(f"Most productive on {best_weekday[0]}s")
        
        return jsonify({
            'project': project,
            'period_days': days,
            'daily_breakdown': {
                date: {
                    'hours': round(data['hours'], 2),
                    'sessions': data['sessions'],
                    'categories': list(data['categories'])
                } for date, data in daily_data.items()
            },
            'hourly_breakdown': {str(hour): round(hours, 2) for hour, hours in hourly_data.items()},
            'weekday_breakdown': {day: round(hours, 2) for day, hours in weekday_data.items()},
            'insights': insights,
            'stats': {
                'avg_daily_hours': round(avg_daily_hours, 2),
                'total_sessions': len(sessions),
                'best_hour': best_hour[0],
                'best_weekday': best_weekday[0]
            }
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/v1/analytics/session-patterns', methods=['GET'])
def get_session_patterns():
    """Analyze session patterns and provide recommendations"""
    project = request.args.get('project')
    days = request.args.get('days', 30, type=int)
    
    if not project:
        return jsonify({'error': 'Project parameter required'}), 400
    
    try:
        start_date = datetime.now() - timedelta(days=days)
        
        project_obj = Project.query.filter_by(name=project).first()
        if not project_obj:
            return jsonify({'error': 'Project not found'}), 400
        
        sessions = Session.query.filter(
            Session.project_id == project_obj.id,
            Session.start_time >= start_date,
            Session.end_time.isnot(None)
        ).all()
        
        if not sessions:
            return jsonify({
                'project': project,
                'session_lengths': [],
                'break_analysis': {},
                'recommendations': ['Start tracking sessions to see patterns!']
            })
        
        # Analyze session lengths
        session_durations = []
        break_data = []
        
        for session in sessions:
            duration_hours = (session.end_time - session.start_time).total_seconds() / 3600
            session_durations.append(duration_hours)
            
            # Get breaks for this session
            breaks = Break.query.filter_by(session_id=session.id).all()
            for break_obj in breaks:
                if break_obj.end_time:
                    break_duration = (break_obj.end_time - break_obj.start_time).total_seconds() / 60
                    break_data.append({
                        'type': break_obj.break_type,
                        'duration_minutes': break_duration
                    })
        
        # Calculate statistics
        avg_session_length = sum(session_durations) / len(session_durations)
        short_sessions = len([d for d in session_durations if d < 0.5])  # < 30 minutes
        long_sessions = len([d for d in session_durations if d > 3])     # > 3 hours
        
        # Break analysis
        break_types = {}
        total_break_time = 0
        for break_item in break_data:
            break_type = break_item['type']
            duration = break_item['duration_minutes']
            
            if break_type not in break_types:
                break_types[break_type] = {'count': 0, 'total_minutes': 0}
            
            break_types[break_type]['count'] += 1
            break_types[break_type]['total_minutes'] += duration
            total_break_time += duration
        
        # Generate recommendations
        recommendations = []
        
        if avg_session_length < 1:
            recommendations.append("Consider longer coding sessions for better flow state")
        elif avg_session_length > 4:
            recommendations.append("Consider taking more breaks during long sessions")
        
        if short_sessions > len(sessions) * 0.3:
            recommendations.append(f"You have {short_sessions} short sessions - try to minimize context switching")
        
        if long_sessions > 0:
            recommendations.append("Great job on sustained focus! Remember to take breaks every 90-120 minutes")
        
        if total_break_time < len(sessions) * 10:
            recommendations.append("Consider taking more breaks to maintain productivity")
        
        break_ratio = total_break_time / (sum(session_durations) * 60) if session_durations else 0
        if break_ratio > 0.3:
            recommendations.append("High break-to-work ratio - consider optimizing your work environment")
        
        return jsonify({
            'project': project,
            'period_days': days,
            'session_lengths': {
                'average_hours': round(avg_session_length, 2),
                'shortest_hours': round(min(session_durations), 2) if session_durations else 0,
                'longest_hours': round(max(session_durations), 2) if session_durations else 0,
                'distribution': {
                    'short_sessions': short_sessions,
                    'medium_sessions': len(session_durations) - short_sessions - long_sessions,
                    'long_sessions': long_sessions
                }
            },
            'break_analysis': {
                'total_break_minutes': round(total_break_time, 2),
                'break_types': {
                    break_type: {
                        'count': data['count'],
                        'avg_duration': round(data['total_minutes'] / data['count'], 2)
                    } for break_type, data in break_types.items()
                },
                'break_to_work_ratio': round(break_ratio, 3)
            },
            'recommendations': recommendations
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/dashboard')
def dashboard():
    """Serve interactive analytics dashboard"""
    html_content = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Time Tracker Analytics Dashboard</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        
        .container {
            max-width: 1400px;
            margin: 0 auto;
        }
        
        .header {
            text-align: center;
            color: white;
            margin-bottom: 30px;
        }
        
        .header h1 {
            font-size: 2.5rem;
            margin-bottom: 10px;
        }
        
        .controls {
            background: rgba(255, 255, 255, 0.1);
            padding: 20px;
            border-radius: 15px;
            margin-bottom: 30px;
            backdrop-filter: blur(10px);
        }
        
        .controls input, .controls select, .controls button {
            padding: 10px 15px;
            margin: 5px;
            border: none;
            border-radius: 8px;
            font-size: 14px;
        }
        
        .controls button {
            background: #4CAF50;
            color: white;
            cursor: pointer;
            transition: background 0.3s;
        }
        
        .controls button:hover {
            background: #45a049;
        }
        
        .dashboard-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
            gap: 20px;
            margin-bottom: 20px;
        }
        
        .card {
            background: rgba(255, 255, 255, 0.95);
            padding: 25px;
            border-radius: 15px;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
            backdrop-filter: blur(10px);
        }
        
        .card h3 {
            color: #333;
            margin-bottom: 20px;
            font-size: 1.3rem;
        }
        
        .heatmap-container {
            grid-column: 1 / -1;
        }
        
        .heatmap {
            display: grid;
            grid-template-columns: repeat(53, 1fr);
            gap: 2px;
            margin: 20px 0;
        }
        
        .heatmap-week {
            display: grid;
            grid-template-rows: repeat(7, 1fr);
            gap: 2px;
        }
        
        .heatmap-day {
            width: 12px;
            height: 12px;
            border-radius: 2px;
            cursor: pointer;
            transition: all 0.2s;
        }
        
        .heatmap-day:hover {
            transform: scale(1.3);
            border: 2px solid #333;
        }
        
        .level-0 { background-color: #ebedf0; }
        .level-1 { background-color: #c6e48b; }
        .level-2 { background-color: #7bc96f; }
        .level-3 { background-color: #239a3b; }
        .level-4 { background-color: #196127; }
        
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin: 20px 0;
        }
        
        .stat-item {
            text-align: center;
            padding: 15px;
            background: rgba(0, 0, 0, 0.05);
            border-radius: 8px;
        }
        
        .stat-value {
            font-size: 2rem;
            font-weight: bold;
            color: #4CAF50;
        }
        
        .stat-label {
            color: #666;
            margin-top: 5px;
        }
        
        .error {
            color: #f44336;
            background: rgba(244, 67, 54, 0.1);
            padding: 15px;
            border-radius: 8px;
            margin: 10px 0;
        }
        
        .loading {
            text-align: center;
            color: #666;
            padding: 40px;
        }
        
        .chart-container {
            position: relative;
            height: 300px;
            margin-top: 20px;
        }
        
        .recommendations {
            background: rgba(76, 175, 80, 0.1);
            border-left: 4px solid #4CAF50;
            padding: 15px;
            margin: 15px 0;
            border-radius: 0 8px 8px 0;
        }
        
        .recommendations h4 {
            margin-bottom: 10px;
            color: #4CAF50;
        }
        
        .recommendations ul {
            list-style-position: inside;
            color: #333;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📊 Time Tracker Analytics</h1>
            <p>Visualize your coding patterns and productivity insights</p>
        </div>
        
        <div class="controls">
            <select id="projectSelect" onchange="loadDashboard()">
                <option value="">Select a project...</option>
            </select>
            <select id="yearSelect" onchange="loadDashboard()">
                <option value="2024">2024</option>
                <option value="2023">2023</option>
                <option value="2025">2025</option>
            </select>
            <button onclick="loadDashboard()">Load Analytics</button>
            <button onclick="refreshData()">Refresh</button>
        </div>
        
        <div id="dashboardContent">
            <div class="loading">Select a project and click "Load Analytics" to get started!</div>
        </div>
    </div>

    <script>
        let currentProject = '';
        let currentYear = new Date().getFullYear();
        
        function loadDashboard() {
            currentProject = document.getElementById('projectSelect').value.trim();
            currentYear = document.getElementById('yearSelect').value;
            
            if (!currentProject) {
                document.getElementById('dashboardContent').innerHTML = 
                    '<div class="loading">Please select a project to view analytics</div>';
                return;
            }
            
            document.getElementById('dashboardContent').innerHTML = '<div class="loading">Loading analytics...</div>';
            
            Promise.all([
                fetchHeatmap(),
                fetchCategoryBreakdown(),
                fetchProductivityTrends(),
                fetchSessionPatterns()
            ]).then(([heatmap, categories, trends, patterns]) => {
                renderDashboard(heatmap, categories, trends, patterns);
            }).catch(error => {
                document.getElementById('dashboardContent').innerHTML = 
                    `<div class="error">Error loading data: ${error.message}</div>`;
            });
        }
        
        function refreshData() {
            if (currentProject) {
                loadDashboard();
            }
        }
        
        async function fetchHeatmap() {
            const response = await fetch(`/api/v1/analytics/heatmap?project=${encodeURIComponent(currentProject)}&year=${currentYear}`);
            if (!response.ok) throw new Error('Failed to fetch heatmap data');
            return response.json();
        }
        
        async function fetchCategoryBreakdown() {
            const response = await fetch(`/api/v1/analytics/category-breakdown?project=${encodeURIComponent(currentProject)}&period=month`);
            if (!response.ok) throw new Error('Failed to fetch category data');
            return response.json();
        }
        
        async function fetchProductivityTrends() {
            const response = await fetch(`/api/v1/analytics/productivity-trends?project=${encodeURIComponent(currentProject)}&days=30`);
            if (!response.ok) throw new Error('Failed to fetch productivity data');
            return response.json();
        }
        
        async function fetchSessionPatterns() {
            const response = await fetch(`/api/v1/analytics/session-patterns?project=${encodeURIComponent(currentProject)}&days=30`);
            if (!response.ok) throw new Error('Failed to fetch session data');
            return response.json();
        }
        
        async function loadProjects() {
            try {
                const response = await fetch('/api/v1/projects');
                if (!response.ok) throw new Error('Failed to fetch projects');
                const projects = await response.json();
                
                const projectSelect = document.getElementById('projectSelect');
                
                // Clear existing options except the first one
                while (projectSelect.children.length > 1) {
                    projectSelect.removeChild(projectSelect.lastChild);
                }
                
                // Add project options
                projects.forEach(project => {
                    const option = document.createElement('option');
                    option.value = project.name;
                    option.textContent = project.name;
                    projectSelect.appendChild(option);
                });
                
                // Auto-select the first project if available
                if (projects.length > 0) {
                    projectSelect.value = projects[0].name;
                }
            } catch (error) {
                console.error('Error loading projects:', error);
                // Show error in dropdown
                const projectSelect = document.getElementById('projectSelect');
                const option = document.createElement('option');
                option.value = '';
                option.textContent = 'Error loading projects';
                option.disabled = true;
                projectSelect.appendChild(option);
            }
        }
        
        function renderDashboard(heatmap, categories, trends, patterns) {
            const content = `
                <div class="dashboard-grid">
                    <div class="card heatmap-container">
                        <h3>🔥 Activity Heatmap (${currentYear})</h3>
                        <div class="stats-grid">
                            <div class="stat-item">
                                <div class="stat-value">${heatmap.stats.total_hours}</div>
                                <div class="stat-label">Total Hours</div>
                            </div>
                            <div class="stat-item">
                                <div class="stat-value">${heatmap.stats.active_days}</div>
                                <div class="stat-label">Active Days</div>
                            </div>
                            <div class="stat-item">
                                <div class="stat-value">${heatmap.stats.avg_hours_per_active_day}</div>
                                <div class="stat-label">Avg Hours/Day</div>
                            </div>
                            <div class="stat-item">
                                <div class="stat-value">${heatmap.stats.max_daily_hours}</div>
                                <div class="stat-label">Best Day</div>
                            </div>
                        </div>
                        ${renderHeatmap(heatmap.heatmap)}
                    </div>
                    
                    <div class="card">
                        <h3>📊 Category Breakdown</h3>
                        <div class="chart-container">
                            <canvas id="categoryChart"></canvas>
                        </div>
                    </div>
                    
                    <div class="card">
                        <h3>📈 Hourly Productivity</h3>
                        <div class="chart-container">
                            <canvas id="hourlyChart"></canvas>
                        </div>
                    </div>
                    
                    <div class="card">
                        <h3>📅 Weekly Patterns</h3>
                        <div class="chart-container">
                            <canvas id="weeklyChart"></canvas>
                        </div>
                    </div>
                    
                    <div class="card">
                        <h3>⏱️ Session Analysis</h3>
                        <div class="stats-grid">
                            <div class="stat-item">
                                <div class="stat-value">${patterns.session_lengths.average_hours}</div>
                                <div class="stat-label">Avg Session</div>
                            </div>
                            <div class="stat-item">
                                <div class="stat-value">${patterns.session_lengths.distribution.long_sessions}</div>
                                <div class="stat-label">Long Sessions</div>
                            </div>
                            <div class="stat-item">
                                <div class="stat-value">${patterns.break_analysis.total_break_minutes}</div>
                                <div class="stat-label">Break Minutes</div>
                            </div>
                            <div class="stat-item">
                                <div class="stat-value">${Math.round(patterns.break_analysis.break_to_work_ratio * 100)}%</div>
                                <div class="stat-label">Break Ratio</div>
                            </div>
                        </div>
                        ${renderRecommendations(patterns.recommendations)}
                    </div>
                </div>
            `;
            
            document.getElementById('dashboardContent').innerHTML = content;
            
            // Render charts
            renderCategoryChart(categories);
            renderHourlyChart(trends);
            renderWeeklyChart(trends);
        }
        
        function renderHeatmap(heatmapData) {
            const heatmapHtml = heatmapData.map(week => {
                const weekHtml = week.map(day => 
                    `<div class="heatmap-day level-${day.level}" 
                          title="${day.date}: ${day.hours} hours"
                          style="opacity: ${day.in_year ? 1 : 0.3}"></div>`
                ).join('');
                return `<div class="heatmap-week">${weekHtml}</div>`;
            }).join('');
            
            return `<div class="heatmap">${heatmapHtml}</div>`;
        }
        
        function renderRecommendations(recommendations) {
            const recHtml = recommendations.map(rec => `<li>${rec}</li>`).join('');
            return `
                <div class="recommendations">
                    <h4>💡 Recommendations</h4>
                    <ul>${recHtml}</ul>
                </div>
            `;
        }
        
        function renderCategoryChart(categories) {
            const ctx = document.getElementById('categoryChart').getContext('2d');
            new Chart(ctx, {
                type: 'doughnut',
                data: {
                    labels: categories.categories.map(c => c.category),
                    datasets: [{
                        data: categories.categories.map(c => c.hours),
                        backgroundColor: [
                            '#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0', 
                            '#9966FF', '#FF9F40', '#FF6384', '#C9CBCF'
                        ]
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            position: 'bottom'
                        }
                    }
                }
            });
        }
        
        function renderHourlyChart(trends) {
            const ctx = document.getElementById('hourlyChart').getContext('2d');
            const hourlyData = trends.hourly_breakdown;
            const hours = Array.from({length: 24}, (_, i) => i);
            const values = hours.map(h => hourlyData[h] || 0);
            
            new Chart(ctx, {
                type: 'bar',
                data: {
                    labels: hours.map(h => `${h}:00`),
                    datasets: [{
                        label: 'Hours Worked',
                        data: values,
                        backgroundColor: 'rgba(54, 162, 235, 0.8)',
                        borderColor: 'rgba(54, 162, 235, 1)',
                        borderWidth: 1
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {
                        y: {
                            beginAtZero: true
                        }
                    }
                }
            });
        }
        
        function renderWeeklyChart(trends) {
            const ctx = document.getElementById('weeklyChart').getContext('2d');
            const weeklyData = trends.weekday_breakdown;
            const days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'];
            const values = days.map(day => weeklyData[day] || 0);
            
            new Chart(ctx, {
                type: 'line',
                data: {
                    labels: days,
                    datasets: [{
                        label: 'Hours Worked',
                        data: values,
                        borderColor: 'rgba(75, 192, 192, 1)',
                        backgroundColor: 'rgba(75, 192, 192, 0.2)',
                        fill: true,
                        tension: 0.4
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {
                        y: {
                            beginAtZero: true
                        }
                    }
                }
            });
        }
        
        // Set current year as default
        document.getElementById('yearSelect').value = currentYear;
        
        // Load projects when page loads
        document.addEventListener('DOMContentLoaded', function() {
            loadProjects();
        });
        
        // Also load projects immediately since the script runs after DOM is loaded
        loadProjects();
    </script>
</body>
</html>
    """
    return html_content

if __name__ == '__main__':
    # Ensure data directory exists
    os.makedirs(os.path.dirname(DATABASE_PATH), exist_ok=True)
    
    # Start the server
    port = int(os.environ.get('PORT', 9000))
    logger.info(f"Starting Time Tracker Server on port {port}")
    app.run(host='0.0.0.0', port=port, debug=True)
       