#!/usr/bin/env python3
"""
Simple Database Browser for Universal Time Tracker
Provides web-based database viewing and editing capabilities
"""

from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash, Response
from datetime import datetime, timedelta
import json
import sqlite3
import os

db_browser = Blueprint('db_browser', __name__)

def get_db_connection():
    """Get database connection"""
    database_path = os.environ.get('DATABASE_PATH', '/app/data/timetracker.db')
    conn = sqlite3.connect(database_path)
    conn.row_factory = sqlite3.Row
    return conn

@db_browser.route('/db')
def index():
    """Main database browser page"""
    conn = get_db_connection()
    
    # Get basic stats
    stats = {}
    stats['projects'] = conn.execute('SELECT COUNT(*) as count FROM projects').fetchone()['count']
    stats['sessions'] = conn.execute('SELECT COUNT(*) as count FROM sessions').fetchone()['count']
    stats['breaks'] = conn.execute('SELECT COUNT(*) as count FROM breaks').fetchone()['count']
    stats['active_sessions'] = conn.execute('SELECT COUNT(*) as count FROM sessions WHERE end_time IS NULL').fetchone()['count']
    
    # Get total duration
    result = conn.execute('SELECT SUM(duration_minutes) as total FROM sessions WHERE duration_minutes IS NOT NULL').fetchone()
    stats['total_hours'] = (result['total'] or 0) / 60
    
    conn.close()
    return render_template('db_browser/index.html', stats=stats)

@db_browser.route('/db/projects')
def projects():
    """View all projects"""
    conn = get_db_connection()
    
    # Get projects with session counts
    projects = conn.execute('''
        SELECT p.*, COUNT(s.id) as session_count, 
               SUM(s.duration_minutes) as total_duration
        FROM projects p
        LEFT JOIN sessions s ON p.id = s.project_id
        GROUP BY p.id
        ORDER BY p.last_activity DESC
    ''').fetchall()
    
    conn.close()
    return render_template('db_browser/projects.html', projects=projects)

@db_browser.route('/db/projects/<int:project_id>')
def project_detail(project_id):
    """View project details"""
    conn = get_db_connection()
    
    project = conn.execute('SELECT * FROM projects WHERE id = ?', (project_id,)).fetchone()
    if not project:
        conn.close()
        flash('Project not found', 'error')
        return redirect(url_for('db_browser.projects'))
    
    # Get master project (parent) if this is a subproject
    master_project = None
    if project['parent_id']:
        master_project = conn.execute('SELECT id, name FROM projects WHERE id = ?', (project['parent_id'],)).fetchone()
    
    # Get subprojects if this is a master project
    subprojects = conn.execute('SELECT id, name, type FROM projects WHERE parent_id = ? ORDER BY name', (project_id,)).fetchall()
    
    # Get sessions for this project
    sessions = conn.execute('''
        SELECT s.*, COUNT(b.id) as break_count
        FROM sessions s
        LEFT JOIN breaks b ON s.id = b.session_id
        WHERE s.project_id = ?
        GROUP BY s.id
        ORDER BY s.start_time DESC
    ''', (project_id,)).fetchall()
    
    # Calculate total duration including subprojects
    total_duration = sum(s['duration_minutes'] or 0 for s in sessions)
    for subproject in subprojects:
        sub_sessions = conn.execute('SELECT duration_minutes FROM sessions WHERE project_id = ?', (subproject['id'],)).fetchall()
        total_duration += sum(s['duration_minutes'] or 0 for s in sub_sessions)
    
    conn.close()
    return render_template('db_browser/project_detail.html', 
                         project=project, 
                         sessions=sessions, 
                         master_project=master_project,
                         subprojects=subprojects,
                         total_duration=total_duration)

