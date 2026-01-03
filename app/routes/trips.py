from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_login import login_required, current_user
from app.models import db, Trip, Budget
from app.forms import TripForm
from werkzeug.utils import secure_filename
from datetime import date
import os

bp = Blueprint('trips', __name__)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']

@bp.route('/')
@login_required
def list():
    status_filter = request.args.get('status', 'all')
    today = date.today()
    
    query = Trip.query.filter_by(user_id=current_user.id)
    
    if status_filter == 'ongoing':
        query = query.filter(Trip.start_date <= today, Trip.end_date >= today)
    elif status_filter == 'upcoming':
        query = query.filter(Trip.start_date > today)
    elif status_filter == 'completed':
        query = query.filter(Trip.end_date < today)
    
    trips = query.order_by(Trip.start_date.desc()).all()
    
    return render_template('trips/list.html', trips=trips, status_filter=status_filter)

@bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    form = TripForm()
    if form.validate_on_submit():
        trip = Trip(
            user_id=current_user.id,
            name=form.name.data,
            description=form.description.data,
            start_date=form.start_date.data,
            end_date=form.end_date.data
        )
        
        # Handle cover image upload
        if form.cover_image.data:
            file = form.cover_image.data
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                filename = f"{current_user.id}_{trip.name.replace(' ', '_')}_{filename}"
                filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
                file.save(filepath)
                trip.cover_image_url = f"/static/images/{filename}"
        
        db.session.add(trip)
        db.session.commit()
        
        # Create default budget
        budget = Budget(trip_id=trip.id)
        db.session.add(budget)
        db.session.commit()
        
        flash('Trip created successfully!', 'success')
        return redirect(url_for('trips.view', id=trip.id))
    
    return render_template('trips/create.html', form=form)

@bp.route('/<int:id>')
@login_required
def view(id):
    trip = Trip.query.get_or_404(id)
    if trip.user_id != current_user.id:
        flash('You do not have permission to view this trip.', 'danger')
        return redirect(url_for('trips.list'))
    
    return render_template('trips/view.html', trip=trip)

@bp.route('/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit(id):
    trip = Trip.query.get_or_404(id)
    if trip.user_id != current_user.id:
        flash('You do not have permission to edit this trip.', 'danger')
        return redirect(url_for('trips.list'))
    
    form = TripForm(obj=trip)
    if form.validate_on_submit():
        trip.name = form.name.data
        trip.description = form.description.data
        trip.start_date = form.start_date.data
        trip.end_date = form.end_date.data
        
        # Handle cover image upload
        if form.cover_image.data:
            file = form.cover_image.data
            if file and allowed_file(file.filename):
                # Delete old image if exists
                if trip.cover_image_url:
                    old_path = os.path.join(current_app.config['UPLOAD_FOLDER'], 
                                          trip.cover_image_url.split('/')[-1])
                    if os.path.exists(old_path):
                        os.remove(old_path)
                
                filename = secure_filename(file.filename)
                filename = f"{current_user.id}_{trip.name.replace(' ', '_')}_{filename}"
                filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
                file.save(filepath)
                trip.cover_image_url = f"/static/images/{filename}"
        
        db.session.commit()
        flash('Trip updated successfully!', 'success')
        return redirect(url_for('trips.view', id=trip.id))
    
    return render_template('trips/edit.html', form=form, trip=trip)

@bp.route('/<int:id>/delete', methods=['POST'])
@login_required
def delete(id):
    trip = Trip.query.get_or_404(id)
    if trip.user_id != current_user.id:
        flash('You do not have permission to delete this trip.', 'danger')
        return redirect(url_for('trips.list'))
    
    # Delete cover image if exists
    if trip.cover_image_url:
        old_path = os.path.join(current_app.config['UPLOAD_FOLDER'], 
                              trip.cover_image_url.split('/')[-1])
        if os.path.exists(old_path):
            os.remove(old_path)
    
    db.session.delete(trip)
    db.session.commit()
    flash('Trip deleted successfully!', 'success')
    return redirect(url_for('trips.list'))

