from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from models import Like
from schemas import LikeBase
from database import get_db

router = APIRouter(
    prefix="/likes",        
    tags=["likes"]           
)

@router.post("/")
def like_movie(data: LikeBase, db: Session = Depends(get_db)):
    existing_like = db.query(Like).filter_by(user_id=data.user_id, movie_id=data.movie_id).first()
    if existing_like:
        raise HTTPException(status_code=400, detail="User already liked this movie")

    new_like = Like(
        user_id=data.user_id,
        movie_id=data.movie_id,
        comment=data.comment,
        like=1
    )
    db.add(new_like)
    db.commit()
    db.refresh(new_like)
    return {"message": "Movie liked successfully."}

# GET /likes/movies/{movie_id}
@router.get("/movies/{movie_id}")
def get_movie_likes(movie_id: int, db: Session = Depends(get_db)):
    total_likes = db.query(Like).filter_by(movie_id=movie_id, like=1).count()
    return {"movie_id": movie_id, "total_likes": total_likes}
