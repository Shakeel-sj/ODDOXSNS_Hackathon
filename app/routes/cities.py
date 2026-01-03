from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required, current_user
from app.models import db, City, SavedDestination
from app.forms import CitySearchForm
from sqlalchemy import or_

bp = Blueprint('cities', __name__)

@bp.route('/search')
@login_required
def search():
    form = CitySearchForm()
    page = request.args.get('page', 1, type=int)
    per_page = 20
    
    query = City.query
    
    if form.query.data:
        search_term = f"%{form.query.data}%"
        query = query.filter(or_(
            City.name.ilike(search_term),
            City.country.ilike(search_term),
            City.region.ilike(search_term)
        ))
    
    if form.country.data:
        query = query.filter(City.country.ilike(f"%{form.country.data}%"))
    
    if form.region.data:
        query = query.filter(City.region.ilike(f"%{form.region.data}%"))
    
    cities = query.order_by(City.name).paginate(page=page, per_page=per_page, error_out=False)
    
    # Get user's saved destinations
    saved_city_ids = {sd.city_id for sd in SavedDestination.query.filter_by(user_id=current_user.id).all()}
    
    return render_template('cities/search.html', form=form, cities=cities, saved_city_ids=saved_city_ids)

@bp.route('/<int:city_id>/save', methods=['POST'])
@login_required
def save(city_id):
    city = City.query.get_or_404(city_id)
    
    # Check if already saved
    existing = SavedDestination.query.filter_by(user_id=current_user.id, city_id=city_id).first()
    if existing:
        return jsonify({'success': True, 'message': 'Already saved'})
    
    saved = SavedDestination(user_id=current_user.id, city_id=city_id)
    db.session.add(saved)
    db.session.commit()
    
    return jsonify({'success': True, 'message': 'City saved to your destinations'})

@bp.route('/<int:city_id>/unsave', methods=['POST'])
@login_required
def unsave(city_id):
    saved = SavedDestination.query.filter_by(user_id=current_user.id, city_id=city_id).first()
    if saved:
        db.session.delete(saved)
        db.session.commit()
    
    return jsonify({'success': True, 'message': 'City removed from saved destinations'})

