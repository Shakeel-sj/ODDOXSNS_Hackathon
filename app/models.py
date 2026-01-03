from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    full_name = db.Column(db.String(100))
    avatar_url = db.Column(db.String(255))
    role = db.Column(db.String(20), default='User', nullable=False)
    language_preference = db.Column(db.String(10), default='en')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    trips = db.relationship('Trip', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    saved_destinations = db.relationship('SavedDestination', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def is_admin(self):
        return self.role == 'Admin'
    
    def __repr__(self):
        return f'<User {self.username}>'

class City(db.Model):
    __tablename__ = 'cities'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    country = db.Column(db.String(100), nullable=False)
    region = db.Column(db.String(100))
    cost_index = db.Column(db.Numeric(10, 2), default=1.0)
    latitude = db.Column(db.Numeric(10, 7))
    longitude = db.Column(db.Numeric(10, 7))
    description = db.Column(db.Text)
    
    # Relationships
    trip_stops = db.relationship('TripStop', backref='city', lazy='dynamic')
    activities = db.relationship('Activity', backref='city', lazy='dynamic')
    saved_destinations = db.relationship('SavedDestination', backref='city', lazy='dynamic')
    
    def __repr__(self):
        return f'<City {self.name}, {self.country}>'

class Trip(db.Model):
    __tablename__ = 'trips'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    cover_image_url = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    trip_stops = db.relationship('TripStop', backref='trip', lazy='dynamic', cascade='all, delete-orphan', order_by='TripStop.order_index')
    budget = db.relationship('Budget', backref='trip', uselist=False, cascade='all, delete-orphan')
    shared_links = db.relationship('SharedLink', backref='trip', lazy='dynamic', cascade='all, delete-orphan')
    
    @property
    def status(self):
        today = datetime.utcnow().date()
        if self.end_date < today:
            return 'Completed'
        elif self.start_date <= today <= self.end_date:
            return 'Ongoing'
        else:
            return 'Upcoming'
    
    def __repr__(self):
        return f'<Trip {self.name}>'

class TripStop(db.Model):
    __tablename__ = 'trip_stops'
    
    id = db.Column(db.Integer, primary_key=True)
    trip_id = db.Column(db.Integer, db.ForeignKey('trips.id', ondelete='CASCADE'), nullable=False)
    city_id = db.Column(db.Integer, db.ForeignKey('cities.id'), nullable=False)
    arrival_date = db.Column(db.Date, nullable=False)
    departure_date = db.Column(db.Date, nullable=False)
    order_index = db.Column(db.Integer, default=0)
    notes = db.Column(db.Text)
    
    # Relationships
    itinerary_days = db.relationship('ItineraryDay', backref='trip_stop', lazy='dynamic', cascade='all, delete-orphan', order_by='ItineraryDay.day_number')
    
    def __repr__(self):
        return f'<TripStop {self.id}>'

class ItineraryDay(db.Model):
    __tablename__ = 'itinerary_days'
    
    id = db.Column(db.Integer, primary_key=True)
    trip_stop_id = db.Column(db.Integer, db.ForeignKey('trip_stops.id', ondelete='CASCADE'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    day_number = db.Column(db.Integer, nullable=False)
    
    # Relationships
    activities = db.relationship('ItineraryActivity', backref='itinerary_day', lazy='dynamic', cascade='all, delete-orphan', order_by='ItineraryActivity.order_index')
    
    def __repr__(self):
        return f'<ItineraryDay {self.day_number}>'

class Activity(db.Model):
    __tablename__ = 'activities'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    activity_type = db.Column(db.String(50))
    duration_hours = db.Column(db.Numeric(5, 2))
    estimated_cost = db.Column(db.Numeric(10, 2))
    city_id = db.Column(db.Integer, db.ForeignKey('cities.id'))
    image_url = db.Column(db.String(255))
    
    # Relationships
    itinerary_activities = db.relationship('ItineraryActivity', backref='activity', lazy='dynamic')
    
    def __repr__(self):
        return f'<Activity {self.name}>'

class ItineraryActivity(db.Model):
    __tablename__ = 'itinerary_activities'
    
    id = db.Column(db.Integer, primary_key=True)
    itinerary_day_id = db.Column(db.Integer, db.ForeignKey('itinerary_days.id', ondelete='CASCADE'), nullable=False)
    activity_id = db.Column(db.Integer, db.ForeignKey('activities.id'), nullable=False)
    start_time = db.Column(db.Time)
    actual_cost = db.Column(db.Numeric(10, 2))
    notes = db.Column(db.Text)
    order_index = db.Column(db.Integer, default=0)
    
    def __repr__(self):
        return f'<ItineraryActivity {self.id}>'

class Budget(db.Model):
    __tablename__ = 'budgets'
    
    id = db.Column(db.Integer, primary_key=True)
    trip_id = db.Column(db.Integer, db.ForeignKey('trips.id', ondelete='CASCADE'), nullable=False, unique=True)
    transport_budget = db.Column(db.Numeric(10, 2), default=0)
    accommodation_budget = db.Column(db.Numeric(10, 2), default=0)
    activities_budget = db.Column(db.Numeric(10, 2), default=0)
    meals_budget = db.Column(db.Numeric(10, 2), default=0)
    other_budget = db.Column(db.Numeric(10, 2), default=0)
    
    # Relationships
    expenses = db.relationship('BudgetExpense', backref='budget', lazy='dynamic', cascade='all, delete-orphan')
    
    @property
    def total_budget(self):
        return (self.transport_budget or 0) + (self.accommodation_budget or 0) + \
               (self.activities_budget or 0) + (self.meals_budget or 0) + (self.other_budget or 0)
    
    @property
    def total_expenses(self):
        return sum(exp.amount for exp in self.expenses) if self.expenses else 0
    
    def __repr__(self):
        return f'<Budget for Trip {self.trip_id}>'

class BudgetExpense(db.Model):
    __tablename__ = 'budget_expenses'
    
    id = db.Column(db.Integer, primary_key=True)
    budget_id = db.Column(db.Integer, db.ForeignKey('budgets.id', ondelete='CASCADE'), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    description = db.Column(db.String(255))
    date = db.Column(db.Date, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    itinerary_activity_id = db.Column(db.Integer, db.ForeignKey('itinerary_activities.id', ondelete='CASCADE'), nullable=True)
    
    # Relationships
    itinerary_activity = db.relationship('ItineraryActivity', backref='budget_expense', uselist=False)
    
    def __repr__(self):
        return f'<BudgetExpense {self.category}: {self.amount}>'

class SharedLink(db.Model):
    __tablename__ = 'shared_links'
    
    id = db.Column(db.Integer, primary_key=True)
    trip_id = db.Column(db.Integer, db.ForeignKey('trips.id', ondelete='CASCADE'), nullable=False)
    share_token = db.Column(db.String(64), unique=True, nullable=False, index=True)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime)
    
    def __repr__(self):
        return f'<SharedLink {self.share_token}>'

class SavedDestination(db.Model):
    __tablename__ = 'saved_destinations'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    city_id = db.Column(db.Integer, db.ForeignKey('cities.id', ondelete='CASCADE'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    __table_args__ = (db.UniqueConstraint('user_id', 'city_id', name='unique_user_city'),)
    
    def __repr__(self):
        return f'<SavedDestination {self.id}>'

