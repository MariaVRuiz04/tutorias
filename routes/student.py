from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from models.user import User, Availability, TutoringRequest, Notification
from extensions import db
from forms.tutoring_request_form import TutoringRequestForm
from datetime import datetime, time

student_bp = Blueprint('student', __name__, url_prefix='/student')

# Student route protection
@student_bp.before_request
def check_student():
    if not current_user.is_authenticated or current_user.role != 'student':
        flash('Access denied. Student privileges required.', 'danger')
        return redirect(url_for('main.index'))

@student_bp.route('/dashboard')
@login_required
def dashboard():
    # Get pending tutoring requests
    pending_requests = TutoringRequest.query.filter_by(
        student_id=current_user.id, 
        status='pending'
    ).order_by(TutoringRequest.created_at.desc()).all()
    
    # Get upcoming accepted tutoring sessions
    today = datetime.now().date()
    upcoming_sessions = TutoringRequest.query.filter(
        TutoringRequest.student_id == current_user.id,
        TutoringRequest.status == 'accepted',
        TutoringRequest.requested_date >= today
    ).order_by(TutoringRequest.requested_date, TutoringRequest.requested_time).all()
    
    # Get unread notifications
    unread_notifications = Notification.query.filter_by(
        user_id=current_user.id,
        is_read=False
    ).order_by(Notification.created_at.desc()).all()
    
    return render_template(
        'student/dashboard.html',
        title='Student Dashboard',
        pending_requests=pending_requests,
        upcoming_sessions=upcoming_sessions,
        notifications=unread_notifications
    )

@student_bp.route('/professors')
@login_required
def view_professors():
    professors = User.query.filter_by(role='professor').all()
    return render_template(
        'student/professors.html',
        title='Available Professors',
        professors=professors
    )

@student_bp.route('/professor/<int:professor_id>')
@login_required
def professor_detail(professor_id):
    professor = User.query.filter_by(id=professor_id, role='professor').first_or_404()
    
    # Get professor's availability
    availabilities = Availability.query.filter_by(professor_id=professor_id).all()
    
    return render_template(
        'student/professor_detail.html',
        title=f'Professor {professor.get_full_name()}',
        professor=professor,
        availabilities=availabilities
    )

@student_bp.route('/request-tutoring/<int:professor_id>', methods=['GET', 'POST'])
@login_required
def request_tutoring(professor_id):
    professor = User.query.filter_by(id=professor_id, role='professor').first_or_404()
    
    form = TutoringRequestForm()
    
    if form.validate_on_submit():
        new_request = TutoringRequest(
            student_id=current_user.id,
            professor_id=professor.id,
            subject=form.subject.data,
            message=form.message.data,
            requested_date=form.requested_date.data,
            requested_time=form.requested_time.data,
            status='pending'
        )
        
        db.session.add(new_request)
        db.session.commit()
        
        flash(f'Tutoring request sent to Professor {professor.get_full_name()}.', 'success')
        return redirect(url_for('student.dashboard'))
    
    return render_template(
        'student/request_tutoring.html',
        title='Request Tutoring Session',
        form=form,
        professor=professor
    )

@student_bp.route('/tutoring-requests')
@login_required
def tutoring_requests():
    pending = TutoringRequest.query.filter_by(
        student_id=current_user.id, 
        status='pending'
    ).order_by(TutoringRequest.created_at.desc()).all()
    
    accepted = TutoringRequest.query.filter_by(
        student_id=current_user.id, 
        status='accepted'
    ).order_by(TutoringRequest.requested_date, TutoringRequest.requested_time).all()
    
    completed = TutoringRequest.query.filter_by(
        student_id=current_user.id, 
        status='completed'
    ).order_by(TutoringRequest.updated_at.desc()).limit(10).all()
    
    rejected = TutoringRequest.query.filter_by(
        student_id=current_user.id, 
        status='rejected'
    ).order_by(TutoringRequest.updated_at.desc()).limit(10).all()
    
    return render_template(
        'student/tutoring_requests.html',
        title='My Tutoring Requests',
        pending=pending,
        accepted=accepted,
        completed=completed,
        rejected=rejected
    )

@student_bp.route('/notifications')
@login_required
def notifications():
    notifications = Notification.query.filter_by(
        user_id=current_user.id
    ).order_by(Notification.created_at.desc()).all()
    
    # Mark all as read
    for notification in notifications:
        notification.is_read = True
    
    db.session.commit()
    
    return render_template(
        'student/notifications.html',
        title='Notifications',
        notifications=notifications
    )

@student_bp.route('/mark-notification-read/<int:notification_id>', methods=['POST'])
@login_required
def mark_notification_read(notification_id):
    notification = Notification.query.get_or_404(notification_id)
    
    # Check if it belongs to current student
    if notification.user_id != current_user.id:
        flash('Permission denied.', 'danger')
        return redirect(url_for('student.dashboard'))
    
    notification.is_read = True
    db.session.commit()
    
    return redirect(url_for('student.notifications'))