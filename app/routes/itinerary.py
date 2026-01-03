from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from app.models import db, Trip, TripStop, ItineraryDay, ItineraryActivity, Activity, City, Budget, BudgetExpense
from app.forms import TripStopForm, ItineraryActivityForm
from datetime import datetime, timedelta
from decimal import Decimal

bp = Blueprint('itinerary', __name__)

@bp.route('/trip/<int:trip_id>')
@login_required
def builder(trip_id):
    trip = Trip.query.get_or_404(trip_id)
    if trip.user_id != current_user.id:
        flash('You do not have permission to view this trip.', 'danger')
        return redirect(url_for('trips.list'))
    
    # Get initial data for better UX (optional - for showing popular cities/activities)
    popular_cities = City.query.order_by(City.name).limit(10).all()
    popular_activities = Activity.query.order_by(Activity.name).limit(10).all()
    
    return render_template('itinerary/builder.html', 
                         trip=trip, 
                         popular_cities=popular_cities,
                         popular_activities=popular_activities)

@bp.route('/api/cities', methods=['GET'])
@login_required
def api_cities():
    """API endpoint to fetch cities with search"""
    search = request.args.get('search', '').strip()
    limit = request.args.get('limit', 50, type=int)
    
    query = City.query
    
    if search:
        from sqlalchemy import or_
        search_term = f"%{search}%"
        query = query.filter(or_(
            City.name.ilike(search_term),
            City.country.ilike(search_term),
            City.region.ilike(search_term)
        ))
    
    cities = query.order_by(City.name).limit(limit).all()
    
    if not cities and not search:
        # If no search term and no results, return empty array
        return jsonify([])
    
    return jsonify([{
        'id': city.id,
        'name': city.name,
        'country': city.country,
        'region': city.region or '',
        'cost_index': float(city.cost_index) if city.cost_index else None,
        'description': city.description or '',
        'display': f"{city.name}, {city.country}"
    } for city in cities])

@bp.route('/api/activities', methods=['GET'])
@login_required
def api_activities():
    """API endpoint to fetch activities with search and filters"""
    search = request.args.get('search', '').strip()
    city_id = request.args.get('city_id', type=int)
    activity_type = request.args.get('activity_type', '').strip()
    limit = request.args.get('limit', 50, type=int)
    
    query = Activity.query
    
    if search:
        from sqlalchemy import or_
        search_term = f"%{search}%"
        query = query.filter(or_(
            Activity.name.ilike(search_term),
            Activity.description.ilike(search_term)
        ))
    
    if city_id:
        query = query.filter(Activity.city_id == city_id)
    
    if activity_type:
        query = query.filter(Activity.activity_type == activity_type)
    
    activities = query.order_by(Activity.name).limit(limit).all()
    
    return jsonify([{
        'id': activity.id,
        'name': activity.name,
        'description': activity.description or '',
        'activity_type': activity.activity_type or '',
        'duration_hours': float(activity.duration_hours) if activity.duration_hours else None,
        'estimated_cost': float(activity.estimated_cost) if activity.estimated_cost else None,
        'city_id': activity.city_id,
        'city_name': activity.city.name if activity.city else None,
        'display': f"{activity.name}{' (' + activity.activity_type + ')' if activity.activity_type else ''}{' - ' + activity.city.name if activity.city else ''}"
    } for activity in activities])

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
        
        # Get actual cost or use estimated cost from activity
        actual_cost = None
        if data.get('actual_cost'):
            actual_cost = float(data['actual_cost'])
        elif activity.estimated_cost:
            actual_cost = float(activity.estimated_cost)
        
        itinerary_activity = ItineraryActivity(
            itinerary_day_id=day_id,
            activity_id=data['activity_id'],
            start_time=start_time,
            actual_cost=actual_cost,
            notes=data.get('notes', ''),
            order_index=max_order + 1
        )
        db.session.add(itinerary_activity)
        db.session.flush()  # Flush to get the ID
        
        # Create corresponding budget expense if there's a cost
        if actual_cost:
            # Get or create budget for this trip
            budget = Budget.query.filter_by(trip_id=trip.id).first()
            if not budget:
                budget = Budget(trip_id=trip.id)
                db.session.add(budget)
                db.session.flush()
            
            # Create budget expense linked to this itinerary activity
            budget_expense = BudgetExpense(
                budget_id=budget.id,
                category='Activities',
                amount=Decimal(str(actual_cost)),
                description=activity.name,
                date=day.date,
                itinerary_activity_id=itinerary_activity.id
            )
            db.session.add(budget_expense)
        
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
    
    # Delete associated budget expense if it exists
    if activity.budget_expense:
        db.session.delete(activity.budget_expense)
    
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

@bp.route('/activity/<int:activity_id>/update', methods=['POST'])
@login_required
def update_activity(activity_id):
    activity = ItineraryActivity.query.get_or_404(activity_id)
    trip = activity.itinerary_day.trip_stop.trip
    if trip.user_id != current_user.id:
        return jsonify({'error': 'Permission denied'}), 403
    
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    try:
        # Update start_time if provided
        if 'start_time' in data:
            if data['start_time']:
                activity.start_time = datetime.strptime(data['start_time'], '%H:%M').time()
            else:
                activity.start_time = None
        
        # Update notes if provided
        if 'notes' in data:
            activity.notes = data['notes']
        
        # Update actual_cost if provided
        new_cost = None
        if 'actual_cost' in data:
            if data['actual_cost']:
                new_cost = float(data['actual_cost'])
            activity.actual_cost = new_cost
        
        # Get or create budget
        budget = Budget.query.filter_by(trip_id=trip.id).first()
        if not budget:
            budget = Budget(trip_id=trip.id)
            db.session.add(budget)
            db.session.flush()
        
        # Update or create budget expense
        if new_cost:
            # Update existing expense or create new one
            if activity.budget_expense:
                activity.budget_expense.amount = Decimal(str(new_cost))
                activity.budget_expense.description = activity.activity.name
            else:
                budget_expense = BudgetExpense(
                    budget_id=budget.id,
                    category='Activities',
                    amount=Decimal(str(new_cost)),
                    description=activity.activity.name,
                    date=activity.itinerary_day.date,
                    itinerary_activity_id=activity.id
                )
                db.session.add(budget_expense)
        else:
            # Remove budget expense if cost is removed
            if activity.budget_expense:
                db.session.delete(activity.budget_expense)
        
        db.session.commit()
        return jsonify({'success': True, 'activity_id': activity.id})
    except ValueError as e:
        db.session.rollback()
        return jsonify({'error': f'Invalid data format: {str(e)}'}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Database error: {str(e)}'}), 500

