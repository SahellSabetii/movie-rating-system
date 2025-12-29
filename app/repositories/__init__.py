from app.repositories.base import BaseRepository
from app.repositories.movie_repository import MovieRepository
from app.repositories.director_repository import DirectorRepository
from app.repositories.genre_repository import GenreRepository
from app.repositories.rating_repository import RatingRepository
from app.repositories.factory import RepositoryFactory
from app.repositories.deps import (
    get_repository_factory,
    get_movie_repository,
    get_director_repository,
    get_genre_repository,
    get_rating_repository
)


__all__ = [
    "BaseRepository",
    "MovieRepository",
    "DirectorRepository",
    "GenreRepository",
    "RatingRepository",
    "RepositoryFactory",
    "get_repository_factory",
    "get_movie_repository",
    "get_director_repository",
    "get_genre_repository",
    "get_rating_repository",
]
