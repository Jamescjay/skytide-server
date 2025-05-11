from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class UserBase(BaseModel):
    username: str
    email: str
    role: Optional[str] = None

class UserCreate(UserBase):
    password: str

class UserResponse(UserBase):
    id: int
    created_at: datetime

    class Config:
        orm_mode = True


class MovieBase(BaseModel):
    title: str
    description: str
    release_date: datetime
    poster: Optional[str] = None

class MovieCreate(MovieBase):
    pass

class MovieResponse(MovieBase):
    id: int
    created_at: datetime

    class Config:
        orm_mode = True


class ReviewBase(BaseModel):
    review: str
    user_id: int
    movie_id: int

class ReviewCreate(ReviewBase):
    pass

class ReviewResponse(ReviewBase):
    id: int
    created_at: datetime

    class Config:
        orm_mode = True


class LikeBase(BaseModel):
    user_id: int
    movie_id: int
    comment: Optional[str] = None
    like: Optional[int] = 0

class LikeCreate(BaseModel):
    movie_id: int
    like: int = 1  # 1 for like, 0 for unlike
    comment: Optional[str] = None

class LikeResponse(BaseModel):
    id: int
    user_id: int
    movie_id: int
    like: int
    created_at: datetime
    comment: Optional[str] = None

    class Config:
        orm_mode = True

class LikeCountResponse(BaseModel):
    movie_id: int
    total_likes: int



class FollowBase(BaseModel):
    following_user_id: int
    followed_user_id: int

class FollowCreate(FollowBase):
    pass

class FollowResponse(FollowBase):
    created_at: datetime

    class Config:
        orm_mode = True
