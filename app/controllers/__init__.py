from .movie_controller import router as movies_router
from .director_controller import router as directors_router
from .genre_controller import router as genres_router
from .rating_controller import router as ratings_router


__all__ = ["movies_router", "directors_router", "genres_router", "ratings_router"]
