from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_login import login_required, current_user
from app.models import db, User, SavedDestination, City
from app.forms import ProfileForm
from werkzeug.utils import secure_filename
import os

bp = Blueprint('profile', __name__)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']

@bp.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    form = ProfileForm(original_email=current_user.email, original_username=current_user.username, obj=current_user)
    
    if form.validate_on_submit():
        current_user.full_name = form.full_name.data
        current_user.email = form.email.data
        current_user.username = form.username.data
        current_user.language_preference = form.language_preference.data
        
        # Handle avatar upload
        if form.avatar.data:
            file = form.avatar.data
            if file and allowed_file(file.filename):
                # Delete old avatar if exists
                if current_user.avatar_url:
                    old_path = os.path.join(current_app.config['UPLOAD_FOLDER'], 
                                          current_user.avatar_url.split('/')[-1])
                    if os.path.exists(old_path):
                        os.remove(old_path)
                
                filename = secure_filename(file.filename)
                filename = f"avatar_{current_user.id}_{filename}"
                filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
                file.save(filepath)
                current_user.avatar_url = f"/static/images/{filename}"
        
        db.session.commit()
        flash('Profile updated successfully!', 'success')
        return redirect(url_for('profile.settings'))
    
    # Get saved destinations
    saved_destinations = City.query.join(SavedDestination).filter(
        SavedDestination.user_id == current_user.id
    ).all()
    
    return render_template('profile/settings.html', form=form, saved_destinations=saved_destinations)

@bp.route('/delete-account', methods=['POST'])
@login_required
def delete_account():
    # Delete user's avatar if exists
    if current_user.avatar_url:
        old_path = os.path.join(current_app.config['UPLOAD_FOLDER'], 
                              current_user.avatar_url.split('/')[-1])
        if os.path.exists(old_path):
            os.remove(old_path)
    
    # Delete user (cascade will handle related data)
    db.session.delete(current_user)
    db.session.commit()
    
    flash('Your account has been deleted.', 'info')
    return redirect(url_for('auth.login'))

@bp.route('/saved-destinations/<int:city_id>/remove', methods=['POST'])
@login_required
def remove_saved_destination(city_id):
    saved = SavedDestination.query.filter_by(user_id=current_user.id, city_id=city_id).first()
    if saved:
        db.session.delete(saved)
        db.session.commit()
        flash('Destination removed from saved list.', 'success')
    else:
        flash('Destination not found in saved list.', 'warning')
    
    return redirect(url_for('profile.settings'))

