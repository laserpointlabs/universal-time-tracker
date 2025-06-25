#!/usr/bin/env python3
"""
Script to update time tracking sessions with correct June 19, 2025 data
"""

import sqlite3
from datetime import datetime, timedelta

# Database path
DB_PATH = '/home/jdehart/dadm/universal-time-tracker/data/timetracker.db'

# Session details for June 19, 2025
sessions_data = [
    # Session ID 8: Technology Stack Research (2.5 hrs)
    {
        'id': 8,
        'start_time': datetime(2025, 6, 19, 8, 0, 0),
        'end_time': datetime(2025, 6, 19, 10, 30, 0),
        'duration_minutes': 150
    },
    # Session ID 9: Architecture Analysis (2.0 hrs) 
    {
        'id': 9,
        'start_time': datetime(2025, 6, 19, 10, 30, 0),
        'end_time': datetime(2025, 6, 19, 12, 30, 0),
        'duration_minutes': 120
    },
    # Session ID 10: Competitive Analysis (1.5 hrs)
    {
        'id': 10,
        'start_time': datetime(2025, 6, 19, 13, 30, 0),
        'end_time': datetime(2025, 6, 19, 15, 0, 0),
        'duration_minutes': 90
    },
    # Session ID 11: System Architecture Design (2.0 hrs)
    {
        'id': 11,
        'start_time': datetime(2025, 6, 19, 15, 0, 0),
        'end_time': datetime(2025, 6, 19, 17, 0, 0),
        'duration_minutes': 120
    },
    # Session ID 12: Implementation Planning (1.5 hrs)
    {
        'id': 12,
        'start_time': datetime(2025, 6, 19, 17, 0, 0),
        'end_time': datetime(2025, 6, 19, 18, 30, 0),
        'duration_minutes': 90
    },
    # Session ID 13: Documentation & Knowledge Capture (1.5 hrs)
    {
        'id': 13,
        'start_time': datetime(2025, 6, 19, 18, 30, 0),
        'end_time': datetime(2025, 6, 19, 20, 0, 0),
        'duration_minutes': 90
    }
]

try:
    # Connect to database
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    total_minutes = 0
    
    # Update each session with correct dates and durations
    for session in sessions_data:
        cursor.execute("""
            UPDATE sessions 
            SET start_time = ?, 
                end_time = ?, 
                duration_minutes = ?
            WHERE id = ?
        """, (
            session['start_time'].isoformat(), 
            session['end_time'].isoformat(), 
            session['duration_minutes'], 
            session['id']
        ))
        
        total_minutes += session['duration_minutes']
        print(f"✅ Updated session {session['id']}: {session['duration_minutes']} minutes ({session['duration_minutes']/60} hours)")
    
    # Update the project's last_activity to June 19
    cursor.execute("""
        UPDATE projects 
        SET last_activity = ?
        WHERE name = 'DADM BPMN Research June 19'
    """, (datetime(2025, 6, 19, 20, 0, 0).isoformat(),))
    
    conn.commit()
    print(f"\n🎯 Total hours logged: {total_minutes/60} hours ({total_minutes} minutes)")
    print(f"📅 All sessions dated: June 19, 2025")
    
    # Verify the updates
    cursor.execute("""
        SELECT id, start_time, end_time, duration_minutes, description 
        FROM sessions 
        WHERE id IN (8, 9, 10, 11, 12, 13)
        ORDER BY id
    """)
    
    print("\n📋 Verification:")
    for session in cursor.fetchall():
        print(f"   Session {session[0]}: {session[3]} min - {session[4][:50]}...")
    
except Exception as e:
    print(f"❌ Error updating sessions: {e}")
finally:
    conn.close()
