from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField, DateField, TimeField, IntegerField, SelectField, FieldList, FormField
from wtforms.validators import DataRequired, Email, EqualTo, ValidationError, NumberRange, Length
from models import User

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(max=64)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField(
        'Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Please use a different username.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Please use a different email address.')

class NotificationTimeForm(FlaskForm):
    time = TimeField('Notification Time', validators=[DataRequired()])

class CourseForm(FlaskForm):
    medication = StringField('Medication Name', validators=[DataRequired()])
    dosage = StringField('Dosage (e.g., 500 mg)', validators=[DataRequired()])
    start = DateField('Start Date', validators=[DataRequired()])
    end_date = DateField('End Date', validators=[DataRequired()])
    frequency = IntegerField('Frequency (Days)', validators=[DataRequired(), NumberRange(min=1)])
    times_per_day = IntegerField('Times Per Day', validators=[DataRequired(), NumberRange(min=1, max=24)])
    submit = SubmitField('Save Course')
    notifications = FieldList(
        FormField(NotificationTimeForm), 
        min_entries=1
    )

class ReminderForm(FlaskForm):
    time = TimeField('Reminder Time', validators=[DataRequired()])
    notes = TextAreaField('Notes', validators=[Length(max=256)])
    submit = SubmitField('Save Reminder')

class NotificationSettingsForm(FlaskForm):
    enable_notifications = BooleanField('Enable Notifications')
    notification_time = TimeField('Default Notification Time', validators=[DataRequired()])
    submit = SubmitField('Save Settings')
