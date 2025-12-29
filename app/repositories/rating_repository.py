from typing import List, Optional, Tuple

from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func, desc

from app.models import MovieRating, Movie
from app.repositories.base import BaseRepository
from app.exceptions import DatabaseError, ValidationError


class RatingRepository(BaseRepository[MovieRating]):
    """Repository for MovieRating model"""
    
    def __init__(self, db: Session):
        super().__init__(MovieRating, db)
    
    def get_movie_ratings(
        self, 
        movie_id: int, 
        skip: int = 0, 
        limit: int = 100,
        order_by: str = "created_at",
        order_direction: str = "desc"
    ) -> List[MovieRating]:
        """Get all ratings for a specific movie"""
        try:
            query = (
                self.db.query(MovieRating)
                .filter(MovieRating.movie_id == movie_id)
            )
            
            if order_by:
                column = getattr(MovieRating, order_by, None)
                if column:
                    if order_direction.lower() == "desc":
                        query = query.order_by(desc(column))
                    else:
                        query = query.order_by(column.asc())
            
            return query.offset(skip).limit(limit).all()
        except Exception as e:
            raise DatabaseError(f"Failed to get ratings for movie {movie_id}", e)
    
    def get_movie_average_rating(self, movie_id: int) -> Optional[float]:
        """Get average rating for a movie"""
        try:
            result = (
                self.db.query(func.avg(MovieRating.score))
                .filter(MovieRating.movie_id == movie_id)
                .scalar()
            )
            return float(result) if result else None
        except Exception as e:
            raise DatabaseError(f"Failed to get average rating for movie {movie_id}", e)
    
    def get_movie_rating_stats(self, movie_id: int) -> dict:
        """Get rating statistics for a movie"""
        try:
            result = (
                self.db.query(
                    func.count(MovieRating.id).label('count'),
                    func.avg(MovieRating.score).label('average'),
                    func.min(MovieRating.score).label('min'),
                    func.max(MovieRating.score).label('max')
                )
                .filter(MovieRating.movie_id == movie_id)
                .first()
            )
            
            return {
                "count": result.count or 0,
                "average": float(result.average) if result.average else None,
                "min": result.min,
                "max": result.max
            }
        except Exception as e:
            raise DatabaseError(f"Failed to get rating stats for movie {movie_id}", e)
    
    def create_rating(self, movie_id: int, score: int) -> MovieRating:
        """Create a new rating with validation"""
        try:
            if not (1 <= score <= 10):
                raise ValidationError("score", "Score must be between 1 and 10")
            
            movie_exists = self.db.query(Movie).filter(Movie.id == movie_id).first()
            if not movie_exists:
                raise ValidationError("movie_id", f"Movie with id {movie_id} does not exist")
            
            rating = MovieRating(movie_id=movie_id, score=score)
            self.db.add(rating)
            self.db.commit()
            self.db.refresh(rating)
            
            return rating
        except ValidationError:
            raise
        except Exception as e:
            self.db.rollback()
            raise DatabaseError(f"Failed to create rating for movie {movie_id}", e)
    
    def get_recent_ratings(self, limit: int = 50) -> List[MovieRating]:
        """Get most recent ratings across all movies"""
        try:
            return (
                self.db.query(MovieRating)
                .options(joinedload(MovieRating.movie))
                .order_by(desc(MovieRating.created_at))
                .limit(limit)
                .all()
            )
        except Exception as e:
            raise DatabaseError("Failed to get recent ratings", e)
    
    def get_user_ratings(self, user_id: str, skip: int = 0, limit: int = 100) -> List[MovieRating]:
        """Get ratings by a specific user (if user system is added later)"""
        try:
            return (
                self.db.query(MovieRating)
                .options(joinedload(MovieRating.movie))
                .order_by(desc(MovieRating.created_at))
                .offset(skip)
                .limit(limit)
                .all()
            )
        except Exception as e:
            raise DatabaseError(f"Failed to get ratings for user {user_id}", e)
