from flask import Flask
from flask_login import LoginManager
from app.config import config
from app.models import db, User
import os

login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.login_message = 'Please log in to access this page.'
login_manager.login_message_category = 'info'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def create_app(config_name=None):
    app = Flask(__name__)
    
    # Load configuration
    config_name = config_name or os.environ.get('FLASK_ENV', 'development')
    app.config.from_object(config[config_name])
    
    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    
    # Register blueprints
    from app.routes.auth import bp as auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')
    
    from app.routes.dashboard import bp as dashboard_bp
    app.register_blueprint(dashboard_bp)
    
    from app.routes.trips import bp as trips_bp
    app.register_blueprint(trips_bp, url_prefix='/trips')
    
    from app.routes.itinerary import bp as itinerary_bp
    app.register_blueprint(itinerary_bp, url_prefix='/itinerary')
    
    from app.routes.cities import bp as cities_bp
    app.register_blueprint(cities_bp, url_prefix='/cities')
    
    from app.routes.activities import bp as activities_bp
    app.register_blueprint(activities_bp, url_prefix='/activities')
    
    from app.routes.budget import bp as budget_bp
    app.register_blueprint(budget_bp, url_prefix='/budget')
    
    from app.routes.calendar import bp as calendar_bp
    app.register_blueprint(calendar_bp, url_prefix='/calendar')
    
    from app.routes.share import bp as share_bp
    app.register_blueprint(share_bp, url_prefix='/share')
    
    from app.routes.profile import bp as profile_bp
    app.register_blueprint(profile_bp, url_prefix='/profile')
    
    from app.routes.admin import bp as admin_bp
    app.register_blueprint(admin_bp, url_prefix='/admin')
    
    # Create upload directory if it doesn't exist
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    
    return app

