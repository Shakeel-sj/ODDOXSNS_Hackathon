from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required, current_user
from app.models import db, Activity, City
from app.forms import ActivitySearchForm
from sqlalchemy import or_, and_

bp = Blueprint('activities', __name__)

@bp.route('/search')
@login_required
def search():
    form = ActivitySearchForm()
    page = request.args.get('page', 1, type=int)
    per_page = 20
    
    query = Activity.query
    
    if form.query.data:
        search_term = f"%{form.query.data}%"
        query = query.filter(or_(
            Activity.name.ilike(search_term),
            Activity.description.ilike(search_term)
        ))
    
    if form.activity_type.data:
        query = query.filter(Activity.activity_type == form.activity_type.data)
    
    if form.min_cost.data is not None:
        query = query.filter(Activity.estimated_cost >= form.min_cost.data)
    
    if form.max_cost.data is not None:
        query = query.filter(Activity.estimated_cost <= form.max_cost.data)
    
    if form.max_duration.data is not None:
        query = query.filter(Activity.duration_hours <= form.max_duration.data)
    
    activities = query.order_by(Activity.name).paginate(page=page, per_page=per_page, error_out=False)
    
    return render_template('activities/search.html', form=form, activities=activities)

@bp.route('/<int:activity_id>')
@login_required
def view(activity_id):
    activity = Activity.query.get_or_404(activity_id)
    return jsonify({
        'id': activity.id,
        'name': activity.name,
        'description': activity.description,
        'activity_type': activity.activity_type,
        'duration_hours': float(activity.duration_hours) if activity.duration_hours else None,
        'estimated_cost': float(activity.estimated_cost) if activity.estimated_cost else None,
        'city': activity.city.name if activity.city else None,
        'image_url': activity.image_url
    })

