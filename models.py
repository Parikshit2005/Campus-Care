from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from flask_bcrypt import Bcrypt
from datetime import datetime

db = SQLAlchemy()
bcrypt = Bcrypt()

class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # student, faculty, authority
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def set_password(self, password):
        self.password = bcrypt.generate_password_hash(password).decode('utf-8')

    def check_password(self, password):
        return bcrypt.check_password_hash(self.password, password)

class Issue(db.Model):
    __tablename__ = 'issues'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    location = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    photo = db.Column(db.String(200), nullable=True)
    status = db.Column(db.String(30), default='Pending')
    priority = db.Column(db.String(20), default='Unset')
    faculty_observation = db.Column(db.Text, nullable=True)
    faculty_priority = db.Column(db.String(20), nullable=True)
    reported_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    assigned_to = db.Column(db.String(100), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    resolved_at = db.Column(db.DateTime, nullable=True)

    reporter = db.relationship('User', backref='issues')