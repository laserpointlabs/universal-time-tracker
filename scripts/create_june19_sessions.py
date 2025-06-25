#!/usr/bin/env python3
"""
Script to create June 19, 2025 work sessions via API
"""

import requests
import json
from datetime import datetime

# API base URL
BASE_URL = 'http://localhost:9000/api/v1'

# Project ID for "DADM BPMN Research June 19"
PROJECT_ID = 3

# Session details for June 19, 2025
sessions_data = [
    {
        'description': 'Technology Stack Research - Analysis of modern workflow engines, BPMN standards, and integration patterns',
        'category': 'Research',
        'start_time': '2025-06-19T08:00:00',
        'end_time': '2025-06-19T10:30:00',
        'duration_hours': 2.5
    },
    {
        'description': 'Architecture Analysis - Deep dive into Camunda architecture and deployment patterns',
        'category': 'Architecture',
        'start_time': '2025-06-19T10:30:00',
        'end_time': '2025-06-19T12:30:00',
        'duration_hours': 2.0
    },
    {
        'description': 'Competitive Analysis - Evaluation of workflow engines and BPMN solutions',
        'category': 'Research',
        'start_time': '2025-06-19T13:30:00',
        'end_time': '2025-06-19T15:00:00',
        'duration_hours': 1.5
    },
    {
        'description': 'System Architecture Design - Design of integrated BPMN-AI system architecture',
        'category': 'Design',
        'start_time': '2025-06-19T15:00:00',
        'end_time': '2025-06-19T17:00:00',
        'duration_hours': 2.0
    },
    {
        'description': 'Implementation Planning - Development roadmap and integration strategies',
        'category': 'Planning',
        'start_time': '2025-06-19T17:00:00',
        'end_time': '2025-06-19T18:30:00',
        'duration_hours': 1.5
    },
    {
        'description': 'Documentation & Knowledge Capture - Comprehensive documentation of research findings',
        'category': 'Documentation',
        'start_time': '2025-06-19T18:30:00',
        'end_time': '2025-06-19T20:00:00',
        'duration_hours': 1.5
    }
]

def create_sessions():
    """Create backdated sessions for June 19, 2025"""
    total_hours = 0
    
    for i, session in enumerate(sessions_data, 1):
        print(f"Creating session {i}/6: {session['description'][:50]}...")
        
        # Start session
        start_payload = {
            'project': 'DADM BPMN Research June 19',
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
            
            # Stop the session
            stop_payload = {
                'project': 'DADM BPMN Research June 19'
            }
            
            stop_response = requests.post(f'{BASE_URL}/sessions/stop', json=stop_payload)
            if stop_response.status_code != 200:
                print(f"Error stopping session: {stop_response.text}")
                continue
                
            print(f"  Stopped session {session_id}")
            total_hours += session['duration_hours']
            
        except requests.exceptions.RequestException as e:
            print(f"Network error: {e}")
            continue
    
    print(f"\nCreated 6 sessions totaling {total_hours} hours for June 19, 2025")
    print("Now we need to update the database directly to set the correct timestamps...")

if __name__ == "__main__":
    create_sessions()