@db_browser.route('/db/projects/<int:project_id>/edit', methods=['GET', 'POST'])
def edit_project(project_id):
    """Edit project"""
    conn = get_db_connection()
    
    if request.method == 'POST':
        data = request.form
        parent_id = data.get('parent_id') or None
        if parent_id == '' or parent_id == 'None':
            parent_id = None
        conn.execute('''
            UPDATE projects 
            SET name = ?, type = ?, language = ?, framework = ?, path = ?, git_remote = ?, parent_id = ?
            WHERE id = ?
        ''', (
            data['name'], data['type'], data['language'], data['framework'],
            data['path'], data['git_remote'], parent_id, project_id
        ))
        conn.commit()
        conn.close()
        flash('Project updated successfully', 'success')
        return redirect(url_for('db_browser.project_detail', project_id=project_id))
    
    project = conn.execute('SELECT * FROM projects WHERE id = ?', (project_id,)).fetchone()
    # Get all top-level projects except self and subprojects
    all_projects = conn.execute('SELECT id, name FROM projects WHERE parent_id IS NULL AND id != ? ORDER BY name', (project_id,)).fetchall()
    conn.close()
    
    if not project:
        flash('Project not found', 'error')
        return redirect(url_for('db_browser.projects'))
    
    return render_template('db_browser/edit_project.html', project=project, parent_projects=all_projects)

@db_browser.route('/db/sessions')
def sessions():
    """View all sessions"""
    conn = get_db_connection()
    
    # Get filter parameters
    project_filter = request.args.get('project')
    category_filter = request.args.get('category')
    date_from = request.args.get('date_from')
    date_to = request.args.get('date_to')
    
    # Build query
    query = '''
        SELECT s.*, p.name as project_name, COUNT(b.id) as break_count
        FROM sessions s
        JOIN projects p ON s.project_id = p.id
        LEFT JOIN breaks b ON s.id = b.session_id
    '''
    params = []
    conditions = []
    
    if project_filter:
        conditions.append('p.name LIKE ?')
        params.append(f'%{project_filter}%')
    
    if category_filter:
        conditions.append('s.category = ?')
        params.append(category_filter)
    
    if date_from:
        conditions.append('DATE(s.start_time) >= ?')
        params.append(date_from)
    
    if date_to:
        conditions.append('DATE(s.start_time) <= ?')
        params.append(date_to)
    
    if conditions:
        query += ' WHERE ' + ' AND '.join(conditions)
    
    query += ' GROUP BY s.id ORDER BY s.start_time DESC'
    
    sessions = conn.execute(query, params).fetchall()
    
    # Get projects for filter dropdown
    projects = conn.execute('SELECT name FROM projects ORDER BY name').fetchall()
    
    conn.close()
    return render_template('db_browser/sessions.html', 
                         sessions=sessions, 
                         projects=projects,
                         filters={'project': project_filter, 'category': category_filter, 
                                 'date_from': date_from, 'date_to': date_to})

@db_browser.route('/db/sessions/<int:session_id>')
def session_detail(session_id):
    """View session details"""
    conn = get_db_connection()
    
    session = conn.execute('''
        SELECT s.*, p.name as project_name
        FROM sessions s
        JOIN projects p ON s.project_id = p.id
        WHERE s.id = ?
    ''', (session_id,)).fetchone()
    
    if not session:
        conn.close()
        flash('Session not found', 'error')
        return redirect(url_for('db_browser.sessions'))
    
    breaks = conn.execute('SELECT * FROM breaks WHERE session_id = ? ORDER BY start_time', 
                         (session_id,)).fetchall()
    
    conn.close()
    return render_template('db_browser/session_detail.html', session=session, breaks=breaks)

@db_browser.route('/db/sessions/<int:session_id>/edit', methods=['GET', 'POST'])
def edit_session(session_id):
    """Edit session"""
    conn = get_db_connection()
    
    if request.method == 'POST':
        data = request.form
        
        # Parse datetime
        start_time = datetime.fromisoformat(data['start_time'].replace('Z', '+00:00'))
        end_time = None
        if data['end_time']:
            end_time = datetime.fromisoformat(data['end_time'].replace('Z', '+00:00'))
        
        # Calculate duration
        duration_minutes = None
        if start_time and end_time:
            duration_seconds = (end_time - start_time).total_seconds()
            duration_minutes = int(duration_seconds / 60)
        
        conn.execute('''
            UPDATE sessions 
            SET start_time = ?, end_time = ?, duration_minutes = ?, 
                category = ?, description = ?
            WHERE id = ?
        ''', (start_time, end_time, duration_minutes, data['category'], 
              data['description'], session_id))
        conn.commit()
        conn.close()
        
        flash('Session updated successfully', 'success')
        return redirect(url_for('db_browser.session_detail', session_id=session_id))
    
    session = conn.execute('''
        SELECT s.*, p.name as project_name
        FROM sessions s
        JOIN projects p ON s.project_id = p.id
        WHERE s.id = ?
    ''', (session_id,)).fetchone()
    
    conn.close()
    
    if not session:
        flash('Session not found', 'error')
        return redirect(url_for('db_browser.sessions'))
    
    return render_template('db_browser/edit_session.html', session=session)

