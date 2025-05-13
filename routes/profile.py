from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required, current_user
from models.user import User
from extensions import db
from forms.profile_form import ProfileUpdateForm
import os
from werkzeug.utils import secure_filename
from PIL import Image
import uuid

profile_bp = Blueprint('profile', __name__, url_prefix='/profile')

def save_profile_picture(form_picture):
    random_hex = uuid.uuid4().hex
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_filename = random_hex + f_ext
    picture_path = os.path.join(current_app.root_path, 'static/uploads/profile_pics', picture_filename)
    

    output_size = (150, 150)
    img = Image.open(form_picture)
    img.thumbnail(output_size)
    img.save(picture_path)
    
    return picture_filename

@profile_bp.route('/', methods=['GET', 'POST'])
@login_required
def profile():
    form = ProfileUpdateForm()
    
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_profile_picture(form.picture.data)
            current_user.profile_pic = picture_file
        
        current_user.first_name = form.first_name.data
        current_user.last_name = form.last_name.data
        
        db.session.commit()
        
        flash('Your profile has been updated!', 'success')
        return redirect(url_for('profile.profile'))
    elif request.method == 'GET':
        form.first_name.data = current_user.first_name
        form.last_name.data = current_user.last_name
    
    image_file = url_for('static', filename='uploads/profile_pics/' + current_user.profile_pic)
    
    return render_template(
        'profile/profile.html',
        title='Profile',
        form=form,
        image_file=image_file
    )