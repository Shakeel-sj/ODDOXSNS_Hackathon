"""Migration script to add itinerary_activity_id to budget_expenses table"""
from app import create_app, db
from sqlalchemy import text

app = create_app()

with app.app_context():
    try:
        # Check if column already exists
        inspector = db.inspect(db.engine)
        columns = [col['name'] for col in inspector.get_columns('budget_expenses')]
        
        if 'itinerary_activity_id' not in columns:
            print("Adding itinerary_activity_id column to budget_expenses table...")
            # Add the new column
            db.session.execute(text("""
                ALTER TABLE budget_expenses 
                ADD COLUMN itinerary_activity_id INTEGER 
                REFERENCES itinerary_activities(id) ON DELETE CASCADE
            """))
            db.session.commit()
            print("Migration completed successfully!")
        else:
            print("Column itinerary_activity_id already exists. No migration needed.")
    except Exception as e:
        db.session.rollback()
        print(f"Migration error: {str(e)}")
        print("If you're using SQLite, you may need to recreate the database.")
        print("Run: python init_db.py (this will recreate all tables)")
