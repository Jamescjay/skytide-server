# resources/reviews.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime

import models, schemas
from database import get_db

router = APIRouter(prefix="/reviews", tags=["Reviews"])

# Get all reviews
@router.get("/", response_model=List[schemas.ReviewResponse])
def get_all_reviews(db: Session = Depends(get_db)):
    return db.query(models.Review).all()

# Create a new review (must be logged in)
@router.post("/", response_model=schemas.ReviewResponse)
def create_review(review: schemas.ReviewCreate, db: Session = Depends(get_db)):
    # Optional: Add authentication here to ensure user is logged in
    new_review = models.Review(
        review=review.review,
        user_id=review.user_id,
        movie_id=review.movie_id,
        created_at=datetime.utcnow()
    )
    db.add(new_review)
    db.commit()
    db.refresh(new_review)
    return new_review

# Update a review (only by owner)
@router.put("/{review_id}", response_model=schemas.ReviewResponse)
def update_review(review_id: int, updated_review: schemas.ReviewCreate, db: Session = Depends(get_db)):
    review = db.query(models.Review).filter(models.Review.id == review_id).first()
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")

    if review.user_id != updated_review.user_id:
        raise HTTPException(status_code=403, detail="Not authorized to update this review")

    review.review = updated_review.review
    review.movie_id = updated_review.movie_id
    db.commit()
    db.refresh(review)
    return review

# Delete a review (only by owner)
@router.delete("/{review_id}")
def delete_review(review_id: int, user_id: int, db: Session = Depends(get_db)):
    review = db.query(models.Review).filter(models.Review.id == review_id).first()
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")

    if review.user_id != user_id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this review")

    db.delete(review)
    db.commit()
    return {"message": "Review deleted successfully"}
