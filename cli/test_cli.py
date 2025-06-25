import pytest
import os
import tempfile
import yaml
from click.testing import CliRunner
from tt import cli

@pytest.fixture
def runner():
    """Create a Click test runner"""
    return CliRunner()

@pytest.fixture
def temp_project():
    """Create a temporary project directory with .timecfg"""
    temp_dir = tempfile.mkdtemp()
    config = {
        'project': {
            'name': 'Test Project',
            'type': 'development',
            'language': 'python'
        },
        'server': {
            'url': 'http://localhost:9000',
            'api_version': 'v1'
        },
        'tracking': {
            'categories': ['development', 'testing', 'documentation'],
            'default_category': 'development'
        }
    }
    
    config_path = os.path.join(temp_dir, '.timecfg')
    with open(config_path, 'w') as f:
        yaml.dump(config, f)
    
    yield temp_dir
    
    # Cleanup
    import shutil
    shutil.rmtree(temp_dir)

def test_cli_help(runner):
    """Test that CLI help works"""
    result = runner.invoke(cli, ['--help'])
    assert result.exit_code == 0
    assert 'Commands:' in result.output

def test_cli_init_help(runner):
    """Test that init command help works"""
    result = runner.invoke(cli, ['init', '--help'])
    assert result.exit_code == 0
    assert 'Initialize time tracking for this project' in result.output

def test_cli_start_help(runner):
    """Test that start command help works"""
    result = runner.invoke(cli, ['start', '--help'])
    assert result.exit_code == 0
    assert 'Start tracking time' in result.output

def test_cli_stop_help(runner):
    """Test that stop command help works"""
    result = runner.invoke(cli, ['stop', '--help'])
    assert result.exit_code == 0
    assert 'Stop tracking time' in result.output

def test_cli_status_help(runner):
    """Test that status command help works"""
    result = runner.invoke(cli, ['status', '--help'])
    assert result.exit_code == 0
    assert 'Show current tracking status' in result.output

def test_cli_break_help(runner):
    """Test that break command help works"""
    result = runner.invoke(cli, ['break', '--help'])
    assert result.exit_code == 0
    assert 'Start or end a break' in result.output

def test_cli_report_help(runner):
    """Test that report command help works"""
    result = runner.invoke(cli, ['report', '--help'])
    assert result.exit_code == 0
    assert 'Generate time tracking reports' in result.output

def test_cli_init_with_name(runner, temp_project):
    """Test initializing a project with a custom name"""
    with runner.isolated_filesystem():
        result = runner.invoke(cli, ['init', '--name', 'Custom Project Name'])
        assert result.exit_code == 0
        assert 'Custom Project Name' in result.output

def test_cli_init_without_name(runner, temp_project):
    """Test initializing a project without a custom name"""
    with runner.isolated_filesystem():
        # The init command requires a name, so it should prompt or fail
        result = runner.invoke(cli, ['init'], input='Test Project\n')
        assert result.exit_code == 0
        assert 'Project initialized' in result.output or 'Test Project' in result.output

def test_cli_start_missing_description(runner):
    """Test starting a session without description"""
    result = runner.invoke(cli, ['start'])
    assert result.exit_code != 0  # Should fail without description

def test_cli_start_with_description(runner):
    """Test starting a session with description"""
    with runner.isolated_filesystem():
        result = runner.invoke(cli, ['start', 'Test session'])
        # This should fail because no .timecfg is found
        assert result.exit_code != 0  # Expected to fail without config

def test_cli_start_with_category(runner):
    """Test starting a session with category"""
    with runner.isolated_filesystem():
        result = runner.invoke(cli, ['start', 'Test session', '-c', 'testing'])
        # This should fail because no .timecfg is found
        assert result.exit_code != 0  # Expected to fail without config

def test_cli_stop_no_server(runner):
    """Test stopping a session without server running"""
    with runner.isolated_filesystem():
        result = runner.invoke(cli, ['stop'])
        # This should fail because no .timecfg is found
        assert result.exit_code != 0  # Expected to fail without config

def test_cli_status_no_server(runner):
    """Test status without server running"""
    with runner.isolated_filesystem():
        result = runner.invoke(cli, ['status'])
        # This should fail because no .timecfg is found
        assert result.exit_code != 0  # Expected to fail without config

def test_cli_break_no_server(runner):
    """Test break without server running"""
    with runner.isolated_filesystem():
        result = runner.invoke(cli, ['break', 'coffee'])
        # This should fail because no .timecfg is found
        assert result.exit_code != 0  # Expected to fail without config

def test_cli_report_no_server(runner):
    """Test report without server running"""
    with runner.isolated_filesystem():
        result = runner.invoke(cli, ['report', 'today'])
        # This should fail because no .timecfg is found
        assert result.exit_code != 0  # Expected to fail without config 