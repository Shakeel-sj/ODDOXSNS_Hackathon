from flask import Blueprint, render_template, jsonify, redirect, flash
from flask_login import login_required, current_user
from app.models import Trip, ItineraryDay, ItineraryActivity
from datetime import datetime

bp = Blueprint('calendar', __name__)

def _get_activity_color(activity_type):
    colors = {
        'Sightseeing': '#3498db',
        'Food': '#e74c3c',
        'Adventure': '#2ecc71',
        'Culture': '#9b59b6',
        'Nightlife': '#34495e',
        'Shopping': '#f39c12',
        'Nature': '#1abc9c',
        'Sports': '#e67e22',
        'Other': '#95a5a6'
    }
    return colors.get(activity_type, '#95a5a6')

@bp.route('/trip/<int:trip_id>')
@login_required
def view(trip_id):
    trip = Trip.query.get_or_404(trip_id)
    if trip.user_id != current_user.id:
        flash('You do not have permission to view this trip.', 'danger')
        return redirect(url_for('trips.list'))
    
    return render_template('itinerary/calendar_view.html', trip=trip)

@bp.route('/trip/<int:trip_id>/events')
@login_required
def events(trip_id):
    trip = Trip.query.get_or_404(trip_id)
    if trip.user_id != current_user.id:
        return jsonify({'error': 'Permission denied'}), 403
    
    events_list = []
    for stop in trip.trip_stops:
        for day in stop.itinerary_days:
            for activity in day.activities:
                event = {
                    'id': activity.id,
                    'title': activity.activity.name,
                    'start': f"{day.date.isoformat()}T{activity.start_time.strftime('%H:%M:%S')}" if activity.start_time else day.date.isoformat(),
                    'allDay': not activity.start_time,
                    'backgroundColor': _get_activity_color(activity.activity.activity_type),
                    'borderColor': _get_activity_color(activity.activity.activity_type),
                    'extendedProps': {
                        'activity_type': activity.activity.activity_type,
                        'duration': float(activity.activity.duration_hours) if activity.activity.duration_hours else None,
                        'cost': float(activity.actual_cost) if activity.actual_cost else float(activity.activity.estimated_cost) if activity.activity.estimated_cost else None,
                        'notes': activity.notes,
                        'city': stop.city.name
                    }
                }
                events_list.append(event)
    
    return jsonify(events_list)

