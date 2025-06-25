#!/usr/bin/env python3
"""
Universal Time Tracker Server
Flask API for centralized time tracking across projects
"""

from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
import os
import logging
from collections import defaultdict
from dateutil import parser
import sqlite3
import yaml
from openai import OpenAI

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Set secret key for sessions (required for flash messages)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')

# Database configuration
DATABASE_PATH = os.environ.get('DATABASE_PATH', '/app/data/timetracker.db')
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DATABASE_PATH}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize database
db = SQLAlchemy(app)

# Import and create models
from models import create_models
Project, Session, Break = create_models(db)

# Import database browser
from db_browser import db_browser

# Register blueprints
app.register_blueprint(db_browser)

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
        project.userid = os.getlogin()
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
            last_activity=datetime.now(),
            userid=os.getlogin()
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
            last_activity=datetime.now(),
            userid=os.getlogin()
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
        description=description,
        userid=os.getlogin()
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
            break_type=break_type,
            userid=os.getlogin()
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

@app.route('/api/v1/analytics/ai-recommendations', methods=['GET'])
def get_ai_recommendations():
    """Get AI-powered recommendations based on time tracking data"""
    project = request.args.get('project')
    days = request.args.get('days', 30, type=int)
    
    if not project:
        return jsonify({'error': 'Project parameter required'}), 400
    
    # Check if OpenAI API key is configured
    openai_api_key = os.environ.get('OPENAI_API_KEY')
    if not openai_api_key:
        return jsonify({
            'error': 'OpenAI API key not configured. Set OPENAI_API_KEY environment variable.',
            'recommendations': [
                "Configure OpenAI API key to get AI-powered recommendations",
                "Focus on maintaining consistent daily work hours",
                "Take regular breaks every 90-120 minutes",
                "Schedule important tasks during your peak productivity hours"
            ]
        }), 200
    
    try:
        start_date = datetime.now() - timedelta(days=days)
        
        project_obj = Project.query.filter_by(name=project).first()
        if not project_obj:
            return jsonify({'error': 'Project not found'}), 404
        
        # Get comprehensive data for analysis
        sessions = Session.query.filter(
            Session.project_id == project_obj.id,
            Session.start_time >= start_date,
            Session.end_time.isnot(None)
        ).all()
        
        if not sessions:
            return jsonify({
                'project': project,
                'recommendations': ['Start tracking sessions to get personalized recommendations!'],
                'insights': 'No data available for analysis'
            })
        
        # Collect detailed analytics data
        analytics_data = {
            'project': project,
            'period_days': days,
            'total_sessions': len(sessions),
            'total_hours': 0,
            'daily_patterns': {},
            'hourly_patterns': defaultdict(float),
            'category_breakdown': defaultdict(float),
            'session_lengths': [],
            'break_data': [],
            'work_consistency': {},
            'productivity_metrics': {}
        }
        
        # Analyze sessions
        for session in sessions:
            duration_hours = (session.end_time - session.start_time).total_seconds() / 3600
            analytics_data['total_hours'] += duration_hours
            analytics_data['session_lengths'].append(duration_hours)
            
            # Daily patterns
            date_key = session.start_time.strftime('%Y-%m-%d')
            if date_key not in analytics_data['daily_patterns']:
                analytics_data['daily_patterns'][date_key] = {
                    'hours': 0,
                    'sessions': 0,
                    'categories': set()
                }
            analytics_data['daily_patterns'][date_key]['hours'] += duration_hours
            analytics_data['daily_patterns'][date_key]['sessions'] += 1
            analytics_data['daily_patterns'][date_key]['categories'].add(session.category)
            
            # Hourly patterns
            hour_key = session.start_time.hour
            analytics_data['hourly_patterns'][hour_key] += duration_hours
            
            # Category breakdown
            analytics_data['category_breakdown'][session.category] += duration_hours
            
            # Get breaks for this session
            breaks = Break.query.filter_by(session_id=session.id).all()
            for break_obj in breaks:
                if break_obj.end_time:
                    break_duration = (break_obj.end_time - break_obj.start_time).total_seconds() / 60
                    analytics_data['break_data'].append({
                        'type': break_obj.break_type,
                        'duration_minutes': break_duration
                    })
        
        # Calculate additional metrics
        daily_hours = [data['hours'] for data in analytics_data['daily_patterns'].values()]
        analytics_data['productivity_metrics'] = {
            'avg_daily_hours': sum(daily_hours) / len(daily_hours) if daily_hours else 0,
            'avg_session_length': sum(analytics_data['session_lengths']) / len(analytics_data['session_lengths']),
            'total_break_minutes': sum(b['duration_minutes'] for b in analytics_data['break_data']),
            'most_productive_hour': max(analytics_data['hourly_patterns'].items(), key=lambda x: x[1])[0] if analytics_data['hourly_patterns'] else 9,
            'work_days': len(analytics_data['daily_patterns']),
            'consistency_score': len([h for h in daily_hours if 2 <= h <= 8]) / len(daily_hours) if daily_hours else 0
        }
        
        # Load custom prompt or use default
        prompt_file_path = '/app/prompts/ai_recommendations.txt'
        try:
            with open(prompt_file_path, 'r', encoding='utf-8') as f:
                prompt_template = f.read()
        except FileNotFoundError:
            # Use default prompt if file doesn't exist
            prompt_template = """You are a productivity expert analyzing time tracking data for a software developer. 
Provide 5-7 specific, actionable recommendations based on this data:

PROJECT: {project}
ANALYSIS PERIOD: {days} days

KEY METRICS:
- Total Hours: {total_hours:.1f} hours
- Total Sessions: {total_sessions}
- Average Daily Hours: {avg_daily_hours:.1f}
- Average Session Length: {avg_session_length:.1f} hours
- Work Days: {work_days} out of {days}
- Consistency Score: {consistency_score:.1%}

TIME DISTRIBUTION:
{category_breakdown}

PRODUCTIVITY PATTERNS:
- Most Productive Hour: {most_productive_hour}:00
- Total Break Time: {total_break_minutes:.0f} minutes
- Break-to-Work Ratio: {break_ratio:.1f}%

SESSION ANALYSIS:
- Short sessions (<30 min): {short_sessions}
- Medium sessions (30 min - 3 hours): {medium_sessions}
- Long sessions (>3 hours): {long_sessions}

DAILY PATTERNS:
{weekly_patterns}

Provide recommendations that are:
1. Specific and actionable
2. Based on the data patterns shown
3. Focused on productivity, work-life balance, and sustainable work habits
4. Tailored to software development work
5. Include both immediate improvements and long-term strategies
6. Consider the developer's specific work patterns and goals

Format as a JSON array of recommendation strings, each recommendation should be concise but specific."""

        # Prepare data for prompt template
        short_sessions = len([s for s in analytics_data['session_lengths'] if s < 0.5])
        medium_sessions = len([s for s in analytics_data['session_lengths'] if 0.5 <= s <= 3])
        long_sessions = len([s for s in analytics_data['session_lengths'] if s > 3])
        break_ratio = (analytics_data['productivity_metrics']['total_break_minutes'] / (analytics_data['total_hours'] * 60) * 100) if analytics_data['total_hours'] > 0 else 0
        
        # Weekly patterns
        weekday_data = defaultdict(float)
        for session in sessions:
            weekday = session.start_time.strftime('%A')
            duration_hours = (session.end_time - session.start_time).total_seconds() / 3600
            weekday_data[weekday] += duration_hours
        
        weekly_patterns = '\n'.join([f"- {day}: {hours:.1f} hours" for day, hours in weekday_data.items()])
        category_breakdown = '\n'.join([f"- {cat}: {hours:.1f} hours" for cat, hours in analytics_data['category_breakdown'].items()])
        
        # Format the prompt with actual data
        analysis_prompt = prompt_template.format(
            project=project,
            days=days,
            total_hours=analytics_data['total_hours'],
            total_sessions=analytics_data['total_sessions'],
            avg_daily_hours=analytics_data['productivity_metrics']['avg_daily_hours'],
            avg_session_length=analytics_data['productivity_metrics']['avg_session_length'],
            work_days=analytics_data['productivity_metrics']['work_days'],
            consistency_score=analytics_data['productivity_metrics']['consistency_score'],
            category_breakdown=category_breakdown,
            most_productive_hour=analytics_data['productivity_metrics']['most_productive_hour'],
            total_break_minutes=analytics_data['productivity_metrics']['total_break_minutes'],
            break_ratio=break_ratio,
            short_sessions=short_sessions,
            medium_sessions=medium_sessions,
            long_sessions=long_sessions,
            weekly_patterns=weekly_patterns
        )

        # Call OpenAI API
        client = OpenAI(api_key=openai_api_key)
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": "You are a productivity expert specializing in software development workflows. Provide concise, actionable recommendations based on time tracking data."
                },
                {
                    "role": "user",
                    "content": analysis_prompt
                }
            ],
            max_tokens=500,
            temperature=0.7
        )
        
        # Parse recommendations from OpenAI response
        ai_response = response.choices[0].message.content.strip()
        
        # Try to extract JSON array, fallback to parsing text
        try:
            import json
            recommendations = json.loads(ai_response)
        except:
            # Fallback: split by lines and clean up
            recommendations = [line.strip().lstrip('- ').lstrip('* ').lstrip('1. ').lstrip('2. ').lstrip('3. ').lstrip('4. ').lstrip('5. ').lstrip('6. ').lstrip('7. ') 
                             for line in ai_response.split('\n') 
                             if line.strip() and not line.strip().startswith('{') and not line.strip().startswith('}')]
            recommendations = [rec for rec in recommendations if len(rec) > 10]  # Filter out short lines
        
        return jsonify({
            'project': project,
            'period_days': days,
            'recommendations': recommendations[:7],  # Limit to 7 recommendations
            'insights': {
                'total_hours': round(analytics_data['total_hours'], 2),
                'avg_daily_hours': round(analytics_data['productivity_metrics']['avg_daily_hours'], 2),
                'consistency_score': round(analytics_data['productivity_metrics']['consistency_score'] * 100, 1),
                'most_productive_hour': analytics_data['productivity_metrics']['most_productive_hour'],
                'work_days': analytics_data['productivity_metrics']['work_days']
            },
            'data_summary': {
                'sessions_analyzed': len(sessions),
                'categories_tracked': len(analytics_data['category_breakdown']),
                'break_sessions': len(analytics_data['break_data'])
            }
        })
        
    except Exception as e:
        logger.error(f"Error generating AI recommendations: {str(e)}")
        return jsonify({
            'error': 'Failed to generate AI recommendations',
            'recommendations': [
                "Focus on maintaining consistent daily work hours",
                "Take regular breaks every 90-120 minutes",
                "Schedule important tasks during your peak productivity hours",
                "Track your time consistently to get better insights"
            ]
        }), 500

