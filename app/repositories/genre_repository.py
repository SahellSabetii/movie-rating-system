from typing import List, Optional

from sqlalchemy import func, select
from sqlalchemy.orm import Session, joinedload

from app.models import Genre, Movie
from app.repositories.base import BaseRepository
from app.exceptions import DatabaseError


class GenreRepository(BaseRepository[Genre]):
    """Repository for Genre model"""
    
    def __init__(self, db: Session):
        super().__init__(Genre, db)
    
    def get_with_movies(self, genre_id: int) -> Optional[Genre]:
        """Get genre with associated movies loaded"""
        try:
            return (
                self.db.query(Genre)
                .options(joinedload(Genre.movies))
                .filter(Genre.id == genre_id)
                .first()
            )
        except Exception as e:
            raise DatabaseError(f"Failed to get genre {genre_id} with movies", e)
    
    def get_all_with_movie_counts(self, skip: int = 0, limit: int = 100) -> List[dict]:
        """Get all genres with movie counts"""
        try:
            results = (
                self.db.query(
                    Genre,
                    func.count(Movie.id).label('movie_count')
                )
                .outerjoin(Movie.genres)
                .group_by(Genre.id)
                .order_by(Genre.name)
                .offset(skip)
                .limit(limit)
                .all()
            )
            
            return [
                {
                    "genre": genre,
                    "movie_count": movie_count
                }
                for genre, movie_count in results
            ]
        except Exception as e:
            raise DatabaseError("Failed to get genres with movie counts", e)
    
    def get_by_name(self, name: str) -> Optional[Genre]:
        """Get genre by exact name (case-insensitive)"""
        try:
            return (
                self.db.query(Genre)
                .filter(func.lower(Genre.name) == func.lower(name))
                .first()
            )
        except Exception as e:
            raise DatabaseError(f"Failed to get genre by name '{name}'", e)
