"""Seed database with sample data"""
from app import create_app, db
from app.models import User, City, Activity, Trip, TripStop, ItineraryDay, Budget
from datetime import datetime, date, timedelta
from werkzeug.security import generate_password_hash

app = create_app()

def seed_data():
    with app.app_context():
        # Clear existing data (optional - be careful in production!)
        # db.drop_all()
        # db.create_all()
        
        # Create admin user
        admin = User(
            email='admin@globetrotter.com',
            username='admin',
            password_hash=generate_password_hash('admin123'),
            full_name='Admin User',
            role='Admin'
        )
        db.session.add(admin)
        
        # Create regular users
        users = []
        for i in range(1, 6):
            user = User(
                email=f'user{i}@example.com',
                username=f'user{i}',
                password_hash=generate_password_hash('password123'),
                full_name=f'User {i}'
            )
            users.append(user)
            db.session.add(user)
        
        db.session.commit()
        
        # Create cities
        cities_data = [
            {'name': 'Paris', 'country': 'France', 'region': 'Île-de-France', 'cost_index': 1.5, 'description': 'The City of Light'},
            {'name': 'Tokyo', 'country': 'Japan', 'region': 'Kanto', 'cost_index': 1.8, 'description': 'Modern metropolis'},
            {'name': 'New York', 'country': 'USA', 'region': 'New York', 'cost_index': 2.0, 'description': 'The Big Apple'},
            {'name': 'London', 'country': 'UK', 'region': 'England', 'cost_index': 1.6, 'description': 'Historic capital'},
            {'name': 'Barcelona', 'country': 'Spain', 'region': 'Catalonia', 'cost_index': 1.2, 'description': 'Mediterranean gem'},
            {'name': 'Rome', 'country': 'Italy', 'region': 'Lazio', 'cost_index': 1.4, 'description': 'Eternal City'},
            {'name': 'Bangkok', 'country': 'Thailand', 'region': 'Central', 'cost_index': 0.8, 'description': 'Vibrant capital'},
            {'name': 'Dubai', 'country': 'UAE', 'region': 'Dubai', 'cost_index': 1.7, 'description': 'Desert luxury'},
            {'name': 'Sydney', 'country': 'Australia', 'region': 'NSW', 'cost_index': 1.5, 'description': 'Harbor city'},
            {'name': 'Amsterdam', 'country': 'Netherlands', 'region': 'North Holland', 'cost_index': 1.3, 'description': 'Canal city'},
            {'name': 'Berlin', 'country': 'Germany', 'region': 'Berlin', 'cost_index': 1.1, 'description': 'Cultural hub'},
            {'name': 'Prague', 'country': 'Czech Republic', 'region': 'Bohemia', 'cost_index': 0.9, 'description': 'Medieval beauty'},
            {'name': 'Istanbul', 'country': 'Turkey', 'region': 'Marmara', 'cost_index': 0.7, 'description': 'Crossroads of cultures'},
            {'name': 'Singapore', 'country': 'Singapore', 'region': 'Central', 'cost_index': 1.6, 'description': 'Garden city'},
            {'name': 'Vienna', 'country': 'Austria', 'region': 'Vienna', 'cost_index': 1.3, 'description': 'Imperial capital'},
            {'name': 'Bali', 'country': 'Indonesia', 'region': 'Bali', 'cost_index': 0.6, 'description': 'Tropical paradise'},
            {'name': 'Cairo', 'country': 'Egypt', 'region': 'Cairo', 'cost_index': 0.5, 'description': 'Ancient wonders'},
            {'name': 'Marrakech', 'country': 'Morocco', 'region': 'Marrakech-Safi', 'cost_index': 0.6, 'description': 'Exotic markets'},
            {'name': 'Lisbon', 'country': 'Portugal', 'region': 'Lisboa', 'cost_index': 1.0, 'description': 'Coastal charm'},
            {'name': 'Stockholm', 'country': 'Sweden', 'region': 'Stockholm', 'cost_index': 1.4, 'description': 'Nordic beauty'},
        ]
        
        cities = []
        for city_data in cities_data:
            city = City(**city_data)
            cities.append(city)
            db.session.add(city)
        
        db.session.commit()
        
        # Create activities
        activities_data = [
            # Paris
            {'name': 'Eiffel Tower Visit', 'description': 'Iconic iron lattice tower', 'activity_type': 'Sightseeing', 'duration_hours': 2.0, 'estimated_cost': 25.0, 'city_id': cities[0].id},
            {'name': 'Louvre Museum', 'description': 'World-famous art museum', 'activity_type': 'Culture', 'duration_hours': 4.0, 'estimated_cost': 17.0, 'city_id': cities[0].id},
            {'name': 'Seine River Cruise', 'description': 'Scenic boat tour', 'activity_type': 'Sightseeing', 'duration_hours': 1.5, 'estimated_cost': 15.0, 'city_id': cities[0].id},
            {'name': 'French Bistro Dinner', 'description': 'Traditional French cuisine', 'activity_type': 'Food', 'duration_hours': 2.0, 'estimated_cost': 50.0, 'city_id': cities[0].id},
            
            # Tokyo
            {'name': 'Shibuya Crossing', 'description': 'Famous pedestrian scramble', 'activity_type': 'Sightseeing', 'duration_hours': 0.5, 'estimated_cost': 0.0, 'city_id': cities[1].id},
            {'name': 'Sushi Omakase', 'description': 'Chef-selected sushi experience', 'activity_type': 'Food', 'duration_hours': 2.0, 'estimated_cost': 150.0, 'city_id': cities[1].id},
            {'name': 'Tokyo Skytree', 'description': 'Tallest tower in Japan', 'activity_type': 'Sightseeing', 'duration_hours': 1.5, 'estimated_cost': 20.0, 'city_id': cities[1].id},
            
            # New York
            {'name': 'Statue of Liberty Tour', 'description': 'Iconic symbol of freedom', 'activity_type': 'Sightseeing', 'duration_hours': 3.0, 'estimated_cost': 25.0, 'city_id': cities[2].id},
            {'name': 'Broadway Show', 'description': 'World-class theater', 'activity_type': 'Culture', 'duration_hours': 2.5, 'estimated_cost': 120.0, 'city_id': cities[2].id},
            {'name': 'Central Park Walk', 'description': 'Urban oasis', 'activity_type': 'Nature', 'duration_hours': 2.0, 'estimated_cost': 0.0, 'city_id': cities[2].id},
            
            # Generic activities
            {'name': 'City Walking Tour', 'description': 'Explore the city on foot', 'activity_type': 'Sightseeing', 'duration_hours': 3.0, 'estimated_cost': 20.0},
            {'name': 'Local Market Visit', 'description': 'Experience local culture', 'activity_type': 'Culture', 'duration_hours': 2.0, 'estimated_cost': 15.0},
            {'name': 'Sunset Viewpoint', 'description': 'Watch the sunset', 'activity_type': 'Nature', 'duration_hours': 1.0, 'estimated_cost': 0.0},
            {'name': 'Street Food Tour', 'description': 'Taste local street food', 'activity_type': 'Food', 'duration_hours': 2.5, 'estimated_cost': 30.0},
            {'name': 'Museum Visit', 'description': 'Explore local history', 'activity_type': 'Culture', 'duration_hours': 3.0, 'estimated_cost': 15.0},
            {'name': 'Beach Day', 'description': 'Relax on the beach', 'activity_type': 'Nature', 'duration_hours': 4.0, 'estimated_cost': 10.0},
            {'name': 'Nightlife District', 'description': 'Experience local nightlife', 'activity_type': 'Nightlife', 'duration_hours': 4.0, 'estimated_cost': 50.0},
            {'name': 'Shopping District', 'description': 'Shop for souvenirs', 'activity_type': 'Shopping', 'duration_hours': 3.0, 'estimated_cost': 100.0},
            {'name': 'Adventure Activity', 'description': 'Thrilling adventure', 'activity_type': 'Adventure', 'duration_hours': 3.0, 'estimated_cost': 80.0},
            {'name': 'Cooking Class', 'description': 'Learn local cuisine', 'activity_type': 'Food', 'duration_hours': 3.0, 'estimated_cost': 60.0},
        ]
        
        for activity_data in activities_data:
            activity = Activity(**activity_data)
            db.session.add(activity)
        
        db.session.commit()
        
        # Create sample trips
        for i, user in enumerate(users[:3]):
            start_date = date.today() + timedelta(days=30 + i*10)
            end_date = start_date + timedelta(days=5)
            
            trip = Trip(
                user_id=user.id,
                name=f'Sample Trip {i+1}',
                description=f'A wonderful trip planned by {user.username}',
                start_date=start_date,
                end_date=end_date
            )
            db.session.add(trip)
            db.session.flush()
            
            # Create budget
            budget = Budget(
                trip_id=trip.id,
                transport_budget=500.0,
                accommodation_budget=800.0,
                activities_budget=400.0,
                meals_budget=300.0,
                other_budget=200.0
            )
            db.session.add(budget)
            
            # Add a city stop
            city = cities[i % len(cities)]
            stop = TripStop(
                trip_id=trip.id,
                city_id=city.id,
                arrival_date=start_date,
                departure_date=end_date,
                order_index=1
            )
            db.session.add(stop)
            db.session.flush()
            
            # Create itinerary days
            current_date = start_date
            day_num = 1
            while current_date <= end_date:
                day = ItineraryDay(
                    trip_stop_id=stop.id,
                    date=current_date,
                    day_number=day_num
                )
                db.session.add(day)
                current_date += timedelta(days=1)
                day_num += 1
        
        db.session.commit()
        print("Seed data created successfully!")

if __name__ == '__main__':
    seed_data()