# Prompt Management Endpoints
@app.route('/api/v1/prompts/ai-recommendations', methods=['GET'])
def get_ai_prompt():
    """Get the current AI recommendations prompt"""
    try:
        # Use container path for Docker environment
        prompt_file_path = '/app/prompts/ai_recommendations.txt'
        with open(prompt_file_path, 'r', encoding='utf-8') as f:
            prompt = f.read()
        return jsonify({'prompt': prompt})
    except FileNotFoundError:
        return jsonify({'error': 'Prompt file not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/v1/prompts/ai-recommendations', methods=['POST'])
def update_ai_prompt():
    """Update the AI recommendations prompt"""
    try:
        data = request.get_json()
        if not data or 'prompt' not in data:
            return jsonify({'error': 'Prompt content required'}), 400
        
        prompt_file_path = '/app/prompts/ai_recommendations.txt'
        
        # Ensure prompts directory exists
        os.makedirs(os.path.dirname(prompt_file_path), exist_ok=True)
        
        with open(prompt_file_path, 'w', encoding='utf-8') as f:
            f.write(data['prompt'])
        
        return jsonify({'message': 'Prompt updated successfully'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/v1/prompts/ai-recommendations/reset', methods=['POST'])
def reset_ai_prompt():
    """Reset the AI recommendations prompt to default"""
    try:
        default_prompt = """You are a productivity expert analyzing time tracking data for a software developer. 
Provide 5-7 specific, actionable recommendations based on this data:

PROJECT: {project}
ANALYSIS PERIOD: {days} days

KEY METRICS:
- Total Hours: {total_hours:.1f} hours
- Total Sessions: {total_sessions}
- Average Daily Hours: {avg_daily_hours:.1f}
- Average Session Length: {avg_session_length:.1f} hours
- Work Days: {work_days} out of {days}
- Consistency Score: {consistency_score:.1%}

TIME DISTRIBUTION:
{category_breakdown}

PRODUCTIVITY PATTERNS:
- Most Productive Hour: {most_productive_hour}:00
- Total Break Time: {total_break_minutes:.0f} minutes
- Break-to-Work Ratio: {break_ratio:.1f}%

SESSION ANALYSIS:
- Short sessions (<30 min): {short_sessions}
- Medium sessions (30 min - 3 hours): {medium_sessions}
- Long sessions (>3 hours): {long_sessions}

DAILY PATTERNS:
{weekly_patterns}

Provide recommendations that are:
1. Specific and actionable
2. Based on the data patterns shown
3. Focused on productivity, work-life balance, and sustainable work habits
4. Tailored to software development work
5. Include both immediate improvements and long-term strategies
6. Consider the developer's specific work patterns and goals

Format as a JSON array of recommendation strings, each recommendation should be concise but specific."""
        
        prompt_file_path = '/app/prompts/ai_recommendations.txt'
        
        # Ensure prompts directory exists
        os.makedirs(os.path.dirname(prompt_file_path), exist_ok=True)
        
        with open(prompt_file_path, 'w', encoding='utf-8') as f:
            f.write(default_prompt)
        
        return jsonify({'message': 'Prompt reset to default'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/v1/prompts/ai-recommendations/test', methods=['POST'])
def test_ai_prompt():
    """Test the AI recommendations prompt with sample data"""
    try:
        data = request.get_json()
        if not data or 'prompt' not in data:
            return jsonify({'error': 'Prompt content required'}), 400
        
        # Sample data for testing
        sample_data = {
            'project': 'Sample Project',
            'days': 30,
            'total_hours': 120.5,
            'total_sessions': 45,
            'avg_daily_hours': 4.0,
            'avg_session_length': 2.7,
            'work_days': 25,
            'consistency_score': 0.83,
            'category_breakdown': '- Development: 85.2 hours\n- Testing: 20.1 hours\n- Planning: 15.2 hours',
            'most_productive_hour': 10,
            'total_break_minutes': 180,
            'break_ratio': 2.5,
            'short_sessions': 8,
            'medium_sessions': 25,
            'long_sessions': 12,
            'weekly_patterns': '- Monday: 6.2 hours\n- Tuesday: 5.8 hours\n- Wednesday: 7.1 hours\n- Thursday: 6.5 hours\n- Friday: 4.9 hours'
        }
        
        # Format the prompt with sample data
        formatted_prompt = data['prompt'].format(**sample_data)
        
        return jsonify({
            'message': 'Prompt test completed',
            'formatted_prompt': formatted_prompt,
            'sample_data': sample_data
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/prompt-editor')
def prompt_editor():
    """Serve the AI prompt editor page"""
    return render_template('prompt_editor.html')

@app.route('/dashboard')
def dashboard():
    """Serve interactive analytics dashboard"""
    return render_template('dashboard.html')

@app.route('/')
def landing_page():
    return render_template('index.html', year=datetime.now().year)

if __name__ == '__main__':
    # Ensure data directory exists
    os.makedirs(os.path.dirname(DATABASE_PATH), exist_ok=True)
    
    # Start the server
    port = int(os.environ.get('PORT', 9000))
    logger.info(f"Starting Time Tracker Server on port {port}")
    app.run(host='0.0.0.0', port=port, debug=True)
       