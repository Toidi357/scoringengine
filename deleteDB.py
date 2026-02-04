from app import app, db

with app.app_context():
    print("Dropping all tables...")
    db.drop_all()