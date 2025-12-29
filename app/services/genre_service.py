from typing import List, Optional

from sqlalchemy.orm import Session

from app.models import Genre
from app.repositories import GenreRepository, RepositoryFactory
from app.exceptions import NotFoundError, ValidationError, AlreadyExistsError


class GenreService:
    """Service for genre business logic"""
    
    def __init__(self, db: Session):
        self.db = db
        self._genre_repo = None
        self._repo_factory = None
    
    def _get_genre_repo(self) -> GenreRepository:
        """Get genre repository instance"""
        if self._genre_repo is None:
            self._genre_repo = GenreRepository(self.db)
        return self._genre_repo
    
    def _get_repo_factory(self) -> RepositoryFactory:
        """Get repository factory"""
        if self._repo_factory is None:
            self._repo_factory = RepositoryFactory(self.db)
        return self._repo_factory
    
    def get_genre(self, genre_id: int) -> Optional[Genre]:
        """Get a genre by ID"""
        return self._get_genre_repo().get(genre_id)
    
    def get_genre_with_movies(self, genre_id: int) -> Genre:
        """Get genre with associated movies"""
        genre = self._get_genre_repo().get_with_movies(genre_id)
        if not genre:
            raise NotFoundError("Genre", str(genre_id))
        return genre
    
    def create_genre(self, name: str, description: Optional[str] = None) -> Genre:
        """Create a new genre with validation"""
        if not name or not name.strip():
            raise ValidationError("name", "Genre name is required")
        
        existing = self._get_genre_repo().get_by_field('name', name.strip())
        if existing:
            raise AlreadyExistsError("Genre", name)
        
        genre_data = {
            "name": name.strip(),
            "description": description
        }
        
        return self._get_genre_repo().create(genre_data)
    
    def update_genre(self, genre_id: int, name: Optional[str] = None, 
                    description: Optional[str] = None) -> Genre:
        """Update a genre with validation"""
        if not self._get_genre_repo().exists(genre_id):
            raise NotFoundError("Genre", str(genre_id))
        
        update_data = {}
        if name is not None:
            update_data["name"] = name.strip()
            existing = self._get_genre_repo().get_by_field('name', name.strip())
            if existing and existing.id != genre_id:
                raise AlreadyExistsError("Genre", name)
        
        if description is not None:
            update_data["description"] = description
        
        genre = self._get_genre_repo().update(genre_id, update_data)
        if not genre:
            raise NotFoundError("Genre", str(genre_id))
        return genre
    
    def delete_genre(self, genre_id: int) -> bool:
        """Delete a genre by ID"""
        result = self._get_genre_repo().delete(genre_id)
        if not result:
            raise NotFoundError("Genre", str(genre_id))
        return result
    
    def get_all_genres(
        self, 
        skip: int = 0, 
        limit: int = 100,
        order_by: Optional[str] = None,
        order_direction: str = "asc"
    ) -> List[Genre]:
        """Get all genres"""
        return self._get_genre_repo().get_all(skip, limit, order_by, order_direction)
    
    def get_genres_with_movie_counts(
        self, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[dict]:
        """Get all genres with their movie counts"""
        return self._get_genre_repo().get_all_with_movie_counts(skip, limit)
    
    def get_genre_by_name(self, name: str) -> Optional[Genre]:
        """Get genre by exact name (case-insensitive)"""
        return self._get_genre_repo().get_by_name(name)
    
    def get_popular_genres(self, limit: int = 10) -> List[dict]:
        """Get most popular genres by movie count"""
        genres_with_counts = self.get_genres_with_movie_counts(limit=limit)
        
        genres_with_counts.sort(key=lambda x: x['movie_count'], reverse=True)
        
        return genres_with_counts[:limit]
    
    def get_genres_by_ids(self, genre_ids: List[int]) -> List[Genre]:
        """Get multiple genres by their IDs"""
        repo = self._get_genre_repo()
        genres = []
        for genre_id in genre_ids:
            genre = repo.get(genre_id)
            if genre:
                genres.append(genre)
        return genres
    
    def count_genres(self) -> int:
        """Count total genres"""
        return self._get_genre_repo().count()
    
    def genre_exists(self, genre_id: int) -> bool:
        """Check if a genre exists by ID"""
        return self._get_genre_repo().exists(genre_id)
