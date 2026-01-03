from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from app.models import db, Trip, Budget, BudgetExpense
from app.forms import BudgetForm, BudgetExpenseForm
from datetime import datetime, date
from decimal import Decimal

bp = Blueprint('budget', __name__)

@bp.route('/trip/<int:trip_id>')
@login_required
def breakdown(trip_id):
    trip = Trip.query.get_or_404(trip_id)
    if trip.user_id != current_user.id:
        flash('You do not have permission to view this trip.', 'danger')
        return redirect(url_for('trips.list'))
    
    # Get or create budget
    budget = Budget.query.filter_by(trip_id=trip_id).first()
    if not budget:
        budget = Budget(trip_id=trip_id)
        db.session.add(budget)
        db.session.commit()
    
    # Get expenses grouped by category
    expenses_by_category = {}
    for category in ['Transport', 'Accommodation', 'Activities', 'Meals', 'Other']:
        expenses_by_category[category] = BudgetExpense.query.filter_by(
            budget_id=budget.id,
            category=category
        ).all()
    
    # Calculate daily spending
    daily_spending = {}
    all_expenses = BudgetExpense.query.filter_by(budget_id=budget.id).all()
    for expense in all_expenses:
        day_key = expense.date.isoformat()
        if day_key not in daily_spending:
            daily_spending[day_key] = 0
        daily_spending[day_key] += float(expense.amount)
    
    # Calculate average cost per day
    trip_duration = (trip.end_date - trip.start_date).days + 1
    avg_cost_per_day = float(budget.total_expenses) / trip_duration if trip_duration > 0 else 0
    
    return render_template('budget/breakdown.html',
                         trip=trip,
                         budget=budget,
                         expenses_by_category=expenses_by_category,
                         daily_spending=daily_spending,
                         avg_cost_per_day=avg_cost_per_day)

@bp.route('/trip/<int:trip_id>/edit', methods=['GET', 'POST'])
@login_required
def edit(trip_id):
    trip = Trip.query.get_or_404(trip_id)
    if trip.user_id != current_user.id:
        flash('You do not have permission to edit this trip.', 'danger')
        return redirect(url_for('trips.list'))
    
    budget = Budget.query.filter_by(trip_id=trip_id).first()
    if not budget:
        budget = Budget(trip_id=trip_id)
        db.session.add(budget)
        db.session.commit()
    
    form = BudgetForm(obj=budget)
    if form.validate_on_submit():
        budget.transport_budget = form.transport_budget.data or 0
        budget.accommodation_budget = form.accommodation_budget.data or 0
        budget.activities_budget = form.activities_budget.data or 0
        budget.meals_budget = form.meals_budget.data or 0
        budget.other_budget = form.other_budget.data or 0
        db.session.commit()
        flash('Budget updated successfully!', 'success')
        return redirect(url_for('budget.breakdown', trip_id=trip_id))
    
    return render_template('budget/edit.html', form=form, trip=trip, budget=budget)

@bp.route('/trip/<int:trip_id>/expense/add', methods=['POST'])
@login_required
def add_expense(trip_id):
    trip = Trip.query.get_or_404(trip_id)
    if trip.user_id != current_user.id:
        return jsonify({'error': 'Permission denied'}), 403
    
    budget = Budget.query.filter_by(trip_id=trip_id).first()
    if not budget:
        budget = Budget(trip_id=trip_id)
        db.session.add(budget)
        db.session.commit()
    
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    # Convert date string to date object
    if 'date' in data:
        data['date'] = datetime.strptime(data['date'], '%Y-%m-%d').date()
    
    form = BudgetExpenseForm(data=data)
    if form.validate():
        expense = BudgetExpense(
            budget_id=budget.id,
            category=form.category.data,
            amount=form.amount.data,
            description=form.description.data,
            date=form.date.data
        )
        db.session.add(expense)
        db.session.commit()
        return jsonify({'success': True, 'expense_id': expense.id})
    
    return jsonify({'error': 'Validation failed', 'errors': form.errors}), 400

@bp.route('/expense/<int:expense_id>/delete', methods=['POST'])
@login_required
def delete_expense(expense_id):
    expense = BudgetExpense.query.get_or_404(expense_id)
    trip = expense.budget.trip
    if trip.user_id != current_user.id:
        return jsonify({'error': 'Permission denied'}), 403
    
    db.session.delete(expense)
    db.session.commit()
    return jsonify({'success': True})

