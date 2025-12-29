from typing import Dict, Any

from sqlalchemy.orm import Session

from app.services.movie_service import MovieService
from app.services.director_service import DirectorService
from app.services.genre_service import GenreService
from app.services.rating_service import RatingService


class ServiceFactory:
    """Factory for creating service instances"""
    
    def __init__(self, db: Session):
        self.db = db
        self._services: Dict[str, Any] = {}
    
    @property
    def movies(self) -> MovieService:
        """Get movie service instance"""
        if "movies" not in self._services:
            self._services["movies"] = MovieService(self.db)
        return self._services["movies"]
    
    @property
    def directors(self) -> DirectorService:
        """Get director service instance"""
        if "directors" not in self._services:
            self._services["directors"] = DirectorService(self.db)
        return self._services["directors"]
    
    @property
    def genres(self) -> GenreService:
        """Get genre service instance"""
        if "genres" not in self._services:
            self._services["genres"] = GenreService(self.db)
        return self._services["genres"]
    
    @property
    def ratings(self) -> RatingService:
        """Get rating service instance"""
        if "ratings" not in self._services:
            self._services["ratings"] = RatingService(self.db)
        return self._services["ratings"]
    
    def get_service(self, service_type: str):
        """Get service by type name"""
        service_map = {
            "movies": self.movies,
            "directors": self.directors,
            "genres": self.genres,
            "ratings": self.ratings,
        }
        
        if service_type not in service_map:
            raise ValueError(f"Unknown service type: {service_type}")
        
        return service_map[service_type]
