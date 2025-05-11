from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime

from models import Like, LikeComment, Movie
from schemas import LikeCreate, LikeResponse, LikeCountResponse
from dependencies import get_current_user
from database import get_db

router = APIRouter(prefix="/likes", tags=["Likes"])

@router.post("/", response_model=LikeResponse)
def like_movie(payload: LikeCreate, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    
    movie = db.query(Movie).filter(Movie.id == payload.movie_id).first()
    if not movie:
        raise HTTPException(status_code=404, detail="Movie not found")

    existing_like = db.query(Like).filter(Like.user_id == current_user.id, Like.movie_id == payload.movie_id).first()

    if existing_like:
        raise HTTPException(status_code=400, detail="You already liked this movie")

    like = Like(
        user_id=current_user.id,
        movie_id=payload.movie_id,
        like=payload.like,
        created_at=datetime.utcnow()
    )
    db.add(like)
    db.commit()
    db.refresh(like)

    if payload.comment:
        comment = LikeComment(
            like_id=like.id,
            comment=payload.comment,
            created_at=datetime.utcnow()
        )
        db.add(comment)
        db.commit()
        db.refresh(like)  

    return {
        "id": like.id,
        "user_id": like.user_id,
        "movie_id": like.movie_id,
        "like": like.like,
        "created_at": like.created_at,
        "comment": payload.comment
    }

@router.get("/count/{movie_id}", response_model=LikeCountResponse)
def get_like_count(movie_id: int, db: Session = Depends(get_db)):
    count = db.query(Like).filter(Like.movie_id == movie_id, Like.like == 1).count()
    return {"movie_id": movie_id, "total_likes": count}
