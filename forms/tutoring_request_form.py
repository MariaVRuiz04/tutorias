from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, TextAreaField, DateField, TimeField, SubmitField
from wtforms.validators import DataRequired, Length, ValidationError
from datetime import datetime

class TutoringRequestForm(FlaskForm):
    subject = StringField('Subject', validators=[DataRequired(), Length(min=2, max=100)])
    message = TextAreaField('Message', validators=[Length(max=500)])
    requested_date = DateField('Date', format='%Y-%m-%d', validators=[DataRequired()])
    requested_time = TimeField('Time', format='%H:%M', validators=[DataRequired()])
    submit = SubmitField('Send Request')
    
    def validate_requested_date(self, requested_date):
        if requested_date.data < datetime.now().date():
            raise ValidationError('Date cannot be in the past')

class UpdateTutoringRequestForm(FlaskForm):
    status = SelectField('Status', 
                        choices=[('pending', 'Pending'), 
                                ('accepted', 'Accept'), 
                                ('rejected', 'Reject'),
                                ('completed', 'Mark as Completed')],
                        validators=[DataRequired()])
    submit = SubmitField('Update Status')