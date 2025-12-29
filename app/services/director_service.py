from typing import List, Optional

from sqlalchemy.orm import Session

from app.models import Director
from app.repositories import DirectorRepository, RepositoryFactory
from app.exceptions import NotFoundError, ValidationError, AlreadyExistsError


class DirectorService:
    """Service for director business logic"""
    
    def __init__(self, db: Session):
        self.db = db
        self._director_repo = None
        self._repo_factory = None
    
    def _get_director_repo(self) -> DirectorRepository:
        """Get director repository instance"""
        if self._director_repo is None:
            self._director_repo = DirectorRepository(self.db)
        return self._director_repo
    
    def _get_repo_factory(self) -> RepositoryFactory:
        """Get repository factory"""
        if self._repo_factory is None:
            self._repo_factory = RepositoryFactory(self.db)
        return self._repo_factory
    
    def get_director(self, director_id: int) -> Optional[Director]:
        """Get a director by ID"""
        return self._get_director_repo().get(director_id)
    
    def get_director_with_movies(self, director_id: int) -> Director:
        """Get director with their movies"""
        director = self._get_director_repo().get_with_movies(director_id)
        if not director:
            raise NotFoundError("Director", str(director_id))
        return director
    
    def create_director(self, name: str, birth_year: Optional[int] = None, 
                       description: Optional[str] = None) -> Director:
        """Create a new director with validation"""
        if not name or not name.strip():
            raise ValidationError("name", "Director name is required")
        
        if birth_year:
            if not (1800 <= birth_year <= 2100):
                raise ValidationError("birth_year", "Birth year must be between 1800 and 2100")
        
        existing = self._get_director_repo().get_by_field('name', name.strip())
        if existing:
            raise AlreadyExistsError("Director", name)
        
        director_data = {
            "name": name.strip(),
            "birth_year": birth_year,
            "description": description
        }
        
        return self._get_director_repo().create(director_data)
    
    def update_director(self, director_id: int, name: Optional[str] = None,
                       birth_year: Optional[int] = None, description: Optional[str] = None) -> Director:
        """Update a director with validation"""
        if not self._get_director_repo().exists(director_id):
            raise NotFoundError("Director", str(director_id))
        
        update_data = {}
        if name is not None:
            update_data["name"] = name.strip()
            existing = self._get_director_repo().get_by_field('name', name.strip())
            if existing and existing.id != director_id:
                raise AlreadyExistsError("Director", name)
        
        if birth_year is not None:
            if not (1800 <= birth_year <= 2100):
                raise ValidationError("birth_year", "Birth year must be between 1800 and 2100")
            update_data["birth_year"] = birth_year
        
        if description is not None:
            update_data["description"] = description
        
        director = self._get_director_repo().update(director_id, update_data)
        if not director:
            raise NotFoundError("Director", str(director_id))
        return director
    
    def delete_director(self, director_id: int) -> bool:
        """Delete a director by ID"""
        result = self._get_director_repo().delete(director_id)
        if not result:
            raise NotFoundError("Director", str(director_id))
        return result
    
    def get_all_directors(
        self, 
        skip: int = 0, 
        limit: int = 100,
        order_by: Optional[str] = None,
        order_direction: str = "asc"
    ) -> List[Director]:
        """Get all directors"""
        return self._get_director_repo().get_all(skip, limit, order_by, order_direction)
    
    def get_directors_with_movie_counts(
        self, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[dict]:
        """Get all directors with their movie counts"""
        return self._get_director_repo().get_all_with_movie_counts(skip, limit)
    
    def search_directors(self, name_query: str, skip: int = 0, limit: int = 100) -> List[Director]:
        """Search directors by name"""
        return self._get_director_repo().search_by_name(name_query, skip, limit)
    
    def get_director_stats(self, director_id: int) -> dict:
        """Get director statistics"""
        director = self.get_director_with_movies(director_id)
        
        movie_repo = self._get_repo_factory().movies
        director_movies = movie_repo.get_by_director(director_id, limit=1000)
        
        total_ratings = 0
        total_score = 0
        movie_count = len(director_movies)
        
        for movie in director_movies:
            avg_rating = self._get_repo_factory().ratings.get_movie_average_rating(movie.id)
            if avg_rating:
                total_ratings += 1
                total_score += avg_rating
        
        avg_director_rating = total_score / total_ratings if total_ratings > 0 else None
        
        return {
            "director": director,
            "movie_count": movie_count,
            "average_movie_rating": avg_director_rating
        }
    
    def get_directors_by_ids(self, director_ids: List[int]) -> List[Director]:
        """Get multiple directors by their IDs"""
        repo = self._get_director_repo()
        directors = []
        for director_id in director_ids:
            director = repo.get(director_id)
            if director:
                directors.append(director)
        return directors
    
    def count_directors(self) -> int:
        """Count total directors"""
        return self._get_director_repo().count()
    
    def director_exists(self, director_id: int) -> bool:
        """Check if a director exists by ID"""
        return self._get_director_repo().exists(director_id)
