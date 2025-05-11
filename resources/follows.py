from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime

from models import Follow, User
from schemas import FollowCreate, FollowResponse
from database import get_db
from auth import jwt, SECRET_KEY, ALGORITHM
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError

router = APIRouter(
    prefix="/follows",
    tags=["Follows"]
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


# Utility to extract user ID from JWT token
def get_current_user_id(token: str = Depends(oauth2_scheme)) -> int:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: int = int(payload.get("sub"))
        if user_id is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid authentication credentials")
        return user_id
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid authentication credentials")


@router.post("/follow/{user_id}", response_model=FollowResponse)
def follow_user(user_id: int, db: Session = Depends(get_db), current_user_id: int = Depends(get_current_user_id)):
    if current_user_id == user_id:
        raise HTTPException(status_code=400, detail="You cannot follow yourself")

    existing_follow = db.query(Follow).filter_by(
        following_user_id=current_user_id,
        followed_user_id=user_id
    ).first()

    if existing_follow:
        raise HTTPException(status_code=400, detail="Already following this user")

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    follow = Follow(
        following_user_id=current_user_id,
        followed_user_id=user_id,
        created_at=datetime.utcnow()
    )
    db.add(follow)
    db.commit()
    db.refresh(follow)
    return follow


@router.delete("/unfollow/{user_id}")
def unfollow_user(user_id: int, db: Session = Depends(get_db), current_user_id: int = Depends(get_current_user_id)):
    follow = db.query(Follow).filter_by(
        following_user_id=current_user_id,
        followed_user_id=user_id
    ).first()

    if not follow:
        raise HTTPException(status_code=404, detail="Not following this user")

    db.delete(follow)
    db.commit()
    return {"detail": "Successfully unfollowed user"}


@router.get("/following", response_model=list[FollowResponse])
def get_following(db: Session = Depends(get_db), current_user_id: int = Depends(get_current_user_id)):
    following = db.query(Follow).filter_by(following_user_id=current_user_id).all()
    return following


@router.get("/followers", response_model=list[FollowResponse])
def get_followers(db: Session = Depends(get_db), current_user_id: int = Depends(get_current_user_id)):
    followers = db.query(Follow).filter_by(followed_user_id=current_user_id).all()
    return followers
