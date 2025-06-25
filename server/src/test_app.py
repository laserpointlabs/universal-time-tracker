import pytest
import os
import tempfile
from app import app, db

@pytest.fixture
def client():
    """Create a test client for the Flask app"""
    # Use a temporary database for testing
    db_fd, db_path = tempfile.mkstemp()
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
    app.config['TESTING'] = True
    app.config['SECRET_KEY'] = 'test-secret-key'
    
    with app.test_client() as client:
        with app.app_context():
            # Initialize database with test configuration
            db.create_all()
            yield client
    
    # Cleanup
    os.close(db_fd)
    os.unlink(db_path)

def test_health(client):
    """Test the health check endpoint"""
    response = client.get('/health')
    assert response.status_code == 200
    data = response.get_json()
    assert data['status'] == 'healthy'
    assert 'timestamp' in data
    assert 'version' in data
    assert 'database' in data

def test_landing_page(client):
    """Test the landing page loads"""
    response = client.get('/')
    assert response.status_code == 200

def test_dashboard_page(client):
    """Test the dashboard page loads"""
    response = client.get('/dashboard')
    assert response.status_code == 200

def test_db_browser_index(client):
    """Test the database browser index page loads"""
    response = client.get('/db')
    assert response.status_code == 200

def test_api_projects_empty(client):
    """Test the projects API endpoint returns empty list initially"""
    response = client.get('/api/v1/projects')
    assert response.status_code == 200
    data = response.get_json()
    assert isinstance(data, list)

def test_api_sessions_status_missing_project(client):
    """Test sessions status API with missing project parameter"""
    response = client.get('/api/v1/sessions/status')
    assert response.status_code == 400
    data = response.get_json()
    assert 'error' in data

def test_api_sessions_status_nonexistent_project(client):
    """Test sessions status API with non-existent project"""
    response = client.get('/api/v1/sessions/status?project=NonExistentProject')
    assert response.status_code == 200
    data = response.get_json()
    assert data['project'] == 'NonExistentProject'
    assert data['active_session'] is None
    assert data['active_break'] is None
    assert data['daily_summary']['total_hours'] == 0

def test_api_start_session_missing_data(client):
    """Test starting a session with missing required data"""
    response = client.post('/api/v1/sessions/start', json={})
    assert response.status_code == 400
    data = response.get_json()
    assert 'error' in data

def test_api_start_session_success(client):
    """Test successfully starting a session"""
    session_data = {
        'project': 'Test Project',
        'description': 'Test session description',
        'category': 'testing'
    }
    response = client.post('/api/v1/sessions/start', json=session_data)
    assert response.status_code == 200
    data = response.get_json()
    assert 'session_id' in data
    assert data['project'] == 'Test Project'
    assert data['description'] == 'Test session description'
    assert data['category'] == 'testing'

def test_api_stop_session_nonexistent_project(client):
    """Test stopping a session for non-existent project"""
    response = client.post('/api/v1/sessions/stop', json={'project': 'NonExistentProject'})
    assert response.status_code == 404
    data = response.get_json()
    assert 'error' in data

def test_api_break_session_nonexistent_project(client):
    """Test break functionality for non-existent project"""
    response = client.post('/api/v1/sessions/break', json={'project': 'NonExistentProject'})
    assert response.status_code == 404
    data = response.get_json()
    assert 'error' in data

def test_api_analytics_heatmap_missing_project(client):
    """Test analytics heatmap with missing project parameter"""
    response = client.get('/api/v1/analytics/heatmap')
    assert response.status_code == 400
    data = response.get_json()
    assert 'error' in data

def test_api_analytics_category_breakdown_missing_project(client):
    """Test category breakdown with missing project parameter"""
    response = client.get('/api/v1/analytics/category-breakdown')
    assert response.status_code == 400
    data = response.get_json()
    assert 'error' in data

def test_api_reports_invalid_period(client):
    """Test reports API with invalid period"""
    response = client.get('/api/v1/reports/invalid')
    assert response.status_code == 400
    data = response.get_json()
    assert 'error' in data

def test_api_reports_valid_periods(client):
    """Test reports API with valid periods"""
    for period in ['today', 'week', 'month']:
        response = client.get(f'/api/v1/reports/{period}')
        assert response.status_code == 200
        data = response.get_json()
        assert 'total_hours' in data
        assert 'sessions' in data
        assert 'category_breakdown' in data
        assert 'project_breakdown' in data

def test_prompt_editor_page(client):
    """Test the prompt editor page loads"""
    response = client.get('/prompt-editor')
    assert response.status_code == 200

def test_api_ai_prompt_get(client):
    """Test getting the AI prompt"""
    response = client.get('/api/v1/prompts/ai-recommendations')
    assert response.status_code == 200
    data = response.get_json()
    assert 'prompt' in data

def test_api_ai_prompt_test_missing_data(client):
    """Test AI prompt testing with missing data"""
    response = client.post('/api/v1/prompts/ai-recommendations/test', json={})
    assert response.status_code == 400
    data = response.get_json()
    assert 'error' in data

def test_api_ai_prompt_test_success(client):
    """Test AI prompt testing with valid data"""
    test_data = {'prompt': 'Test prompt with {project} and {total_hours}'}
    response = client.post('/api/v1/prompts/ai-recommendations/test', json=test_data)
    assert response.status_code == 200
    data = response.get_json()
    assert 'message' in data
    assert 'formatted_prompt' in data
    assert 'sample_data' in data 