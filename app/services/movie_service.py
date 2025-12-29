from typing import List, Optional, Dict, Any

from sqlalchemy.orm import Session

from app.models import Movie, Director, Genre
from app.repositories import MovieRepository, RepositoryFactory
from app.exceptions import NotFoundError, ValidationError, AlreadyExistsError


class MovieService:
    """Service for movie business logic"""
    
    def __init__(self, db: Session):
        self.db = db
        self._movie_repo = None
        self._repo_factory = None
    
    def _get_movie_repo(self) -> MovieRepository:
        """Get movie repository instance"""
        if self._movie_repo is None:
            self._movie_repo = MovieRepository(self.db)
        return self._movie_repo
    
    def _get_repo_factory(self) -> RepositoryFactory:
        """Get repository factory"""
        if self._repo_factory is None:
            self._repo_factory = RepositoryFactory(self.db)
        return self._repo_factory
    
    def get_movie(self, movie_id: int) -> Optional[Movie]:
        """Get a movie by ID"""
        return self._get_movie_repo().get(movie_id)
    
    def get_movie_with_details(self, movie_id: int) -> Movie:
        """Get movie with director, genres, and ratings"""
        movie = self._get_movie_repo().get_with_details(movie_id)
        if not movie:
            raise NotFoundError("Movie", str(movie_id))
        return movie
    
    def get_all_movies(
        self, 
        skip: int = 0, 
        limit: int = 100,
        order_by: Optional[str] = None,
        order_direction: str = "asc"
    ) -> List[Movie]:
        """Get all movies with director and genres loaded"""
        return self._get_movie_repo().get_all_with_details(skip, limit, order_by, order_direction)
    
    def create_movie(self, title: str, director_id: int, release_year: Optional[int] = None, 
                    cast: Optional[str] = None, genre_ids: Optional[List[int]] = None) -> Movie:
        """Create a new movie with validation"""
        if not title or not title.strip():
            raise ValidationError("title", "Title is required")
        
        director_repo = self._get_repo_factory().directors
        if not director_repo.exists(director_id):
            raise ValidationError("director_id", f"Director with id {director_id} does not exist")
        
        if release_year:
            if not (1888 <= release_year <= 2100):
                raise ValidationError("release_year", "Release year must be between 1888 and 2100")
        
        existing = self._get_movie_repo().get_by_field('name', title.strip())
        if existing:
            raise AlreadyExistsError("Movie", title)

        movie_data = {
            "title": title.strip(),
            "director_id": director_id,
            "release_year": release_year,
            "cast": cast
        }
        
        movie = self._get_movie_repo().create(movie_data)
        
        if genre_ids:
            self.update_movie_genres(movie.id, genre_ids)
        
        return movie
    
    def update_movie(self, movie_id: int, title: Optional[str] = None, 
                    director_id: Optional[int] = None, release_year: Optional[int] = None,
                    cast: Optional[str] = None, genre_ids: Optional[List[int]] = None) -> Movie:
        """Update a movie with validation"""
        if not self._get_movie_repo().exists(movie_id):
            raise NotFoundError("Movie", str(movie_id))
        
        update_data = {}
        if title is not None:
            update_data["title"] = title.strip()
        if director_id is not None:
            director_repo = self._get_repo_factory().directors
            if not director_repo.exists(director_id):
                raise ValidationError("director_id", f"Director with id {director_id} does not exist")
            update_data["director_id"] = director_id
        if release_year is not None:
            if not (1888 <= release_year <= 2100):
                raise ValidationError("release_year", "Release year must be between 1888 and 2100")
            update_data["release_year"] = release_year
        if cast is not None:
            update_data["cast"] = cast
        
        movie = self._get_movie_repo().update(movie_id, update_data)
        if not movie:
            raise NotFoundError("Movie", str(movie_id))
        
        if genre_ids is not None:
            self.update_movie_genres(movie_id, genre_ids)
        
        return movie
    
    def update_movie_genres(self, movie_id: int, genre_ids: List[int]) -> Movie:
        """Update movie's genres"""
        if not self._get_movie_repo().exists(movie_id):
            raise NotFoundError("Movie", str(movie_id))
        
        genre_repo = self._get_repo_factory().genres
        for genre_id in genre_ids:
            if not genre_repo.exists(genre_id):
                raise ValidationError("genre_ids", f"Genre with id {genre_id} does not exist")
        
        movie = self._get_movie_repo().update_movie_genres(movie_id, genre_ids)
        if not movie:
            raise NotFoundError("Movie", str(movie_id))
        return movie
    
    def delete_movie(self, movie_id: int) -> bool:
        """Delete a movie by ID"""
        result = self._get_movie_repo().delete(movie_id)
        if not result:
            raise NotFoundError("Movie", str(movie_id))
        return result
    
    def search_movies(
        self, 
        title_query: Optional[str] = None,
        director_id: Optional[int] = None,
        genre_id: Optional[int] = None,
        min_year: Optional[int] = None,
        max_year: Optional[int] = None,
        skip: int = 0, 
        limit: int = 100
    ) -> List[Movie]:
        """Search movies with multiple filters"""
        repo = self._get_movie_repo()
        
        if title_query:
            return repo.search_by_title(title_query, skip, limit)
        elif director_id:
            return repo.get_by_director(director_id, skip, limit)
        elif genre_id:
            return repo.get_by_genre(genre_id, skip, limit)
        elif min_year or max_year:
            return repo.get_by_year_range(min_year, max_year, skip, limit)
        else:
            return self.get_all_movies(skip, limit)
    
    def get_movie_stats(self, movie_id: int) -> Dict[str, Any]:
        """Get movie statistics (ratings, average, etc.)"""
        movie_with_stats = self._get_movie_repo().get_with_stats(movie_id)
        if not movie_with_stats:
            raise NotFoundError("Movie", str(movie_id))
        
        return {
            "movie": movie_with_stats["movie"],
            "rating_count": movie_with_stats["rating_count"],
            "average_rating": movie_with_stats["average_rating"]
        }
    
    def get_highest_rated_movies(self, limit: int = 10, min_ratings: int = 10) -> List[Dict[str, Any]]:
        """Get highest rated movies with their average ratings"""
        results = self._get_movie_repo().get_highest_rated(limit, min_ratings)
        
        return [
            {
                "movie": movie,
                "average_rating": avg_rating
            }
            for movie, avg_rating in results
        ]
    
    def calculate_movie_average_rating(self, movie_id: int) -> Optional[float]:
        """Calculate and return average rating for a movie"""
        rating_repo = self._get_repo_factory().ratings
        return rating_repo.get_movie_average_rating(movie_id)
    
    def get_movies_by_ids(self, movie_ids: List[int]) -> List[Movie]:
        """Get multiple movies by their IDs"""
        repo = self._get_movie_repo()
        movies = []
        for movie_id in movie_ids:
            movie = repo.get(movie_id)
            if movie:
                movies.append(movie)
        return movies
    
    def count_movies(self) -> int:
        """Count total movies"""
        return self._get_movie_repo().count()
    
    def movie_exists(self, movie_id: int) -> bool:
        """Check if a movie exists by ID"""
        return self._get_movie_repo().exists(movie_id)
