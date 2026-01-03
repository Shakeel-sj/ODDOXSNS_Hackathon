from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_login import login_required, current_user
from app.models import db, Trip, SharedLink, TripStop, ItineraryDay, ItineraryActivity, Budget
from datetime import datetime, timedelta
import secrets

bp = Blueprint('share', __name__)

@bp.route('/trip/<int:trip_id>/generate', methods=['POST'])
@login_required
def generate_link(trip_id):
    trip = Trip.query.get_or_404(trip_id)
    if trip.user_id != current_user.id:
        flash('You do not have permission to share this trip.', 'danger')
        return redirect(url_for('trips.list'))
    
    # Check if link already exists
    existing_link = SharedLink.query.filter_by(trip_id=trip_id, is_active=True).first()
    if existing_link:
        # Check if expired
        if existing_link.expires_at and existing_link.expires_at < datetime.utcnow():
            existing_link.is_active = False
            db.session.commit()
        else:
            share_url = request.url_root.rstrip('/') + url_for('share.public_view', token=existing_link.share_token)
            return redirect(url_for('trips.view', id=trip_id))
    
    # Generate new link
    token = secrets.token_urlsafe(32)
    expires_at = datetime.utcnow() + timedelta(days=30)  # 30 days expiry
    
    shared_link = SharedLink(
        trip_id=trip_id,
        share_token=token,
        is_active=True,
        expires_at=expires_at
    )
    db.session.add(shared_link)
    db.session.commit()
    
    flash('Share link generated successfully!', 'success')
    return redirect(url_for('trips.view', id=trip_id))

@bp.route('/trip/<int:trip_id>/revoke', methods=['POST'])
@login_required
def revoke_link(trip_id):
    trip = Trip.query.get_or_404(trip_id)
    if trip.user_id != current_user.id:
        flash('You do not have permission to revoke this link.', 'danger')
        return redirect(url_for('trips.list'))
    
    link = SharedLink.query.filter_by(trip_id=trip_id, is_active=True).first()
    if link:
        link.is_active = False
        db.session.commit()
        flash('Share link revoked successfully!', 'success')
    
    return redirect(url_for('trips.view', id=trip_id))

@bp.route('/<token>')
def public_view(token):
    link = SharedLink.query.filter_by(share_token=token, is_active=True).first_or_404()
    
    # Check if expired
    if link.expires_at and link.expires_at < datetime.utcnow():
        flash('This share link has expired.', 'warning')
        return redirect(url_for('auth.login'))
    
    trip = link.trip
    
    return render_template('share/public_itinerary.html', trip=trip, share_token=token)

@bp.route('/<token>/copy', methods=['POST'])
@login_required
def copy_trip(token):
    link = SharedLink.query.filter_by(share_token=token, is_active=True).first_or_404()
    
    if link.expires_at and link.expires_at < datetime.utcnow():
        flash('This share link has expired.', 'warning')
        return redirect(url_for('trips.list'))
    
    original_trip = link.trip
    
    # Create a copy of the trip
    new_trip = Trip(
        user_id=current_user.id,
        name=f"{original_trip.name} (Copy)",
        description=original_trip.description,
        start_date=original_trip.start_date,
        end_date=original_trip.end_date,
        cover_image_url=original_trip.cover_image_url
    )
    db.session.add(new_trip)
    db.session.flush()
    
    # Copy trip stops
    for stop in original_trip.trip_stops:
        new_stop = TripStop(
            trip_id=new_trip.id,
            city_id=stop.city_id,
            arrival_date=stop.arrival_date,
            departure_date=stop.departure_date,
            order_index=stop.order_index,
            notes=stop.notes
        )
        db.session.add(new_stop)
        db.session.flush()
        
        # Copy itinerary days
        for day in stop.itinerary_days:
            new_day = ItineraryDay(
                trip_stop_id=new_stop.id,
                date=day.date,
                day_number=day.day_number
            )
            db.session.add(new_day)
            db.session.flush()
            
            # Copy activities
            for activity in day.activities:
                new_activity = ItineraryActivity(
                    itinerary_day_id=new_day.id,
                    activity_id=activity.activity_id,
                    start_time=activity.start_time,
                    actual_cost=activity.actual_cost,
                    notes=activity.notes,
                    order_index=activity.order_index
                )
                db.session.add(new_activity)
    
    # Copy budget
    if original_trip.budget:
        new_budget = Budget(
            trip_id=new_trip.id,
            transport_budget=original_trip.budget.transport_budget,
            accommodation_budget=original_trip.budget.accommodation_budget,
            activities_budget=original_trip.budget.activities_budget,
            meals_budget=original_trip.budget.meals_budget,
            other_budget=original_trip.budget.other_budget
        )
        db.session.add(new_budget)
    
    db.session.commit()
    flash('Trip copied successfully!', 'success')
    return redirect(url_for('trips.view', id=new_trip.id))

