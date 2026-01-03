"""Custom validators for Flask-WTF forms"""

from wtforms.validators import ValidationError
from app.models import User, City

def validate_email_unique(form, field):
    """Validate that email is unique"""
    user = User.query.filter_by(email=field.data).first()
    if user and (not form.user_id or user.id != form.user_id):
        raise ValidationError('Email already registered.')

def validate_username_unique(form, field):
    """Validate that username is unique"""
    user = User.query.filter_by(username=field.data).first()
    if user and (not form.user_id or user.id != form.user_id):
        raise ValidationError('Username already taken.')

def validate_dates_order(form, field):
    """Validate that end date is after start date"""
    if form.start_date.data and field.data:
        if field.data < form.start_date.data:
            raise ValidationError('End date must be after start date.')

def validate_city_exists(form, field):
    """Validate that city exists"""
    if field.data:
        city = City.query.get(field.data)
        if not city:
            raise ValidationError('City not found.')