@db_browser.route('/db/export')
def export_data():
    """Export database as JSON or CSV"""
    format_type = request.args.get('format')
    table = request.args.get('table')
    
    conn = get_db_connection()
    
    # Get statistics for the template
    stats = {
        'projects': conn.execute('SELECT COUNT(*) FROM projects').fetchone()[0],
        'sessions': conn.execute('SELECT COUNT(*) FROM sessions').fetchone()[0],
        'breaks': conn.execute('SELECT COUNT(*) FROM breaks').fetchone()[0],
        'total_hours': conn.execute('SELECT COALESCE(SUM(duration_minutes), 0) / 60.0 FROM sessions').fetchone()[0]
    }
    
    if format_type == 'csv' and table:
        # CSV export for specific table
        if table == 'projects':
            data = conn.execute('SELECT * FROM projects').fetchall()
            headers = ['id', 'name', 'type', 'language', 'framework', 'path', 'git_remote', 'created_at']
        elif table == 'sessions':
            data = conn.execute('''
                SELECT s.*, p.name as project_name 
                FROM sessions s 
                JOIN projects p ON s.project_id = p.id
            ''').fetchall()
            headers = ['id', 'project_id', 'project_name', 'start_time', 'end_time', 'duration_minutes', 'category', 'description']
        else:
            conn.close()
            flash('Invalid table specified', 'error')
            return redirect(url_for('db_browser.export_data'))
        
        # Create CSV response
        import csv
        from io import StringIO
        
        si = StringIO()
        cw = csv.writer(si)
        cw.writerow(headers)
        cw.writerows(data)
        
        conn.close()
        
        output = si.getvalue()
        return Response(
            output,
            mimetype='text/csv',
            headers={'Content-Disposition': f'attachment; filename={table}_export.csv'}
        )
    
    elif format_type == 'json':
        # JSON export
        projects = conn.execute('SELECT * FROM projects').fetchall()
        sessions = conn.execute('SELECT * FROM sessions').fetchall()
        breaks = conn.execute('SELECT * FROM breaks').fetchall()
        
        # Convert to dictionaries
        data = {
            'exported_at': datetime.now().isoformat(),
            'projects': [dict(p) for p in projects],
            'sessions': [dict(s) for s in sessions],
            'breaks': [dict(b) for b in breaks]
        }
        
        conn.close()
        
        return jsonify(data)
    
    else:
        # Show export page (default)
        conn.close()
        return render_template('db_browser/export.html', stats=stats)

@db_browser.route('/db/search')
def search():
    """Search across all data"""
    query = request.args.get('q', '')
    if not query:
        return render_template('db_browser/search.html', results=None)
    
    conn = get_db_connection()
    
    # Search in projects
    projects = conn.execute('''
        SELECT 'project' as type, id, name as title, created_at as date
        FROM projects 
        WHERE name LIKE ? OR type LIKE ? OR language LIKE ? OR framework LIKE ?
    ''', (f'%{query}%', f'%{query}%', f'%{query}%', f'%{query}%')).fetchall()
    
    # Search in sessions
    sessions = conn.execute('''
        SELECT 'session' as type, s.id, s.description as title, s.start_time as date,
               p.name as project_name
        FROM sessions s
        JOIN projects p ON s.project_id = p.id
        WHERE s.description LIKE ? OR s.category LIKE ?
    ''', (f'%{query}%', f'%{query}%')).fetchall()
    
    conn.close()
    
    results = {
        'projects': projects,
        'sessions': sessions,
        'query': query
    }
    
    return render_template('db_browser/search.html', results=results) 