#!/usr/bin/env python3
"""
Database Manager CLI for Universal Time Tracker
Provides command-line database management capabilities
"""

import sqlite3
import json
import os
import sys
from datetime import datetime, timedelta
from tabulate import tabulate
import argparse

DATABASE_PATH = os.environ.get('DATABASE_PATH', 'data/timetracker.db')

def get_db_connection():
    """Get database connection"""
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def show_stats():
    """Show database statistics"""
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
    
    print("=== Database Statistics ===")
    print(f"Projects: {stats['projects']}")
    print(f"Sessions: {stats['sessions']}")
    print(f"Breaks: {stats['breaks']}")
    print(f"Active Sessions: {stats['active_sessions']}")
    print(f"Total Hours: {stats['total_hours']:.1f}")
    print()

def list_projects():
    """List all projects"""
    conn = get_db_connection()
    
    projects = conn.execute('''
        SELECT p.*, COUNT(s.id) as session_count, 
               SUM(s.duration_minutes) as total_duration
        FROM projects p
        LEFT JOIN sessions s ON p.id = s.project_id
        GROUP BY p.id
        ORDER BY p.last_activity DESC
    ''').fetchall()
    
    conn.close()
    
    if not projects:
        print("No projects found.")
        return
    
    table_data = []
    for p in projects:
        hours = (p['total_duration'] or 0) / 60
        table_data.append([
            p['id'],
            p['name'],
            p['type'],
            p['language'] or '-',
            p['framework'] or '-',
            p['session_count'],
            f"{hours:.1f}h",
            p['last_activity'].split('T')[0] if p['last_activity'] else '-'
        ])
    
    headers = ['ID', 'Name', 'Type', 'Language', 'Framework', 'Sessions', 'Hours', 'Last Activity']
    print(tabulate(table_data, headers=headers, tablefmt='grid'))

def list_sessions(limit=20, project=None):
    """List recent sessions"""
    conn = get_db_connection()
    
    query = '''
        SELECT s.*, p.name as project_name, COUNT(b.id) as break_count
        FROM sessions s
        JOIN projects p ON s.project_id = p.id
        LEFT JOIN breaks b ON s.id = b.session_id
    '''
    params = []
    
    if project:
        query += ' WHERE p.name LIKE ?'
        params.append(f'%{project}%')
    
    query += ' GROUP BY s.id ORDER BY s.start_time DESC LIMIT ?'
    params.append(limit)
    
    sessions = conn.execute(query, params).fetchall()
    conn.close()
    
    if not sessions:
        print("No sessions found.")
        return
    
    table_data = []
    for s in sessions:
        duration = ""
        if s['duration_minutes']:
            hours = s['duration_minutes'] // 60
            minutes = s['duration_minutes'] % 60
            if hours > 0:
                duration = f"{hours}h {minutes}m"
            else:
                duration = f"{minutes}m"
        else:
            duration = "Active" if not s['end_time'] else "-"
        
        table_data.append([
            s['id'],
            s['project_name'],
            s['description'][:50] + "..." if len(s['description']) > 50 else s['description'],
            s['category'],
            s['start_time'].split('T')[0],
            s['start_time'].split('T')[1][:5],
            duration,
            s['break_count']
        ])
    
    headers = ['ID', 'Project', 'Description', 'Category', 'Date', 'Time', 'Duration', 'Breaks']
    print(tabulate(table_data, headers=headers, tablefmt='grid'))

def search_data(query):
    """Search across all data"""
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
    
    print(f"=== Search Results for '{query}' ===")
    
    if projects:
        print(f"\nProjects ({len(projects)}):")
        for p in projects:
            print(f"  [{p['id']}] {p['title']} ({p['date'].split('T')[0]})")
    
    if sessions:
        print(f"\nSessions ({len(sessions)}):")
        for s in sessions:
            print(f"  [{s['id']}] {s['title']} - {s['project_name']} ({s['date'].split('T')[0]})")
    
    if not projects and not sessions:
        print("No results found.")

def export_data(output_file=None):
    """Export database as JSON"""
    conn = get_db_connection()
    
    # Get all data
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
    
    if output_file:
        with open(output_file, 'w') as f:
            json.dump(data, f, indent=2)
        print(f"Data exported to {output_file}")
    else:
        print(json.dumps(data, indent=2))

def show_project_details(project_id):
    """Show detailed information about a project"""
    conn = get_db_connection()
    
    project = conn.execute('SELECT * FROM projects WHERE id = ?', (project_id,)).fetchone()
    if not project:
        print(f"Project with ID {project_id} not found.")
        conn.close()
        return
    
    sessions = conn.execute('''
        SELECT s.*, COUNT(b.id) as break_count
        FROM sessions s
        LEFT JOIN breaks b ON s.id = b.session_id
        WHERE s.project_id = ?
        GROUP BY s.id
        ORDER BY s.start_time DESC
    ''', (project_id,)).fetchall()
    
    conn.close()
    
    print(f"=== Project: {project['name']} ===")
    print(f"ID: {project['id']}")
    print(f"Type: {project['type']}")
    print(f"Language: {project['language'] or 'N/A'}")
    print(f"Framework: {project['framework'] or 'N/A'}")
    print(f"Created: {project['created_at']}")
    print(f"Last Activity: {project['last_activity']}")
    print(f"Total Sessions: {len(sessions)}")
    
    if sessions:
        total_duration = sum(s['duration_minutes'] or 0 for s in sessions)
        print(f"Total Hours: {total_duration / 60:.1f}")
        
        print(f"\n=== Recent Sessions ===")
        table_data = []
        for s in sessions[:10]:  # Show last 10 sessions
            duration = ""
            if s['duration_minutes']:
                hours = s['duration_minutes'] // 60
                minutes = s['duration_minutes'] % 60
                if hours > 0:
                    duration = f"{hours}h {minutes}m"
                else:
                    duration = f"{minutes}m"
            else:
                duration = "Active" if not s['end_time'] else "-"
            
            table_data.append([
                s['id'],
                s['description'][:40] + "..." if len(s['description']) > 40 else s['description'],
                s['category'],
                s['start_time'].split('T')[0],
                duration,
                s['break_count']
            ])
        
        headers = ['ID', 'Description', 'Category', 'Date', 'Duration', 'Breaks']
        print(tabulate(table_data, headers=headers, tablefmt='grid'))

def main():
    parser = argparse.ArgumentParser(description='Database Manager for Universal Time Tracker')
    parser.add_argument('command', choices=['stats', 'projects', 'sessions', 'search', 'export', 'project'], 
                       help='Command to execute')
    parser.add_argument('--limit', type=int, default=20, help='Limit number of results (for sessions)')
    parser.add_argument('--project', type=str, help='Filter by project name')
    parser.add_argument('--query', type=str, help='Search query')
    parser.add_argument('--output', type=str, help='Output file for export')
    parser.add_argument('--id', type=int, help='Project ID for detailed view')
    
    args = parser.parse_args()
    
    if not os.path.exists(DATABASE_PATH):
        print(f"Database not found at {DATABASE_PATH}")
        sys.exit(1)
    
    if args.command == 'stats':
        show_stats()
    elif args.command == 'projects':
        list_projects()
    elif args.command == 'sessions':
        list_sessions(args.limit, args.project)
    elif args.command == 'search':
        if not args.query:
            print("Please provide a search query with --query")
            sys.exit(1)
        search_data(args.query)
    elif args.command == 'export':
        export_data(args.output)
    elif args.command == 'project':
        if not args.id:
            print("Please provide a project ID with --id")
            sys.exit(1)
        show_project_details(args.id)

if __name__ == '__main__':
    main() 