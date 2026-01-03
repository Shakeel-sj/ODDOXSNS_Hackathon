from flask import Blueprint, render_template, redirect, url_for
from flask_login import login_required, current_user
from app.models import db, Trip, City, SavedDestination, TripStop
from datetime import datetime, date
from sqlalchemy import func

bp = Blueprint('dashboard', __name__)

@bp.route('/')
def root():
    """Root route - redirects to dashboard if logged in, otherwise to login"""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))
    return redirect(url_for('auth.login'))

@bp.route('/dashboard')
@login_required
def index():
    today = date.today()
    
    # Get upcoming trips (next 5)
    upcoming_trips = Trip.query.filter(
        Trip.user_id == current_user.id,
        Trip.start_date >= today
    ).order_by(Trip.start_date.asc()).limit(5).all()
    
    # Get popular destinations (top 10 cities by usage)
    popular_cities = db.session.query(
        City,
        func.count(TripStop.id).label('usage_count')
    ).join(
        TripStop, City.id == TripStop.city_id
    ).group_by(City.id).order_by(
        func.count(TripStop.id).desc()
    ).limit(10).all()
    
    # Calculate total budget across all trips
    total_budget = 0
    user_trips = Trip.query.filter_by(user_id=current_user.id).all()
    for trip in user_trips:
        if trip.budget:
            total_budget += float(trip.budget.total_budget or 0)
    
    return render_template('dashboard/index.html',
                         upcoming_trips=upcoming_trips,
                         popular_cities=popular_cities,
                         total_budget=total_budget)

