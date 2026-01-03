"""Utility helper functions for GlobeTrotter"""

from datetime import datetime, date
from flask import current_app
import os
from werkzeug.utils import secure_filename

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']

def save_uploaded_file(file, prefix=''):
    """Save uploaded file and return the URL path"""
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        if prefix:
            filename = f"{prefix}_{filename}"
        filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        return f"/static/images/{filename}"
    return None

def delete_file(filepath):
    """Delete a file from the filesystem"""
    if filepath:
        full_path = os.path.join(current_app.config['UPLOAD_FOLDER'], 
                               filepath.split('/')[-1])
        if os.path.exists(full_path):
            os.remove(full_path)

def calculate_trip_duration(start_date, end_date):
    """Calculate trip duration in days"""
    if isinstance(start_date, str):
        start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
    if isinstance(end_date, str):
        end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
    return (end_date - start_date).days + 1

def format_currency(amount):
    """Format amount as currency"""
    return f"₹{amount:,.2f}"

def get_status_badge_class(status):
    """Get Bootstrap badge class for trip status"""
    status_classes = {
        'Upcoming': 'success',
        'Ongoing': 'warning',
        'Completed': 'secondary'
    }
    return status_classes.get(status, 'secondary')

