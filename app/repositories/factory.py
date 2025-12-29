from typing import Dict, Any

from sqlalchemy.orm import Session

from app.repositories.movie_repository import MovieRepository
from app.repositories.director_repository import DirectorRepository
from app.repositories.genre_repository import GenreRepository
from app.repositories.rating_repository import RatingRepository


class RepositoryFactory:
    """Factory for creating repository instances"""
    
    def __init__(self, db: Session):
        self.db = db
        self._repositories: Dict[str, Any] = {}
    
    @property
    def movies(self) -> MovieRepository:
        """Get movie repository instance"""
        if "movies" not in self._repositories:
            self._repositories["movies"] = MovieRepository(self.db)
        return self._repositories["movies"]
    
    @property
    def directors(self) -> DirectorRepository:
        """Get director repository instance"""
        if "directors" not in self._repositories:
            self._repositories["directors"] = DirectorRepository(self.db)
        return self._repositories["directors"]
    
    @property
    def genres(self) -> GenreRepository:
        """Get genre repository instance"""
        if "genres" not in self._repositories:
            self._repositories["genres"] = GenreRepository(self.db)
        return self._repositories["genres"]
    
    @property
    def ratings(self) -> RatingRepository:
        """Get rating repository instance"""
        if "ratings" not in self._repositories:
            self._repositories["ratings"] = RatingRepository(self.db)
        return self._repositories["ratings"]
    
    def get_repository(self, repo_type: str):
        """Get repository by type name"""
        repo_map = {
            "movies": self.movies,
            "directors": self.directors,
            "genres": self.genres,
            "ratings": self.ratings,
        }
        
        if repo_type not in repo_map:
            raise ValueError(f"Unknown repository type: {repo_type}")
        
        return repo_map[repo_type]
