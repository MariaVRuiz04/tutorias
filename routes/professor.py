from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from models.user import User, Availability, TutoringRequest, Notification
from extensions import db
from forms.availability_form import AvailabilityForm
from forms.tutoring_request_form import UpdateTutoringRequestForm
from datetime import datetime, time
import json

professor_bp = Blueprint('professor', __name__, url_prefix='/professor')

# Professor route protection
@professor_bp.before_request
def check_professor():
    if not current_user.is_authenticated or current_user.role != 'professor':
        flash('Access denied. Professor privileges required.', 'danger')
        return redirect(url_for('main.index'))

@professor_bp.route('/dashboard')
@login_required
def dashboard():
    # Get pending tutoring requests
    pending_requests = TutoringRequest.query.filter_by(
        professor_id=current_user.id, 
        status='pending'
    ).order_by(TutoringRequest.created_at.desc()).all()
    
    # Get upcoming accepted tutoring sessions
    today = datetime.now().date()
    upcoming_sessions = TutoringRequest.query.filter(
        TutoringRequest.professor_id == current_user.id,
        TutoringRequest.status == 'accepted',
        TutoringRequest.requested_date >= today
    ).order_by(TutoringRequest.requested_date, TutoringRequest.requested_time).all()
    
    # Get availability slots
    availability = Availability.query.filter_by(professor_id=current_user.id).all()
    
    return render_template(
        'professor/dashboard.html',
        title='Professor Dashboard',
        pending_requests=pending_requests,
        upcoming_sessions=upcoming_sessions,
        availability=availability
    )

@professor_bp.route('/availability', methods=['GET', 'POST'])
@login_required
def manage_availability():
    form = AvailabilityForm()
    
    if form.validate_on_submit():
        new_availability = Availability(
            professor_id=current_user.id,
            day_of_week=form.day_of_week.data,
            start_time=form.start_time.data,
            end_time=form.end_time.data,
            is_recurring=form.is_recurring.data,
            specific_date=form.specific_date.data if not form.is_recurring.data else None
        )
        
        db.session.add(new_availability)
        db.session.commit()
        
        # Notify students
        students = User.query.filter_by(role='student').all()
        for student in students:
            notification = Notification(
                user_id=student.id,
                message=f"Professor {current_user.get_full_name()} has added new availability!",
                related_to='availability',
                related_id=new_availability.id
            )
            db.session.add(notification)
        
        db.session.commit()
        
        flash('Availability added successfully!', 'success')
        return redirect(url_for('professor.manage_availability'))
    
    # Get current availability
    availabilities = Availability.query.filter_by(professor_id=current_user.id).all()
    
    return render_template(
        'professor/availability.html',
        title='Manage Availability',
        form=form,
        availabilities=availabilities
    )

@professor_bp.route('/availability/<int:availability_id>/delete', methods=['POST'])
@login_required
def delete_availability(availability_id):
    availability = Availability.query.get_or_404(availability_id)
    
    # Check if it belongs to current professor
    if availability.professor_id != current_user.id:
        flash('Permission denied.', 'danger')
        return redirect(url_for('professor.manage_availability'))
    
    db.session.delete(availability)
    db.session.commit()
    
    flash('Availability slot deleted.', 'success')
    return redirect(url_for('professor.manage_availability'))

@professor_bp.route('/tutoring-requests')
@login_required
def tutoring_requests():
    pending = TutoringRequest.query.filter_by(
        professor_id=current_user.id, 
        status='pending'
    ).order_by(TutoringRequest.created_at.desc()).all()
    
    accepted = TutoringRequest.query.filter_by(
        professor_id=current_user.id, 
        status='accepted'
    ).order_by(TutoringRequest.requested_date, TutoringRequest.requested_time).all()
    
    completed = TutoringRequest.query.filter_by(
        professor_id=current_user.id, 
        status='completed'
    ).order_by(TutoringRequest.updated_at.desc()).limit(10).all()
    
    rejected = TutoringRequest.query.filter_by(
        professor_id=current_user.id, 
        status='rejected'
    ).order_by(TutoringRequest.updated_at.desc()).limit(10).all()
    
    return render_template(
        'professor/tutoring_requests.html',
        title='Tutoring Requests',
        pending=pending,
        accepted=accepted,
        completed=completed,
        rejected=rejected
    )

@professor_bp.route('/tutoring-request/<int:request_id>/update', methods=['GET', 'POST'])
@login_required
def update_tutoring_request(request_id):
    tutoring_request = TutoringRequest.query.get_or_404(request_id)
    
    # Check if it belongs to current professor
    if tutoring_request.professor_id != current_user.id:
        flash('Permission denied.', 'danger')
        return redirect(url_for('professor.tutoring_requests'))
    
    form = UpdateTutoringRequestForm()
    
    if form.validate_on_submit():
        old_status = tutoring_request.status
        tutoring_request.status = form.status.data
        db.session.commit()
        
        # If status changed to accepted, notify student
        if old_status != 'accepted' and form.status.data == 'accepted':
            notification = Notification(
                user_id=tutoring_request.student_id,
                message=f"Your tutoring request for {tutoring_request.subject} has been accepted by Professor {current_user.get_full_name()}!",
                related_to='tutoring_request',
                related_id=tutoring_request.id
            )
            db.session.add(notification)
            db.session.commit()
        
        flash('Tutoring request updated.', 'success')
        return redirect(url_for('professor.tutoring_requests'))
    
    # Pre-populate form with current status
    form.status.data = tutoring_request.status
    student = User.query.get(tutoring_request.student_id)
    
    return render_template(
        'professor/update_request.html',
        title='Update Tutoring Request',
        form=form,
        request=tutoring_request,
        student=student
    )