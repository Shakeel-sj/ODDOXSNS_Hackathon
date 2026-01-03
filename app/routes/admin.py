from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app.models import db, User, Trip, City, TripStop, Activity, ItineraryActivity
from app.forms import AdminUserForm
from sqlalchemy import func
from datetime import datetime, timedelta

bp = Blueprint('admin', __name__)

def admin_required(f):
    """Decorator to require admin role"""
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin():
            flash('Admin access required.', 'danger')
            return redirect(url_for('dashboard.index'))
        return f(*args, **kwargs)
    return decorated_function

@bp.route('/')
@login_required
@admin_required
def dashboard():
    # Total users count
    total_users = User.query.count()
    
    # Total trips created
    total_trips = Trip.query.count()
    
    # Popular cities (by trip_stop count)
    popular_cities = db.session.query(
        City,
        func.count(TripStop.id).label('usage_count')
    ).join(
        TripStop, City.id == TripStop.city_id
    ).group_by(City.id).order_by(
        func.count(TripStop.id).desc()
    ).limit(10).all()
    
    # Popular activities (by usage count)
    popular_activities = db.session.query(
        Activity,
        func.count(ItineraryActivity.id).label('usage_count')
    ).join(
        ItineraryActivity, Activity.id == ItineraryActivity.activity_id
    ).group_by(Activity.id).order_by(
        func.count(ItineraryActivity.id).desc()
    ).limit(10).all()
    
    # User growth (last 30 days)
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    new_users = User.query.filter(User.created_at >= thirty_days_ago).count()
    
    # Trip creation over time (last 30 days)
    new_trips = Trip.query.filter(Trip.created_at >= thirty_days_ago).count()
    
    return render_template('admin/dashboard.html',
                         total_users=total_users,
                         total_trips=total_trips,
                         popular_cities=popular_cities,
                         popular_activities=popular_activities,
                         new_users=new_users,
                         new_trips=new_trips)

@bp.route('/users')
@login_required
@admin_required
def users():
    page = request.args.get('page', 1, type=int)
    per_page = 20
    
    users_list = User.query.order_by(User.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return render_template('admin/users.html', users=users_list)

@bp.route('/users/<int:user_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_user(user_id):
    user = User.query.get_or_404(user_id)
    form = AdminUserForm(obj=user)
    
    if form.validate_on_submit():
        user.email = form.email.data
        user.username = form.username.data
        user.full_name = form.full_name.data
        user.role = form.role.data
        user.language_preference = form.language_preference.data
        db.session.commit()
        flash('User updated successfully!', 'success')
        return redirect(url_for('admin.users'))
    
    return render_template('admin/edit_user.html', form=form, user=user)

@bp.route('/users/<int:user_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    
    # Prevent deleting yourself
    if user.id == current_user.id:
        flash('You cannot delete your own account.', 'danger')
        return redirect(url_for('admin.users'))
    
    db.session.delete(user)
    db.session.commit()
    flash('User deleted successfully!', 'success')
    return redirect(url_for('admin.users'))

