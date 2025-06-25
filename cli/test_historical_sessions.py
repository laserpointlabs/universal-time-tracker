#!/usr/bin/env python3
"""
Test script for historical session creation functionality
"""

import requests
import json
from datetime import datetime, timedelta

# Test configuration
BASE_URL = 'http://localhost:9000/api/v1'
PROJECT_NAME = 'Universal Time Tracker'

def test_create_historical_session():
    """Test creating a historical session"""
    
    # Test data
    test_session = {
        'project': PROJECT_NAME,
        'description': 'Test historical session creation',
        'category': 'testing',
        'start_time': '2024-01-15T09:00:00',
        'end_time': '2024-01-15T11:30:00'
    }
    
    print("🧪 Testing historical session creation...")
    
    try:
        # Create the session
        response = requests.post(f'{BASE_URL}/sessions/create', json=test_session)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Success! Created session #{data['session_id']}")
            print(f"   Description: {data['description']}")
            print(f"   Category: {data['category']}")
            print(f"   Start: {data['start_time']}")
            print(f"   End: {data['end_time']}")
            print(f"   Duration: {data['duration_minutes']} minutes")
            return True
        else:
            print(f"❌ Error: {response.status_code} - {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Network error: {e}")
        return False

def test_create_session_with_duration():
    """Test creating a session with duration instead of end time"""
    
    # Calculate start time as 2 hours ago
    start_time = datetime.now() - timedelta(hours=2)
    
    test_session = {
        'project': PROJECT_NAME,
        'description': 'Test session with duration calculation',
        'category': 'development',
        'start_time': start_time.isoformat(),
        'end_time': (start_time + timedelta(hours=1.5)).isoformat()
    }
    
    print("\n🧪 Testing session with duration calculation...")
    
    try:
        response = requests.post(f'{BASE_URL}/sessions/create', json=test_session)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Success! Created session #{data['session_id']}")
            print(f"   Duration: {data['duration_minutes']} minutes (expected: 90)")
            return True
        else:
            print(f"❌ Error: {response.status_code} - {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Network error: {e}")
        return False

def test_create_active_session():
    """Test creating an active session (no end time)"""
    
    # Start time as 1 hour ago
    start_time = datetime.now() - timedelta(hours=1)
    
    test_session = {
        'project': PROJECT_NAME,
        'description': 'Test active session',
        'category': 'research',
        'start_time': start_time.isoformat()
        # No end_time = active session
    }
    
    print("\n🧪 Testing active session creation...")
    
    try:
        response = requests.post(f'{BASE_URL}/sessions/create', json=test_session)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Success! Created active session #{data['session_id']}")
            print(f"   End time: {data['end_time']} (should be None)")
            print(f"   Duration: {data['duration_minutes']} (should be None)")
            return True
        else:
            print(f"❌ Error: {response.status_code} - {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Network error: {e}")
        return False

def test_validation_errors():
    """Test validation error handling"""
    
    print("\n🧪 Testing validation errors...")
    
    # Test missing required fields
    invalid_session = {
        'project': PROJECT_NAME,
        'description': 'Test missing start time'
        # Missing start_time
    }
    
    try:
        response = requests.post(f'{BASE_URL}/sessions/create', json=invalid_session)
        
        if response.status_code == 400:
            print("✅ Correctly rejected session with missing start time")
        else:
            print(f"❌ Expected 400 error, got {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Network error: {e}")
        return False
    
    # Test invalid datetime format
    invalid_session = {
        'project': PROJECT_NAME,
        'description': 'Test invalid datetime',
        'start_time': 'invalid-datetime'
    }
    
    try:
        response = requests.post(f'{BASE_URL}/sessions/create', json=invalid_session)
        
        if response.status_code == 400:
            print("✅ Correctly rejected session with invalid datetime")
        else:
            print(f"❌ Expected 400 error, got {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Network error: {e}")
        return False
    
    return True

def main():
    """Run all tests"""
    print("🚀 Testing Historical Session Creation API")
    print("=" * 50)
    
    tests = [
        test_create_historical_session,
        test_create_session_with_duration,
        test_create_active_session,
        test_validation_errors
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Historical session creation is working correctly.")
    else:
        print("⚠️  Some tests failed. Please check the implementation.")

if __name__ == "__main__":
    main() 