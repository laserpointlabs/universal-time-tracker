"""
Database models for Universal Time Tracker
"""

from datetime import datetime
import json

# db will be initialized in app.py
db = None

class Project:
    __tablename__ = 'projects'
    
    def __init__(self, db_instance):
        global db
        db = db_instance
        
        self.id = db.Column(db.Integer, primary_key=True)
        self.name = db.Column(db.String(200), unique=True, nullable=False)
        self.type = db.Column(db.String(50), default='development')
        self.language = db.Column(db.String(50))
        self.framework = db.Column(db.String(50))
        self.path = db.Column(db.Text)
        self.git_remote = db.Column(db.Text)
        self.created_at = db.Column(db.DateTime, default=datetime.now)
        self.last_activity = db.Column(db.DateTime, default=datetime.now)
        self.parent_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=True)
        self.userid = db.Column(db.String(100), nullable=False)
        
        # Relationships
        self.sessions = db.relationship('Session', backref='project', lazy=True, cascade='all, delete-orphan')
        self.subprojects = db.relationship('Project', backref=db.backref('parent', remote_side=[id]), lazy=True)

def create_models(db_instance):
    """Create all model classes with the database instance"""
    global db
    db = db_instance
    
    class Project(db.Model):
        __tablename__ = 'projects'
        
        id = db.Column(db.Integer, primary_key=True)
        name = db.Column(db.String(200), unique=True, nullable=False)
        type = db.Column(db.String(50), default='development')
        language = db.Column(db.String(50))
        framework = db.Column(db.String(50))
        path = db.Column(db.Text)
        git_remote = db.Column(db.Text)
        created_at = db.Column(db.DateTime, default=datetime.now)
        last_activity = db.Column(db.DateTime, default=datetime.now)
        parent_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=True)
        userid = db.Column(db.String(100), nullable=False)
        
        # Relationships
        sessions = db.relationship('Session', backref='project', lazy=True, cascade='all, delete-orphan')
        subprojects = db.relationship('Project', backref=db.backref('parent', remote_side=[id]), lazy=True)
        
        @property
        def is_parent(self):
            """Check if this project has subprojects"""
            return len(self.subprojects) > 0
        
        @property
        def is_subproject(self):
            """Check if this project is a subproject"""
            return self.parent_id is not None
        
        def get_total_duration(self):
            """Get total duration including subprojects"""
            total = sum(s.duration_minutes or 0 for s in self.sessions)
            for subproject in self.subprojects:
                total += subproject.get_total_duration()
            return total
        
        def __repr__(self):
            return f'<Project {self.name}>'

    class Session(db.Model):
        __tablename__ = 'sessions'
        
        id = db.Column(db.Integer, primary_key=True)
        project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False)
        start_time = db.Column(db.DateTime, default=datetime.now)
        end_time = db.Column(db.DateTime)
        duration_minutes = db.Column(db.Integer)
        category = db.Column(db.String(50), default='development')
        description = db.Column(db.Text, nullable=False)
        git_commits = db.Column(db.Text)  # JSON string
        userid = db.Column(db.String(100), nullable=False)
        
        # Relationships
        breaks = db.relationship('Break', backref='session', lazy=True, cascade='all, delete-orphan')
        
        @property
        def git_commits_list(self):
            """Get git commits as a list"""
            if self.git_commits:
                try:
                    return json.loads(self.git_commits)
                except:
                    return []
            return []
        
        @git_commits_list.setter
        def git_commits_list(self, value):
            """Set git commits from a list"""
            self.git_commits = json.dumps(value) if value else None
        
        def __repr__(self):
            return f'<Session {self.description[:50]}>'

    class Break(db.Model):
        __tablename__ = 'breaks'
        
        id = db.Column(db.Integer, primary_key=True)
        session_id = db.Column(db.Integer, db.ForeignKey('sessions.id'), nullable=False)
        start_time = db.Column(db.DateTime, default=datetime.now)
        end_time = db.Column(db.DateTime)
        duration_minutes = db.Column(db.Integer)
        break_type = db.Column(db.String(50), default='break')
        
        def __repr__(self):
            return f'<Break {self.break_type}>'
    
    return Project, Session, Break
