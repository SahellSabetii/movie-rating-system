from typing import List, Optional

from sqlalchemy import select, func
from sqlalchemy.orm import Session, joinedload

from app.models import Director, Movie
from app.repositories.base import BaseRepository
from app.exceptions import DatabaseError


class DirectorRepository(BaseRepository[Director]):
    """Repository for Director model"""
    
    def __init__(self, db: Session):
        super().__init__(Director, db)
    
    def get_with_movies(self, director_id: int) -> Optional[Director]:
        """Get director with their movies loaded"""
        try:
            return (
                self.db.query(Director)
                .options(joinedload(Director.movies))
                .filter(Director.id == director_id)
                .first()
            )
        except Exception as e:
            raise DatabaseError(f"Failed to get director {director_id} with movies", e)
    
    def get_all_with_movie_counts(
        self, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[dict]:
        """Get all directors with movie counts"""
        try:
            results = (
                self.db.query(
                    Director,
                    func.count(Movie.id).label('movie_count')
                )
                .outerjoin(Movie, Director.id == Movie.director_id)
                .group_by(Director.id)
                .order_by(Director.name)
                .offset(skip)
                .limit(limit)
                .all()
            )
            
            return [
                {
                    "director": director,
                    "movie_count": movie_count
                }
                for director, movie_count in results
            ]
        except Exception as e:
            raise DatabaseError("Failed to get directors with movie counts", e)
    
    def search_by_name(self, name_query: str, skip: int = 0, limit: int = 100) -> List[Director]:
        """Search directors by name (case-insensitive partial match)"""
        try:
            return (
                self.db.query(Director)
                .filter(Director.name.ilike(f"%{name_query}%"))
                .order_by(Director.name)
                .offset(skip)
                .limit(limit)
                .all()
            )
        except Exception as e:
            raise DatabaseError(f"Failed to search directors by name '{name_query}'", e)
