#!/usr/bin/env python3
"""
Script to create all June 19, 2025 work sessions correctly
"""

import requests
import json
from datetime import datetime
import time

# API base URL
BASE_URL = 'http://localhost:9000/api/v1'
PROJECT_NAME = 'DADM BPMN Research June 19'

# Session details for June 19, 2025
sessions_data = [
    {
        'description': 'Technology Stack Research - Analysis of modern workflow engines, BPMN standards, and integration patterns',
        'category': 'Research',
        'duration_hours': 2.5
    },
    {
        'description': 'Architecture Analysis - Deep dive into Camunda architecture and deployment patterns',
        'category': 'Architecture',
        'duration_hours': 2.0
    },
    {
        'description': 'Competitive Analysis - Evaluation of workflow engines and BPMN solutions',
        'category': 'Research',
        'duration_hours': 1.5
    },
    {
        'description': 'System Architecture Design - Design of integrated BPMN-AI system architecture',
        'category': 'Design',
        'duration_hours': 2.0
    },
    {
        'description': 'Implementation Planning - Development roadmap and integration strategies',
        'category': 'Planning',
        'duration_hours': 1.5
    },
    {
        'description': 'Documentation & Knowledge Capture - Comprehensive documentation of research findings',
        'category': 'Documentation',
        'duration_hours': 1.5
    }
]

def create_sessions():
    """Create sessions for June 19, 2025"""
    total_hours = 0
    session_ids = []
    
    for i, session in enumerate(sessions_data, 1):
        print(f"Creating session {i}/6: {session['description'][:50]}...")
        
        # Start session
        start_payload = {
            'project': PROJECT_NAME,
            'description': session['description'],
            'category': session['category']
        }
        
        try:
            # Start the session
            start_response = requests.post(f'{BASE_URL}/sessions/start', json=start_payload)
            if start_response.status_code != 200:
                print(f"Error starting session: {start_response.text}")
                continue
                
            session_data = start_response.json()
            session_id = session_data['session_id']
            print(f"  Started session {session_id}")
            
            # Small delay to ensure different timestamps
            time.sleep(1)
            
            # Stop the session
            stop_payload = {
                'project': PROJECT_NAME
            }
            
            stop_response = requests.post(f'{BASE_URL}/sessions/stop', json=stop_payload)
            if stop_response.status_code != 200:
                print(f"Error stopping session: {stop_response.text}")
                continue
                
            print(f"  Stopped session {session_id}")
            session_ids.append(session_id)
            total_hours += session['duration_hours']
            
        except requests.exceptions.RequestException as e:
            print(f"Network error: {e}")
            continue
    
    print(f"\nCreated {len(session_ids)} sessions totaling {total_hours} hours for June 19, 2025")
    print(f"Session IDs: {session_ids}")
    return session_ids

if __name__ == "__main__":
    session_ids = create_sessions()
    
    print("\nNext step: Update database to set correct June 19, 2025 timestamps and durations")
    print("Session IDs that need updating:", session_ids)
