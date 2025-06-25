#!/usr/bin/env python3
"""
Script to update sessions 20-25 with correct June 19, 2025 timestamps and durations
"""

import sqlite3
from datetime import datetime

# Database path
DB_PATH = '/home/jdehart/dadm/universal-time-tracker/data/timetracker.db'

# Session updates for sessions 20-25 (June 19, 2025)
session_updates = [
    # Session 20: Technology Stack Research (2.5 hrs)
    {
        'id': 20,
        'start_time': '2025-06-19 08:00:00',
        'end_time': '2025-06-19 10:30:00',
        'duration_minutes': 150
    },
    # Session 21: Architecture Analysis (2.0 hrs) 
    {
        'id': 21,
        'start_time': '2025-06-19 10:30:00',
        'end_time': '2025-06-19 12:30:00',
        'duration_minutes': 120
    },
    # Session 22: Competitive Analysis (1.5 hrs)
    {
        'id': 22,
        'start_time': '2025-06-19 13:30:00',
        'end_time': '2025-06-19 15:00:00',
        'duration_minutes': 90
    },
    # Session 23: System Architecture Design (2.0 hrs)
    {
        'id': 23,
        'start_time': '2025-06-19 15:00:00',
        'end_time': '2025-06-19 17:00:00',
        'duration_minutes': 120
    },
    # Session 24: Implementation Planning (1.5 hrs)
    {
        'id': 24,
        'start_time': '2025-06-19 17:00:00',
        'end_time': '2025-06-19 18:30:00',
        'duration_minutes': 90
    },
    # Session 25: Documentation & Knowledge Capture (1.5 hrs)
    {
        'id': 25,
        'start_time': '2025-06-19 18:30:00',
        'end_time': '2025-06-19 20:00:00',
        'duration_minutes': 90
    }
]

def update_sessions():
    """Update sessions with correct June 19, 2025 timestamps"""
    try:
        # Connect to database
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        total_minutes = 0
        
        for session in session_updates:
            print(f"Updating session {session['id']}...")
            
            # Update the session
            cursor.execute("""
                UPDATE sessions 
                SET start_time = ?, 
                    end_time = ?, 
                    duration_minutes = ?
                WHERE id = ?
            """, (
                session['start_time'],
                session['end_time'], 
                session['duration_minutes'],
                session['id']
            ))
            
            total_minutes += session['duration_minutes']
            print(f"  Set duration to {session['duration_minutes']} minutes")
        
        # Commit changes
        conn.commit()
        
        # Verify updates
        print("\nVerifying updates:")
        cursor.execute("""
            SELECT id, start_time, end_time, duration_minutes, description 
            FROM sessions 
            WHERE id BETWEEN 20 AND 25 
            ORDER BY id
        """)
        
        results = cursor.fetchall()
        for row in results:
            session_id, start_time, end_time, duration, description = row
            print(f"Session {session_id}: {start_time} to {end_time} ({duration} min) - {description[:50]}...")
        
        print(f"\nTotal duration: {total_minutes} minutes ({total_minutes/60:.1f} hours)")
        print("Successfully updated all June 19, 2025 sessions!")
        
        conn.close()
        
    except Exception as e:
        print(f"Error updating sessions: {e}")
        return False
    
    return True

if __name__ == "__main__":
    success = update_sessions()
    if success:
        print("\nDatabase updated successfully!")
        print("You can now restart the Docker container to view the updated hours on the dashboard.")
    else:
        print("\nFailed to update database.")
