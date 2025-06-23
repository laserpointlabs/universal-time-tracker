#!/usr/bin/env python3
"""
Script to move June 19, 2025 sessions from "DADM BPMN Research June 19" to "DADM Development"
"""

import sqlite3

# Database path
DB_PATH = '/home/jdehart/dadm/universal-time-tracker/data/timetracker.db'

def move_sessions_to_dadm_development():
    """Move sessions 20-25 from DADM BPMN Research project to DADM Development"""
    try:
        # Connect to database
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Get project IDs
        cursor.execute("SELECT id, name FROM projects")
        projects = cursor.fetchall()
        print("Available projects:")
        for project_id, name in projects:
            print(f"  {project_id}: {name}")
        
        # Find project IDs
        dadm_dev_id = None
        bpmn_research_id = None
        
        for project_id, name in projects:
            if name == "DADM Development":
                dadm_dev_id = project_id
            elif name == "DADM BPMN Research June 19":
                bpmn_research_id = project_id
        
        if not dadm_dev_id:
            print("Error: DADM Development project not found!")
            return False
            
        if not bpmn_research_id:
            print("Error: DADM BPMN Research June 19 project not found!")
            return False
            
        print(f"\nMoving sessions from project {bpmn_research_id} to project {dadm_dev_id}")
        
        # Check which sessions need to be moved
        cursor.execute("""
            SELECT id, description, start_time, duration_minutes 
            FROM sessions 
            WHERE project_id = ? AND date(start_time) = '2025-06-19'
            ORDER BY id
        """, (bpmn_research_id,))
        
        sessions_to_move = cursor.fetchall()
        print(f"Found {len(sessions_to_move)} sessions to move:")
        
        for session_id, description, start_time, duration in sessions_to_move:
            print(f"  Session {session_id}: {description[:50]}... ({duration} min)")
        
        if sessions_to_move:
            # Update sessions to move them to DADM Development
            cursor.execute("""
                UPDATE sessions 
                SET project_id = ? 
                WHERE project_id = ? AND date(start_time) = '2025-06-19'
            """, (dadm_dev_id, bpmn_research_id))
            
            # Update last_activity for DADM Development project
            cursor.execute("""
                UPDATE projects 
                SET last_activity = '2025-06-19 20:00:00' 
                WHERE id = ?
            """, (dadm_dev_id,))
            
            conn.commit()
            print(f"\nSuccessfully moved {len(sessions_to_move)} sessions to DADM Development!")
            
            # Verify the move
            cursor.execute("""
                SELECT COUNT(*) 
                FROM sessions 
                WHERE project_id = ? AND date(start_time) = '2025-06-19'
            """, (dadm_dev_id,))
            
            count = cursor.fetchone()[0]
            print(f"Verification: DADM Development now has {count} sessions from June 19, 2025")
            
            # Calculate total hours
            cursor.execute("""
                SELECT SUM(duration_minutes) 
                FROM sessions 
                WHERE project_id = ? AND date(start_time) = '2025-06-19'
            """, (dadm_dev_id,))
            
            total_minutes = cursor.fetchone()[0] or 0
            total_hours = total_minutes / 60
            print(f"Total hours for June 19, 2025: {total_hours} hours ({total_minutes} minutes)")
            
        else:
            print("No sessions found to move.")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"Error moving sessions: {e}")
        return False

if __name__ == "__main__":
    success = move_sessions_to_dadm_development()
    if success:
        print("\nSessions successfully moved to DADM Development!")
        print("You can now restart the Docker container to see the unified project data.")
    else:
        print("\nFailed to move sessions.")
