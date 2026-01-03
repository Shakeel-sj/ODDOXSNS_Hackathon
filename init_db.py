"""Initialize the database"""
from app import create_app, db
from app.models import User, Trip, City, Activity, TripStop, ItineraryDay, ItineraryActivity, Budget, BudgetExpense, SharedLink, SavedDestination

app = create_app()

with app.app_context():
    db.create_all()
    print("Database initialized successfully!")

