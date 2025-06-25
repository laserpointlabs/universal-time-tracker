#!/usr/bin/env python3
"""
Test script to verify user ID is set correctly
"""

import requests
import json
from datetime import datetime, timedelta

# Test configuration
BASE_URL = 'http://localhost:9000/api/v1'
PROJECT_NAME = 'Universal Time Tracker'

def test_user_id_in_sessions():
    """Test that user ID is set correctly in sessions"""
    
    print("🧪 Testing User ID in Sessions")
    print("=" * 40)
    
    # Test 1: Historical session creation
    print("\n📅 Testing historical session creation...")
    
    historical_session = {
        'project': PROJECT_NAME,
        'description': 'Test historical session user ID',
        'category': 'testing',
        'start_time': '2024-01-15T22:00:00',
        'end_time': '2024-01-15T23:00:00'
    }
    
    try:
        response = requests.post(f'{BASE_URL}/sessions/create', json=historical_session)
        
        if response.status_code == 200:
            data = response.json()
            session_id = data['session_id']
            print(f"✅ Created historical session #{session_id}")
            
            # Check the session in the database
            db_response = requests.get(f'http://localhost:9000/db/sessions')
            if 'jdehart' in db_response.text and 'Test historical session user ID' in db_response.text:
                print("✅ User ID 'jdehart' found in historical session")
            else:
                print("❌ User ID not found or incorrect in historical session")
        else:
            print(f"❌ Error creating historical session: {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Network error: {e}")
    
    # Test 2: Regular session start/stop
    print("\n⏰ Testing regular session start/stop...")
    
    regular_session = {
        'project': PROJECT_NAME,
        'description': 'Test regular session user ID',
        'category': 'development'
    }
    
    try:
        # Start session
        start_response = requests.post(f'{BASE_URL}/sessions/start', json=regular_session)
        
        if start_response.status_code == 200:
            start_data = start_response.json()
            session_id = start_data['session_id']
            print(f"✅ Started regular session #{session_id}")
            
            # Stop session
            stop_response = requests.post(f'{BASE_URL}/sessions/stop', json={'project': PROJECT_NAME})
            
            if stop_response.status_code == 200:
                print("✅ Stopped regular session")
                
                # Check the session in the database
                db_response = requests.get(f'http://localhost:9000/db/sessions')
                if 'jdehart' in db_response.text and 'Test regular session user ID' in db_response.text:
                    print("✅ User ID 'jdehart' found in regular session")
                else:
                    print("❌ User ID not found or incorrect in regular session")
            else:
                print(f"❌ Error stopping session: {stop_response.text}")
        else:
            print(f"❌ Error starting session: {start_response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Network error: {e}")
    
    # Test 3: Check for "unknown" user IDs
    print("\n🔍 Checking for 'unknown' user IDs...")
    
    try:
        db_response = requests.get(f'http://localhost:9000/db/sessions')
        
        if 'unknown' in db_response.text:
            print("⚠️  Found 'unknown' user IDs in database")
            # Count occurrences
            unknown_count = db_response.text.count('unknown')
            print(f"   Found {unknown_count} occurrences of 'unknown'")
        else:
            print("✅ No 'unknown' user IDs found in database")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Network error: {e}")

def test_user_id_consistency():
    """Test that all recent sessions have consistent user IDs"""
    
    print("\n🔄 Testing User ID Consistency")
    print("-" * 30)
    
    try:
        db_response = requests.get(f'http://localhost:9000/db/sessions')
        
        # Look for recent sessions (last 10)
        lines = db_response.text.split('\n')
        user_lines = []
        
        for i, line in enumerate(lines):
            if 'jdehart' in line:
                # Get the session description from nearby lines
                for j in range(max(0, i-10), min(len(lines), i+10)):
                    if 'Test session' in lines[j] or 'Test historical' in lines[j] or 'Test regular' in lines[j]:
                        user_lines.append((lines[j].strip(), 'jdehart'))
                        break
        
        print(f"✅ Found {len(user_lines)} recent test sessions with 'jdehart' user ID:")
        for desc, user_id in user_lines:
            print(f"   - {desc[:50]}... -> {user_id}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Network error: {e}")

def main():
    """Run all tests"""
    test_user_id_in_sessions()
    test_user_id_consistency()
    
    print(f"\n" + "=" * 40)
    print("🎉 User ID testing completed!")

if __name__ == "__main__":
    main() 