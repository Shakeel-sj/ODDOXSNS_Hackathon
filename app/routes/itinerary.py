from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from app.models import db, Trip, TripStop, ItineraryDay, ItineraryActivity, Activity, City
from app.forms import TripStopForm, ItineraryActivityForm
from datetime import datetime, timedelta

bp = Blueprint('itinerary', __name__)

@bp.route('/trip/<int:trip_id>')
@login_required
def builder(trip_id):
    trip = Trip.query.get_or_404(trip_id)
    if trip.user_id != current_user.id:
        flash('You do not have permission to view this trip.', 'danger')
        return redirect(url_for('trips.list'))
    
    # Get all cities for dropdown
    cities = City.query.order_by(City.name).all()
    
    # Get all activities for dropdown
    activities = Activity.query.order_by(Activity.name).all()
    
    return render_template('itinerary/builder.html', trip=trip, cities=cities, activities=activities)

@bp.route('/trip/<int:trip_id>/view')
@login_required
def view(trip_id):
    trip = Trip.query.get_or_404(trip_id)
    if trip.user_id != current_user.id:
        flash('You do not have permission to view this trip.', 'danger')
        return redirect(url_for('trips.list'))
    
    return render_template('itinerary/view.html', trip=trip)

@bp.route('/trip/<int:trip_id>/add-stop', methods=['POST'])
@login_required
def add_stop(trip_id):
    trip = Trip.query.get_or_404(trip_id)
    if trip.user_id != current_user.id:
        return jsonify({'error': 'Permission denied'}), 403
    
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    # Validate required fields
    if not data.get('city_id'):
        return jsonify({'error': 'City is required'}), 400
    if not data.get('arrival_date'):
        return jsonify({'error': 'Arrival date is required'}), 400
    if not data.get('departure_date'):
        return jsonify({'error': 'Departure date is required'}), 400
    
    try:
        # Convert string dates to date objects
        arrival_date = datetime.strptime(data['arrival_date'], '%Y-%m-%d').date()
        departure_date = datetime.strptime(data['departure_date'], '%Y-%m-%d').date()
    except ValueError as e:
        return jsonify({'error': f'Invalid date format: {str(e)}'}), 400
    
    # Check if dates are within trip dates
    if arrival_date < trip.start_date or departure_date > trip.end_date:
        return jsonify({'error': f'Stop dates must be within trip dates ({trip.start_date} to {trip.end_date})'}), 400
    
    if arrival_date > departure_date:
        return jsonify({'error': 'Arrival date must be before or equal to departure date'}), 400
    
    # Validate city exists
    city = City.query.get(data['city_id'])
    if not city:
        return jsonify({'error': 'City not found'}), 404
    
    try:
        # Get max order_index
        max_order = db.session.query(db.func.max(TripStop.order_index)).filter_by(trip_id=trip_id).scalar() or 0
        
        stop = TripStop(
            trip_id=trip_id,
            city_id=data['city_id'],
            arrival_date=arrival_date,
            departure_date=departure_date,
            order_index=max_order + 1,
            notes=data.get('notes', '')
        )
        db.session.add(stop)
        db.session.flush()
        
        # Create itinerary days for this stop
        current_date = arrival_date
        day_number = 1
        while current_date <= departure_date:
            day = ItineraryDay(
                trip_stop_id=stop.id,
                date=current_date,
                day_number=day_number
            )
            db.session.add(day)
            current_date += timedelta(days=1)
            day_number += 1
        
        db.session.commit()
        return jsonify({'success': True, 'stop_id': stop.id})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Database error: {str(e)}'}), 500

@bp.route('/stop/<int:stop_id>/delete', methods=['POST'])
@login_required
def delete_stop(stop_id):
    stop = TripStop.query.get_or_404(stop_id)
    trip = stop.trip
    if trip.user_id != current_user.id:
        return jsonify({'error': 'Permission denied'}), 403
    
    db.session.delete(stop)
    db.session.commit()
    return jsonify({'success': True})

@bp.route('/stop/<int:stop_id>/reorder', methods=['POST'])
@login_required
def reorder_stop(stop_id):
    stop = TripStop.query.get_or_404(stop_id)
    trip = stop.trip
    if trip.user_id != current_user.id:
        return jsonify({'error': 'Permission denied'}), 403
    
    new_order = request.json.get('order_index')
    if new_order is None:
        return jsonify({'error': 'order_index required'}), 400
    
    stop.order_index = new_order
    db.session.commit()
    return jsonify({'success': True})

@bp.route('/day/<int:day_id>/add-activity', methods=['POST'])
@login_required
def add_activity(day_id):
    day = ItineraryDay.query.get_or_404(day_id)
    trip = day.trip_stop.trip
    if trip.user_id != current_user.id:
        return jsonify({'error': 'Permission denied'}), 403
    
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    if not data.get('activity_id'):
        return jsonify({'error': 'Activity is required'}), 400
    
    # Validate activity exists
    activity = Activity.query.get(data['activity_id'])
    if not activity:
        return jsonify({'error': 'Activity not found'}), 404
    
    # Convert time string to time object if provided
    start_time = None
    if 'start_time' in data and data['start_time']:
        try:
            start_time = datetime.strptime(data['start_time'], '%H:%M').time()
        except ValueError:
            return jsonify({'error': 'Invalid time format. Use HH:MM'}), 400
    
    try:
        # Get max order_index for this day
        max_order = db.session.query(db.func.max(ItineraryActivity.order_index)).filter_by(itinerary_day_id=day_id).scalar() or 0
        
        itinerary_activity = ItineraryActivity(
            itinerary_day_id=day_id,
            activity_id=data['activity_id'],
            start_time=start_time,
            actual_cost=float(data['actual_cost']) if data.get('actual_cost') else None,
            notes=data.get('notes', ''),
            order_index=max_order + 1
        )
        db.session.add(itinerary_activity)
        db.session.commit()
        return jsonify({'success': True, 'activity_id': itinerary_activity.id})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Database error: {str(e)}'}), 500

@bp.route('/activity/<int:activity_id>/delete', methods=['POST'])
@login_required
def delete_activity(activity_id):
    activity = ItineraryActivity.query.get_or_404(activity_id)
    trip = activity.itinerary_day.trip_stop.trip
    if trip.user_id != current_user.id:
        return jsonify({'error': 'Permission denied'}), 403
    
    db.session.delete(activity)
    db.session.commit()
    return jsonify({'success': True})

@bp.route('/activity/<int:activity_id>/reorder', methods=['POST'])
@login_required
def reorder_activity(activity_id):
    activity = ItineraryActivity.query.get_or_404(activity_id)
    trip = activity.itinerary_day.trip_stop.trip
    if trip.user_id != current_user.id:
        return jsonify({'error': 'Permission denied'}), 403
    
    new_order = request.json.get('order_index')
    if new_order is None:
        return jsonify({'error': 'order_index required'}), 400
    
    activity.order_index = new_order
    db.session.commit()
    return jsonify({'success': True})

