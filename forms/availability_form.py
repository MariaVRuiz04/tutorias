from flask_wtf import FlaskForm
from wtforms import SelectField, TimeField, BooleanField, DateField, SubmitField
from wtforms.validators import DataRequired, ValidationError
from datetime import datetime

class AvailabilityForm(FlaskForm):
    day_of_week = SelectField('Day of the Week', 
                             choices=[(0, 'Monday'), (1, 'Tuesday'), (2, 'Wednesday'),
                                     (3, 'Thursday'), (4, 'Friday'), (5, 'Saturday'),
                                     (6, 'Sunday')],
                             coerce=int,
                             validators=[DataRequired()])
    start_time = TimeField('Start Time', format='%H:%M', validators=[DataRequired()])
    end_time = TimeField('End Time', format='%H:%M', validators=[DataRequired()])
    is_recurring = BooleanField('Recurring Weekly', default=True)
    specific_date = DateField('Specific Date', format='%Y-%m-%d', validators=[])
    submit = SubmitField('Add Availability')
    
    def validate_end_time(self, end_time):
        if self.start_time.data >= end_time.data:
            raise ValidationError('End time must be after start time')
        
    def validate_specific_date(self, specific_date):
        if not self.is_recurring.data and not specific_date.data:
            raise ValidationError('Specific date is required for non-recurring availability')
        
        if specific_date.data and specific_date.data < datetime.now().date():
            raise ValidationError('Date cannot be in the past')