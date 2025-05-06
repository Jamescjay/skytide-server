from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from models import Follow, User
from schemas import FollowCreate, FollowResponse
from database import get_db

router = APIRouter(
    prefix="/follows",
    tags=["Follows"]
)


@router.post("/", response_model=FollowResponse, status_code=status.HTTP_201_CREATED)
def create_follow(follow: FollowCreate, db: Session = Depends(get_db)):
    existing_follow = db.query(Follow).filter(
        Follow.following_user_id == follow.following_user_id,
        Follow.followed_user_id == follow.followed_user_id
    ).first()

    if existing_follow:
        raise HTTPException(status_code=400, detail="Already following this user.")

    new_follow = Follow(**follow.dict())
    db.add(new_follow)
    db.commit()
    db.refresh(new_follow)
    return new_follow


@router.get("/", response_model=List[FollowResponse])
def get_all_follows(db: Session = Depends(get_db)):
    follows = db.query(Follow).all()
    return follows


@router.get("/user/{user_id}", response_model=List[FollowResponse])
def get_user_follows(user_id: int, db: Session = Depends(get_db)):
    follows = db.query(Follow).filter(Follow.following_user_id == user_id).all()
    return follows


@router.delete("/", status_code=status.HTTP_204_NO_CONTENT)
def delete_follow(follow: FollowCreate, db: Session = Depends(get_db)):
    follow_record = db.query(Follow).filter(
        Follow.following_user_id == follow.following_user_id,
        Follow.followed_user_id == follow.followed_user_id
    ).first()

    if not follow_record:
        raise HTTPException(status_code=404, detail="Follow relationship not found.")

    db.delete(follow_record)
    db.commit()
    return


