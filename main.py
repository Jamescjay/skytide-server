from fastapi import FastAPI
from datetime import datetime
import models
from database import get_db, engine  # Import engine from database
from resources import users
from models import User
from auth import get_password_hash

# Create database tables
models.Base.metadata.create_all(bind=engine)  # Use engine from database

app = FastAPI()

# Include user routes
app.include_router(users.router)

# Create admin user if it does not exist
def create_admin_user():
    db: Session = next(get_db())
    admin_email = "admin142@gmail.com"
    admin_user = db.query(User).filter(User.email == admin_email).first()
    if not admin_user:
        hashed_password = get_password_hash("pass123")
        new_admin = User(
            username="Admin",
            email=admin_email,
            role="admin",
            password=hashed_password,
            created_at=datetime.utcnow()
        )
        db.add(new_admin)
        db.commit()
        db.refresh(new_admin)
        print("Admin user created successfully")

# Run this once when the server starts
create_admin_user()

@app.get("/")
def read_root():
    return {"message": "Welcome to the Movie Review API"}
