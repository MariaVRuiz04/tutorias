from flask import Blueprint, render_template, redirect, url_for
from flask_login import current_user

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    if current_user.is_authenticated:
        if current_user.role == 'professor':
            return redirect(url_for('professor.dashboard'))
        else:
            return redirect(url_for('student.dashboard'))
    return render_template('index.html', title='Home')

@main_bp.route('/about')
def about():
    return render_template('about.html', title='About')