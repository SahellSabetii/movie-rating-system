from typing import List, Optional, Dict, Any
from datetime import datetime

from sqlalchemy.orm import Session

from app.models import MovieRating
from app.repositories import RatingRepository, RepositoryFactory
from app.exceptions import NotFoundError, ValidationError


class RatingService:
    """Service for rating business logic"""
    
    def __init__(self, db: Session):
        self.db = db
        self._rating_repo = None
        self._repo_factory = None
    
    def _get_rating_repo(self) -> RatingRepository:
        """Get rating repository instance"""
        if self._rating_repo is None:
            self._rating_repo = RatingRepository(self.db)
        return self._rating_repo
    
    def _get_repo_factory(self) -> RepositoryFactory:
        """Get repository factory"""
        if self._repo_factory is None:
            self._repo_factory = RepositoryFactory(self.db)
        return self._repo_factory
    
    def get_rating(self, rating_id: int) -> Optional[MovieRating]:
        """Get a rating by ID"""
        return self._get_rating_repo().get(rating_id)
    
    def create_rating(self, movie_id: int, score: int) -> MovieRating:
        """Create a new rating with validation"""
        movie_repo = self._get_repo_factory().movies
        if not movie_repo.exists(movie_id):
            raise ValidationError("movie_id", f"Movie with id {movie_id} does not exist")
        
        if not (1 <= score <= 10):
            raise ValidationError("score", "Score must be between 1 and 10")
        
        rating = MovieRating(movie_id=movie_id, score=score)
        self.db.add(rating)
        self.db.commit()
        self.db.refresh(rating)
        
        return rating
    
    def update_rating(self, rating_id: int, score: int) -> MovieRating:
        """Update a rating with validation"""
        rating = self._get_rating_repo().get(rating_id)
        if not rating:
            raise NotFoundError("Rating", str(rating_id))
        
        if not (1 <= score <= 10):
            raise ValidationError("score", "Score must be between 1 and 10")
        
        rating.score = score
        self.db.commit()
        self.db.refresh(rating)
        
        return rating
    
    def delete_rating(self, rating_id: int) -> bool:
        """Delete a rating by ID"""
        result = self._get_rating_repo().delete(rating_id)
        if not result:
            raise NotFoundError("Rating", str(rating_id))
        return result
    
    def get_movie_ratings(
        self, 
        movie_id: int, 
        skip: int = 0, 
        limit: int = 100,
        order_by: str = "created_at",
        order_direction: str = "desc"
    ) -> List[MovieRating]:
        """Get all ratings for a specific movie"""
        movie_repo = self._get_repo_factory().movies
        if not movie_repo.exists(movie_id):
            raise NotFoundError("Movie", str(movie_id))
        
        return self._get_rating_repo().get_movie_ratings(movie_id, skip, limit, order_by, order_direction)
    
    def get_movie_rating_stats(self, movie_id: int) -> Dict[str, Any]:
        """Get rating statistics for a movie"""
        movie_repo = self._get_repo_factory().movies
        if not movie_repo.exists(movie_id):
            raise NotFoundError("Movie", str(movie_id))
        
        return self._get_rating_repo().get_movie_rating_stats(movie_id)
    
    def get_average_rating(self, movie_id: int) -> Optional[float]:
        """Get average rating for a movie"""
        movie_repo = self._get_repo_factory().movies
        if not movie_repo.exists(movie_id):
            raise NotFoundError("Movie", str(movie_id))
        
        return self._get_rating_repo().get_movie_average_rating(movie_id)
    
    def get_recent_ratings(self, limit: int = 50) -> List[MovieRating]:
        """Get most recent ratings across all movies"""
        return self._get_rating_repo().get_recent_ratings(limit)

    def calculate_overall_stats(self) -> Dict[str, Any]:
        """Calculate overall rating statistics for all movies"""
        rating_repo = self._get_rating_repo()
        movie_repo = self._get_repo_factory().movies
        
        all_movies = movie_repo.get_all(limit=1000)
        
        total_movies_with_ratings = 0
        total_ratings = 0
        total_score = 0
        
        for movie in all_movies:
            stats = rating_repo.get_movie_rating_stats(movie.id)
            if stats['count'] > 0:
                total_movies_with_ratings += 1
                total_ratings += stats['count']
                total_score += stats['average'] * stats['count'] if stats['average'] else 0
        
        overall_average = total_score / total_ratings if total_ratings > 0 else None
        
        return {
            "total_movies_rated": total_movies_with_ratings,
            "total_ratings": total_ratings,
            "overall_average_rating": overall_average
        }
    
    def validate_rating_score(self, score: int) -> bool:
        """Validate that a rating score is within valid range"""
        return 1 <= score <= 10
    
    def get_ratings_by_movie_ids(self, movie_ids: List[int]) -> Dict[int, List[MovieRating]]:
        """Get ratings for multiple movies"""
        result = {}
        for movie_id in movie_ids:
            ratings = self.get_movie_ratings(movie_id, limit=100)
            result[movie_id] = ratings
        return result
    
    def count_ratings(self) -> int:
        """Count total ratings"""
        return self._get_rating_repo().count()
    
    def rating_exists(self, rating_id: int) -> bool:
        """Check if a rating exists by ID"""
        return self._get_rating_repo().exists(rating_id)
