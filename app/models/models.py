from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Table, CheckConstraint, UniqueConstraint
from sqlalchemy.sql import func, select
from sqlalchemy.orm import relationship
from sqlalchemy.ext.hybrid import hybrid_property

from app.db.base import Base


movie_genre_association = Table(
    'movie_genres',
    Base.metadata,
    Column('id', Integer, primary_key=True),
    Column('movie_id', Integer, ForeignKey('movies.id', ondelete='CASCADE'), nullable=False),
    Column('genre_id', Integer, ForeignKey('genres.id', ondelete='CASCADE'), nullable=False),
    UniqueConstraint('movie_id', 'genre_id', name='unique_movie_genre')
)


class Director(Base):
    __tablename__ = 'directors'
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    birth_year = Column(Integer, nullable=True)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    movies = relationship('Movie', back_populates='director', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f"<Director(id={self.id}, name='{self.name}')>"


class Genre(Base):
    __tablename__ = 'genres'
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, unique=True)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    movies = relationship('Movie', secondary=movie_genre_association, back_populates='genres')
    
    def __repr__(self):
        return f"<Genre(id={self.id}, name='{self.name}')>"


class Movie(Base):
    __tablename__ = 'movies'
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(300), nullable=False, index=True)
    director_id = Column(Integer, ForeignKey('directors.id', ondelete='SET NULL'), nullable=True)
    release_year = Column(Integer, nullable=True)
    cast = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    director = relationship('Director', back_populates='movies')
    genres = relationship('Genre', secondary=movie_genre_association, back_populates='movies')
    ratings = relationship('MovieRating', back_populates='movie', cascade='all, delete-orphan')
    
    @hybrid_property
    def average_rating(self):
        if self.ratings:
            return round(sum(rating.score for rating in self.ratings) / len(self.ratings), 1)
        return None
    
    @average_rating.expression
    def average_rating(cls):
        return (
            select(func.avg(MovieRating.score))
            .where(MovieRating.movie_id == cls.id)
            .label('average_rating')
        )
    
    @hybrid_property
    def ratings_count(self):
        return len(self.ratings) if self.ratings else 0
    
    @ratings_count.expression
    def ratings_count(cls):
        return (
            select(func.count(MovieRating.id))
            .where(MovieRating.movie_id == cls.id)
            .label('ratings_count')
        )
    
    def __repr__(self):
        return f"<Movie(id={self.id}, title='{self.title}')>"


class MovieRating(Base):
    __tablename__ = 'movie_ratings'
    
    id = Column(Integer, primary_key=True, index=True)
    movie_id = Column(Integer, ForeignKey('movies.id', ondelete='CASCADE'), nullable=False)
    score = Column(Integer, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    movie = relationship('Movie', back_populates='ratings')
    
    __table_args__ = (
        CheckConstraint('score >= 1 AND score <= 10', name='check_score_range'),
    )
    
    def __repr__(self):
        return f"<MovieRating(id={self.id}, movie_id={self.movie_id}, score={self.score})>"
