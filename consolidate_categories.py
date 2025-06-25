#!/usr/bin/env python3
"""
Consolidate session categories in the database to match .timecfg structure
"""

import sqlite3
import os

def get_db_connection():
    """Get database connection"""
    database_path = os.environ.get('DATABASE_PATH', '/app/data/timetracker.db')
    conn = sqlite3.connect(database_path)
    conn.row_factory = sqlite3.Row
    return conn

def consolidate_categories():
    """Consolidate categories to match .timecfg structure"""
    conn = get_db_connection()
    
    # Standard categories from .timecfg
    standard_categories = {
        'development',
        'research', 
        'documentation',
        'meetings',
        'testing',
        'deployment'
    }
    
    # Category mapping for consolidation
    category_mapping = {
        # Uppercase to lowercase
        'Architecture': 'development',
        'Design': 'development', 
        'Documentation': 'documentation',
        'Planning': 'meetings',
        'Research': 'research',
        
        # Non-standard to standard
        'architecture': 'development',
        'design': 'development',
        'frontend': 'development',
        'planning': 'meetings',
        'debugging': 'testing',
        'meeting': 'meetings',
        'other': 'development'
    }
    
    print("Current categories in database:")
    current_categories = conn.execute("SELECT DISTINCT category FROM sessions ORDER BY category").fetchall()
    for row in current_categories:
        print(f"  - {row['category']}")
    
    print(f"\nStandard categories from .timecfg: {', '.join(sorted(standard_categories))}")
    
    # Get all sessions with non-standard categories
    non_standard_sessions = conn.execute("""
        SELECT id, category FROM sessions 
        WHERE category NOT IN (?, ?, ?, ?, ?, ?)
        ORDER BY category
    """, tuple(standard_categories)).fetchall()
    
    if not non_standard_sessions:
        print("\n✅ All categories are already standardized!")
        conn.close()
        return
    
    print(f"\nFound {len(non_standard_sessions)} sessions with non-standard categories:")
    
    # Group by current category
    category_counts = {}
    for session in non_standard_sessions:
        cat = session['category']
        category_counts[cat] = category_counts.get(cat, 0) + 1
    
    for cat, count in sorted(category_counts.items()):
        new_cat = category_mapping.get(cat, 'development')
        print(f"  - {cat} ({count} sessions) → {new_cat}")
    
    # Confirm before proceeding
    response = input("\nProceed with consolidation? (y/N): ").strip().lower()
    if response != 'y':
        print("Consolidation cancelled.")
        conn.close()
        return
    
    # Update categories
    updated_count = 0
    for session in non_standard_sessions:
        old_category = session['category']
        new_category = category_mapping.get(old_category, 'development')
        
        conn.execute("UPDATE sessions SET category = ? WHERE id = ?", 
                    (new_category, session['id']))
        updated_count += 1
    
    conn.commit()
    
    print(f"\n✅ Updated {updated_count} sessions")
    
    # Show final categories
    print("\nFinal categories in database:")
    final_categories = conn.execute("SELECT DISTINCT category FROM sessions ORDER BY category").fetchall()
    for row in final_categories:
        count = conn.execute("SELECT COUNT(*) as count FROM sessions WHERE category = ?", 
                           (row['category'],)).fetchone()['count']
        print(f"  - {row['category']} ({count} sessions)")
    
    conn.close()

if __name__ == "__main__":
    consolidate_categories() 