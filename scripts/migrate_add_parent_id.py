#!/usr/bin/env python3
"""
Migration script to add parent_id column to projects table
and set up initial parent-child relationships
"""

import sqlite3
import os

def migrate_database():
    """Add parent_id column and set up initial relationships"""
    # Use correct path for real database
    db_path = '../data/timetracker.db'
    
    # Ensure the data directory exists
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Check if parent_id column already exists
        cursor.execute("PRAGMA table_info(projects)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'parent_id' not in columns:
            print("Adding parent_id column to projects table...")
            cursor.execute("ALTER TABLE projects ADD COLUMN parent_id INTEGER REFERENCES projects(id)")
            print("✓ parent_id column added successfully")
        else:
            print("✓ parent_id column already exists")
        
        # Set up DADM BPMN Research June 19 as subproject of DADM Development
        print("\nSetting up parent-child relationships...")
        
        # Find DADM Development project
        cursor.execute("SELECT id FROM projects WHERE name = 'DADM Development'")
        dadm_dev_result = cursor.fetchone()
        
        # Find DADM BPMN Research June 19 project
        cursor.execute("SELECT id FROM projects WHERE name = 'DADM BPMN Research June 19'")
        bpmn_research_result = cursor.fetchone()
        
        if dadm_dev_result and bpmn_research_result:
            dadm_dev_id = dadm_dev_result[0]
            bpmn_research_id = bpmn_research_result[0]
            
            # Set DADM BPMN Research June 19 as subproject of DADM Development
            cursor.execute("UPDATE projects SET parent_id = ? WHERE id = ?", (dadm_dev_id, bpmn_research_id))
            print(f"✓ Set 'DADM BPMN Research June 19' (ID: {bpmn_research_id}) as subproject of 'DADM Development' (ID: {dadm_dev_id})")
        else:
            print("⚠ Could not find required projects for relationship setup")
            if not dadm_dev_result:
                print("  - 'DADM Development' not found")
            if not bpmn_research_result:
                print("  - 'DADM BPMN Research June 19' not found")
        
        # Commit changes
        conn.commit()
        print("\n✓ Migration completed successfully")
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        conn.rollback()
        raise
    finally:
        conn.close()

if __name__ == "__main__":
    migrate_database() 