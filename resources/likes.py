from fastapi import APIRouter, Depends, HTTPException, Body
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


@router.get("/movies/{movie_id}/likes")
def get_movie_likes(movie_id: int, db: Session = Depends(get_db)):
    total_likes = db.query(Like).filter_by(movie_id=movie_id, like=1).count()
    return {"movie_id": movie_id, "total_likes": total_likes}


@router.get("/movies/{movie_id}/comments")
def get_comments(movie_id: int, db: Session = Depends(get_db)):
    comments = db.query(Like).filter(
        Like.movie_id == movie_id,
        Like.comment != None,
        Like.comment != ""
    ).all()

    return {
        "movie_id": movie_id,
        "total_comments": len(comments),
        "comments": [{"user_id": c.user_id, "comment": c.comment} for c in comments]
    }


@router.post("/movies/{movie_id}/comment")
def add_comment(
    movie_id: int,
    payload: dict = Body(...),  # expects {"user_id": 1, "comment": "Nice movie!"}
    db: Session = Depends(get_db)
):
    user_id = payload.get("user_id")
    comment = payload.get("comment")

    if not comment:
        raise HTTPException(status_code=400, detail="Comment cannot be empty")

    existing_like = db.query(Like).filter_by(user_id=user_id, movie_id=movie_id).first()

    if existing_like:
        # Update comment
        existing_like.comment = comment
        db.commit()
        db.refresh(existing_like)
        return {"message": "Comment updated"}
    else:
        # Create comment-only record
        new_like = Like(user_id=user_id, movie_id=movie_id, comment=comment, like=0)
        db.add(new_like)
        db.commit()
        db.refresh(new_like)
        return {"message": "Comment added"}
