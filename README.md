# GlobeTrotter - Travel Planning Application

A comprehensive Flask-based web application for planning and managing travel itineraries.

## Features

- **User Authentication**: Secure login, signup, and password management
- **Trip Management**: Create, edit, and organize multiple trips
- **Itinerary Builder**: Add cities and activities to build detailed day-by-day itineraries
- **City & Activity Search**: Browse and search cities and activities with filters
- **Budget Management**: Track expenses by category with visual charts
- **Calendar View**: FullCalendar integration for timeline visualization
- **Trip Sharing**: Generate shareable links for public itinerary viewing
- **User Profiles**: Manage profile settings and saved destinations
- **Admin Dashboard**: User management and analytics (admin only)

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd tripplanner
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up the database:
```bash
flask db init
flask db migrate -m "Initial migration"
flask db upgrade
```

5. (Optional) Seed the database with sample data:
```bash
python seed_data.py
```

6. Run the application:
```bash
python run.py
```

The application will be available at `http://localhost:5000`

## Configuration

Create a `.env` file in the root directory (optional):
```
SECRET_KEY=your-secret-key-here
DATABASE_URL=sqlite:///instance/globetrotter.db
FLASK_ENV=development
```

## Default Admin Account

After running `seed_data.py`:
- Email: `admin@globetrotter.com`
- Password: `admin123`

## Project Structure

```
tripplanner/
├── app/
│   ├── __init__.py          # Flask app factory
│   ├── models.py            # SQLAlchemy models
│   ├── forms.py             # Flask-WTF forms
│   ├── config.py            # Configuration
│   ├── routes/              # Blueprint routes
│   ├── templates/           # Jinja2 templates
│   ├── static/              # CSS, JS, images
│   └── utils/               # Utility functions
├── migrations/              # Database migrations
├── instance/                # SQLite database
├── requirements.txt         # Python dependencies
├── run.py                   # Application entry point
└── seed_data.py            # Database seeding script
```

## Technologies Used

- **Backend**: Flask, SQLAlchemy, Flask-Login, Flask-WTF
- **Frontend**: Bootstrap 5, Chart.js, FullCalendar.js
- **Database**: SQLite (development), PostgreSQL (production-ready)

## Security Features

- Password hashing with Werkzeug
- CSRF protection (Flask-WTF)
- SQL injection prevention (SQLAlchemy ORM)
- XSS protection (Jinja2 auto-escaping)
- Role-based access control

## License

This project is open source and available under the MIT License.

