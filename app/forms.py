from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, TextAreaField, DateField, TimeField, DecimalField, SelectField, BooleanField, IntegerField
from wtforms.validators import DataRequired, Email, Length, EqualTo, Optional, NumberRange, ValidationError
from app.models import User

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')

class SignupForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email(), Length(max=120)])
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=80)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    password2 = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password', message='Passwords must match')])
    full_name = StringField('Full Name', validators=[Optional(), Length(max=100)])
    
    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Email already registered. Please use a different email.')
    
    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Username already taken. Please choose a different username.')

class ForgotPasswordForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])

class TripForm(FlaskForm):
    name = StringField('Trip Name', validators=[DataRequired(), Length(max=200)])
    description = TextAreaField('Description', validators=[Optional()])
    start_date = DateField('Start Date', validators=[DataRequired()])
    end_date = DateField('End Date', validators=[DataRequired()])
    cover_image = FileField('Cover Image', validators=[Optional(), FileAllowed(['jpg', 'jpeg', 'png', 'gif', 'webp'], 'Images only!')])
    
    def validate_end_date(self, end_date):
        if self.start_date.data and end_date.data:
            if end_date.data < self.start_date.data:
                raise ValidationError('End date must be after start date.')

class CitySearchForm(FlaskForm):
    query = StringField('Search', validators=[Optional()])
    country = StringField('Country', validators=[Optional()])
    region = StringField('Region', validators=[Optional()])

class ActivitySearchForm(FlaskForm):
    query = StringField('Search', validators=[Optional()])
    activity_type = SelectField('Type', choices=[
        ('', 'All Types'),
        ('Sightseeing', 'Sightseeing'),
        ('Food', 'Food'),
        ('Adventure', 'Adventure'),
        ('Culture', 'Culture'),
        ('Nightlife', 'Nightlife'),
        ('Shopping', 'Shopping'),
        ('Nature', 'Nature'),
        ('Sports', 'Sports'),
        ('Other', 'Other')
    ], validators=[Optional()])
    min_cost = DecimalField('Min Cost', validators=[Optional(), NumberRange(min=0)])
    max_cost = DecimalField('Max Cost', validators=[Optional(), NumberRange(min=0)])
    max_duration = DecimalField('Max Duration (hours)', validators=[Optional(), NumberRange(min=0)])

class TripStopForm(FlaskForm):
    city_id = IntegerField('City', validators=[DataRequired()])
    arrival_date = DateField('Arrival Date', validators=[DataRequired()])
    departure_date = DateField('Departure Date', validators=[DataRequired()])
    notes = TextAreaField('Notes', validators=[Optional()])

class ItineraryActivityForm(FlaskForm):
    activity_id = IntegerField('Activity', validators=[DataRequired()])
    start_time = TimeField('Start Time', validators=[Optional()], format='%H:%M')
    actual_cost = DecimalField('Actual Cost', validators=[Optional(), NumberRange(min=0)])
    notes = TextAreaField('Notes', validators=[Optional()])

class BudgetForm(FlaskForm):
    transport_budget = DecimalField('Transport Budget', validators=[Optional(), NumberRange(min=0)])
    accommodation_budget = DecimalField('Accommodation Budget', validators=[Optional(), NumberRange(min=0)])
    activities_budget = DecimalField('Activities Budget', validators=[Optional(), NumberRange(min=0)])
    meals_budget = DecimalField('Meals Budget', validators=[Optional(), NumberRange(min=0)])
    other_budget = DecimalField('Other Budget', validators=[Optional(), NumberRange(min=0)])

class BudgetExpenseForm(FlaskForm):
    category = SelectField('Category', choices=[
        ('Transport', 'Transport'),
        ('Accommodation', 'Accommodation'),
        ('Activities', 'Activities'),
        ('Meals', 'Meals'),
        ('Other', 'Other')
    ], validators=[DataRequired()])
    amount = DecimalField('Amount', validators=[DataRequired(), NumberRange(min=0.01)])
    description = StringField('Description', validators=[Optional(), Length(max=255)])
    date = DateField('Date', validators=[DataRequired()], format='%Y-%m-%d')

class ProfileForm(FlaskForm):
    full_name = StringField('Full Name', validators=[Optional(), Length(max=100)])
    email = StringField('Email', validators=[DataRequired(), Email(), Length(max=120)])
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=80)])
    language_preference = SelectField('Language', choices=[
        ('en', 'English'),
        ('es', 'Spanish'),
        ('fr', 'French'),
        ('de', 'German'),
        ('it', 'Italian'),
        ('pt', 'Portuguese'),
        ('ja', 'Japanese'),
        ('zh', 'Chinese')
    ], validators=[Optional()])
    avatar = FileField('Avatar', validators=[Optional(), FileAllowed(['jpg', 'jpeg', 'png', 'gif', 'webp'], 'Images only!')])
    
    def __init__(self, original_email, original_username, *args, **kwargs):
        super(ProfileForm, self).__init__(*args, **kwargs)
        self.original_email = original_email
        self.original_username = original_username
    
    def validate_email(self, email):
        if email.data != self.original_email:
            user = User.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError('Email already registered. Please use a different email.')
    
    def validate_username(self, username):
        if username.data != self.original_username:
            user = User.query.filter_by(username=username.data).first()
            if user:
                raise ValidationError('Username already taken. Please choose a different username.')

class AdminUserForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email(), Length(max=120)])
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=80)])
    full_name = StringField('Full Name', validators=[Optional(), Length(max=100)])
    role = SelectField('Role', choices=[('User', 'User'), ('Admin', 'Admin')], validators=[DataRequired()])
    language_preference = SelectField('Language', choices=[
        ('en', 'English'),
        ('es', 'Spanish'),
        ('fr', 'French'),
        ('de', 'German'),
        ('it', 'Italian'),
        ('pt', 'Portuguese'),
        ('ja', 'Japanese'),
        ('zh', 'Chinese')
    ], validators=[Optional()])

