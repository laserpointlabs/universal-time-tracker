import pytest
import sqlite3
import tempfile
import os
from unittest import mock

import db_browser

@pytest.fixture(scope='function')
def patch_db_browser(monkeypatch):
    # Create in-memory SQLite DB and initialize schema
    conn = sqlite3.connect(':memory:')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    # Create minimal schema for db_browser
    cursor.executescript('''
        CREATE TABLE projects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            type TEXT,
            language TEXT,
            framework TEXT,
            path TEXT,
            git_remote TEXT,
            created_at TEXT,
            last_activity TEXT,
            parent_id INTEGER,
            userid TEXT
        );
        CREATE TABLE sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id INTEGER,
            start_time TEXT,
            end_time TEXT,
            duration_minutes INTEGER,
            category TEXT,
            description TEXT,
            git_commits TEXT,
            userid TEXT
        );
        CREATE TABLE breaks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id INTEGER,
            start_time TEXT,
            end_time TEXT,
            duration_minutes INTEGER,
            break_type TEXT
        );
    ''')
    conn.commit()

    def get_test_db_connection():
        return conn

    monkeypatch.setattr(db_browser, 'get_db_connection', get_test_db_connection)
    yield
    conn.close()

@pytest.fixture(scope='function')
def patch_prompt_file(tmp_path, monkeypatch):
    # Create a temp prompt file
    prompt_file = tmp_path / 'ai_recommendations.txt'
    prompt_file.write_text('Test prompt content')
    # Patch the path in the app
    monkeypatch.setenv('PROMPT_FILE_PATH', str(prompt_file))
    yield str(prompt_file)
    # No cleanup needed, tmp_path is auto-removed 