from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
from jose import JWTError, jwt
from pydantic import BaseModel
from fastapi.security import OAuth2PasswordBearer  # Added import

from database import get_db
from models import User
from schemas import UserCreate, UserResponse
from auth import get_password_hash, verify_password, create_access_token

router = APIRouter(prefix="/users", tags=["Users"])

# JWT Secret Key — use environment variable in production
SECRET_KEY = "your_secret_key_here"
ALGORITHM = "HS256"

# Dependency to get the current user
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/users/login") 

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):  
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: int = int(payload.get("sub"))
        if user_id is None:
            raise credentials_exception
    except (JWTError, ValueError):
        raise credentials_exception
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise credentials_exception
    return user

# Dependency to get the current admin user
def get_current_admin(current_user: User = Depends(get_current_user)):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    return current_user

# Register a new user
@router.post("/register", response_model=UserResponse)
def register(user: UserCreate, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.email == user.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    hashed_password = get_password_hash(user.password)
    new_user = User(
        username=user.username,
        email=user.email,
        role="user",  # Always default to 'user' role
        password=hashed_password,
        created_at=datetime.utcnow()
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

# Login schema for JSON-based login
class LoginInput(BaseModel):
    email: str
    password: str

# User login with JSON body
@router.post("/login")
def login(login_data: LoginInput, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == login_data.email).first()
    if not user or not verify_password(login_data.password, user.password):
        raise HTTPException(status_code=400, detail="Incorrect email or password")
    access_token = create_access_token(data={"sub": str(user.id)})
    return {"access_token": access_token, "token_type": "bearer"}

# Get current user's information
@router.get("/me", response_model=UserResponse)
def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user

# Pydantic model to accept the new username in the request body
class UpdateUsername(BaseModel):
    new_username: str

# Update username
@router.put("/update", response_model=UserResponse)
def update_username(user_update: UpdateUsername, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    current_user.username = user_update.new_username
    db.commit()
    db.refresh(current_user)
    return current_user

# Delete own account
@router.delete("/delete")
def delete_own_account(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    db.delete(current_user)
    db.commit()
    return {"message": "Account deleted successfully"}

# Admin: Get all users
@router.get("/", response_model=List[UserResponse])
def get_all_users(db: Session = Depends(get_db), _: User = Depends(get_current_admin)):
    return db.query(User).all()

# Admin: Get user by ID
@router.get("/{user_id}", response_model=UserResponse)
def get_user_by_id(user_id: int, db: Session = Depends(get_db), _: User = Depends(get_current_admin)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

# Admin: Delete any user
@router.delete("/{user_id}")
def delete_user_by_admin(user_id: int, db: Session = Depends(get_db), _: User = Depends(get_current_admin)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    db.delete(user)
    db.commit()
    return {"message": "User deleted successfully"}

# User: Get own user by ID
@router.get("/my/{user_id}", response_model=UserResponse)
def get_own_user_by_id(user_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if current_user.id != user_id:
        raise HTTPException(status_code=403, detail="Not authorized to access this user")
    return current_user

# Pre-create the admin if not exists
def create_admin_if_not_exists(db: Session):
    admin_email = "admin142@gmail.com"
    existing_admin = db.query(User).filter(User.email == admin_email).first()
    if not existing_admin:
        admin_user = User(
            username="Admin",
            email=admin_email,
            password=get_password_hash("pass123"),
            role="admin",
            created_at=datetime.utcnow()
        )
        db.add(admin_user)
        db.commit()
        print("✅ Admin user created.")
