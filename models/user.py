from extensions import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

class User(db.Model, UserMixin):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    profile_pic = db.Column(db.String(150), default='default.jpg')
    role = db.Column(db.String(20), nullable=False)  # 'professor' or 'student'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    availability = db.relationship('Availability', backref='professor', lazy=True)
    tutoring_requests_sent = db.relationship('TutoringRequest', 
                                          foreign_keys='TutoringRequest.student_id',
                                          backref='student', lazy=True)
    tutoring_requests_received = db.relationship('TutoringRequest', 
                                              foreign_keys='TutoringRequest.professor_id',
                                              backref='professor', lazy=True)
    notifications = db.relationship('Notification', backref='user', lazy=True)
    
    def __init__(self, email, first_name, last_name, role, password):
        self.email = email
        self.first_name = first_name
        self.last_name = last_name
        self.role = role
        self.set_password(password)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"
    
    def __repr__(self):
        return f"<User {self.email} ({self.role})>"

# Availability model for professors
class Availability(db.Model):
    __tablename__ = 'availability'
    
    id = db.Column(db.Integer, primary_key=True)
    professor_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    day_of_week = db.Column(db.Integer, nullable=False)  # 0=Monday, 6=Sunday
    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time, nullable=False)
    is_recurring = db.Column(db.Boolean, default=True)
    specific_date = db.Column(db.Date, nullable=True)  # Only for non-recurring
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<Availability: {self.day_of_week} {self.start_time}-{self.end_time}>"

# Tutoring request model
class TutoringRequest(db.Model):
    __tablename__ = 'tutoring_requests'
    
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    professor_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    subject = db.Column(db.String(100), nullable=False)
    message = db.Column(db.Text, nullable=True)
    requested_date = db.Column(db.Date, nullable=False)
    requested_time = db.Column(db.Time, nullable=False)
    status = db.Column(db.String(20), default='pending')  # pending, accepted, rejected, completed
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<TutoringRequest: {self.subject} - {self.status}>"

# Notification model
class Notification(db.Model):
    __tablename__ = 'notifications'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    message = db.Column(db.Text, nullable=False)
    related_to = db.Column(db.String(50), nullable=True)  # Type of notification
    related_id = db.Column(db.Integer, nullable=True)  # ID of related entity
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<Notification: {self.message[:20]}...>"