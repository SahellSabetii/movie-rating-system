from typing import Generator

from sqlalchemy.orm import Session

from app.db.session import get_db
from app.services.factory import ServiceFactory
from app.services.movie_service import MovieService
from app.services.director_service import DirectorService
from app.services.genre_service import GenreService
from app.services.rating_service import RatingService


def get_service_factory() -> Generator[ServiceFactory, None, None]:
    """Dependency to get service factory."""
    db: Session = next(get_db())
    try:
        yield ServiceFactory(db)
    finally:
        db.close()


def get_movie_service() -> Generator[MovieService, None, None]:
    """Dependency to get movie service directly"""
    from app.services.movie_service import MovieService
    db: Session = next(get_db())
    try:
        yield MovieService(db)
    finally:
        db.close()


def get_director_service() -> Generator[DirectorService, None, None]:
    """Dependency to get director service directly"""
    from app.services.director_service import DirectorService
    db: Session = next(get_db())
    try:
        yield DirectorService(db)
    finally:
        db.close()


def get_genre_service() -> Generator[GenreService, None, None]:
    """Dependency to get genre service directly"""
    from app.services.genre_service import GenreService
    db: Session = next(get_db())
    try:
        yield GenreService(db)
    finally:
        db.close()


def get_rating_service() -> Generator[RatingService, None, None]:
    """Dependency to get rating service directly"""
    from app.services.rating_service import RatingService
    db: Session = next(get_db())
    try:
        yield RatingService(db)
    finally:
        db.close()
