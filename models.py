from sqlalchemy import Column, Integer, String, Text, ForeignKey, TIMESTAMP
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, nullable=False)
    email = Column(String, nullable=False, unique=True)
    role = Column(String, default='user')
    password = Column(String, nullable=False)
    created_at = Column(TIMESTAMP)

    # Relationships
    reviews = relationship('Review', back_populates='user')
    likes = relationship('Like', back_populates='user')
    following = relationship('Follow', foreign_keys='Follow.following_user_id', back_populates='follower')
    followers = relationship('Follow', foreign_keys='Follow.followed_user_id', back_populates='followed')


class Movie(Base):
    __tablename__ = 'movies'

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(Text)
    release_date = Column(TIMESTAMP)
    poster = Column(String)
    created_at = Column(TIMESTAMP)

    # Relationships
    reviews = relationship('Review', back_populates='movie')
    likes = relationship('Like', back_populates='movie')


class Review(Base):
    __tablename__ = 'reviews'

    id = Column(Integer, primary_key=True, index=True)
    review = Column(String)
    user_id = Column(Integer, ForeignKey('users.id'))
    movie_id = Column(Integer, ForeignKey('movies.id'))
    created_at = Column(TIMESTAMP)

    # Relationships
    user = relationship('User', back_populates='reviews')
    movie = relationship('Movie', back_populates='reviews')


class Like(Base):
    __tablename__ = 'likes'

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    movie_id = Column(Integer, ForeignKey('movies.id'))
    comment = Column(String)
    like = Column(Integer)
    created_at = Column(TIMESTAMP)

    user = relationship('User', back_populates='likes')
    movie = relationship('Movie', back_populates='likes')
    comment_obj = relationship('LikeComment', back_populates='like', uselist=False)


class LikeComment(Base):
    __tablename__ = 'like_comments'

    id = Column(Integer, primary_key=True, index=True)
    like_id = Column(Integer, ForeignKey('likes.id'), nullable=False)
    comment = Column(String, nullable=True)
    created_at = Column(TIMESTAMP)

    like = relationship('Like', back_populates='comment_obj')



class Follow(Base):
    __tablename__ = 'follows'

    following_user_id = Column(Integer, ForeignKey('users.id'), primary_key=True)
    followed_user_id = Column(Integer, ForeignKey('users.id'), primary_key=True)
    created_at = Column(TIMESTAMP)

    # Relationships
    follower = relationship('User', foreign_keys=[following_user_id], back_populates='following')
    followed = relationship('User', foreign_keys=[followed_user_id], back_populates='followers')
