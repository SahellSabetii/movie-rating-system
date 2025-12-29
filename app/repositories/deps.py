from typing import Generator

from sqlalchemy.orm import Session

from app.db.session import get_db
from app.repositories.director_repository import DirectorRepository
from app.repositories.genre_repository import GenreRepository
from app.repositories.movie_repository import MovieRepository
from app.repositories.rating_repository import RatingRepository
from app.repositories.factory import RepositoryFactory


def get_repository_factory() -> Generator[RepositoryFactory, None, None]:
    """
    Dependency to get repository factory.
    """
    db: Session = next(get_db())
    try:
        yield RepositoryFactory(db)
    finally:
        db.close()


def get_movie_repository() -> Generator[MovieRepository, None, None]:
    """Dependency to get movie repository directly"""
    from app.repositories.movie_repository import MovieRepository
    db: Session = next(get_db())
    try:
        yield MovieRepository(db)
    finally:
        db.close()


def get_director_repository() -> Generator[DirectorRepository, None, None]:
    """Dependency to get director repository directly"""
    from app.repositories.director_repository import DirectorRepository
    db: Session = next(get_db())
    try:
        yield DirectorRepository(db)
    finally:
        db.close()


def get_genre_repository() -> Generator[GenreRepository, None, None]:
    """Dependency to get genre repository directly"""
    from app.repositories.genre_repository import GenreRepository
    db: Session = next(get_db())
    try:
        yield GenreRepository(db)
    finally:
        db.close()


def get_rating_repository() -> Generator[RatingRepository, None, None]:
    """Dependency to get rating repository directly"""
    from app.repositories.rating_repository import RatingRepository
    db: Session = next(get_db())
    try:
        yield RatingRepository(db)
    finally:
        db.close()
