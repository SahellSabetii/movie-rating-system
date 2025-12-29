from typing import List, Optional, Tuple

from sqlalchemy.orm import Session, joinedload
from sqlalchemy import select, func, and_, or_

from app.models import Movie, Director, Genre, MovieRating
from app.repositories.base import BaseRepository
from app.exceptions import NotFoundError, DatabaseError


class MovieRepository(BaseRepository[Movie]):
    """Repository for Movie model with specialized queries"""
    
    def __init__(self, db: Session):
        super().__init__(Movie, db)
    
    def get_by_title(self, title: str) -> Optional[Movie]:
        """Get a movie by exact title (case-insensitive)"""
        try:
            return (
                self.db.query(Movie)
                .filter(func.lower(Movie.title) == func.lower(title))
                .first()
            )
        except Exception as e:
            raise DatabaseError(f"Failed to get movie by title '{title}'", e)
    
    def get_with_details(self, movie_id: int) -> Optional[Movie]:
        """Get a movie with director, genres, and ratings loaded"""
        try:
            return (
                self.db.query(Movie)
                .options(
                    joinedload(Movie.director),
                    joinedload(Movie.genres),
                    joinedload(Movie.ratings)
                )
                .filter(Movie.id == movie_id)
                .first()
            )
        except Exception as e:
            raise DatabaseError(f"Failed to get movie {movie_id} with details", e)
    
    def get_all_with_details(
        self, 
        skip: int = 0, 
        limit: int = 100,
        order_by: Optional[str] = None,
        order_direction: str = "asc"
    ) -> List[Movie]:
        """Get all movies with director and genres loaded"""
        try:
            query = (
                self.db.query(Movie)
                .options(
                    joinedload(Movie.director),
                    joinedload(Movie.genres)
                )
            )
            
            if order_by:
                column = getattr(Movie, order_by, None)
                if column:
                    if order_direction.lower() == "desc":
                        query = query.order_by(column.desc())
                    else:
                        query = query.order_by(column.asc())
                else:
                    query = query.order_by(Movie.title.asc())
            else:
                query = query.order_by(Movie.title.asc())
            
            return query.offset(skip).limit(limit).all()
        except Exception as e:
            raise DatabaseError("Failed to get movies with details", e)
    
    def search_by_title(self, title_query: str, skip: int = 0, limit: int = 100) -> List[Movie]:
        """Search movies by title (case-insensitive partial match)"""
        try:
            return (
                self.db.query(Movie)
                .options(joinedload(Movie.director))
                .filter(Movie.title.ilike(f"%{title_query}%"))
                .order_by(Movie.title)
                .offset(skip)
                .limit(limit)
                .all()
            )
        except Exception as e:
            raise DatabaseError(f"Failed to search movies by title '{title_query}'", e)
    
    def get_by_director(self, director_id: int, skip: int = 0, limit: int = 100) -> List[Movie]:
        """Get all movies by a specific director"""
        try:
            return (
                self.db.query(Movie)
                .options(joinedload(Movie.director), joinedload(Movie.genres))
                .filter(Movie.director_id == director_id)
                .order_by(Movie.release_year.desc())
                .offset(skip)
                .limit(limit)
                .all()
            )
        except Exception as e:
            raise DatabaseError(f"Failed to get movies by director {director_id}", e)
    
    def get_by_genre(self, genre_id: int, skip: int = 0, limit: int = 100) -> List[Movie]:
        """Get all movies in a specific genre"""
        try:
            return (
                self.db.query(Movie)
                .join(Movie.genres)
                .options(joinedload(Movie.director))
                .filter(Genre.id == genre_id)
                .order_by(Movie.title)
                .offset(skip)
                .limit(limit)
                .all()
            )
        except Exception as e:
            raise DatabaseError(f"Failed to get movies by genre {genre_id}", e)
    
    def get_by_year_range(
        self, 
        start_year: Optional[int] = None, 
        end_year: Optional[int] = None,
        skip: int = 0, 
        limit: int = 100
    ) -> List[Movie]:
        """Get movies within a year range"""
        try:
            query = self.db.query(Movie).options(joinedload(Movie.director))
            
            if start_year and end_year:
                query = query.filter(
                    and_(
                        Movie.release_year >= start_year,
                        Movie.release_year <= end_year
                    )
                )
            elif start_year:
                query = query.filter(Movie.release_year >= start_year)
            elif end_year:
                query = query.filter(Movie.release_year <= end_year)
            
            return (
                query.order_by(Movie.release_year.desc())
                .offset(skip)
                .limit(limit)
                .all()
            )
        except Exception as e:
            raise DatabaseError(
                f"Failed to get movies by year range {start_year}-{end_year}", 
                e
            )
    
    def get_highest_rated(self, limit: int = 10, min_ratings: int = 10) -> List[Tuple[Movie, float]]:
        """Get highest rated movies with average rating"""
        try:
            avg_ratings = (
                select(
                    MovieRating.movie_id,
                    func.avg(MovieRating.score).label('avg_rating'),
                    func.count(MovieRating.id).label('rating_count')
                )
                .group_by(MovieRating.movie_id)
                .having(func.count(MovieRating.id) >= min_ratings)
                .subquery()
            )
            
            results = (
                self.db.query(Movie, avg_ratings.c.avg_rating)
                .join(avg_ratings, Movie.id == avg_ratings.c.movie_id)
                .options(joinedload(Movie.director))
                .order_by(avg_ratings.c.avg_rating.desc())
                .limit(limit)
                .all()
            )
            
            return [(movie, float(avg_rating)) for movie, avg_rating in results]
        except Exception as e:
            raise DatabaseError("Failed to get highest rated movies", e)
    
    def update_movie_genres(self, movie_id: int, genre_ids: List[int]) -> Movie:
        """Update movie's genres (replace existing ones)"""
        try:
            movie = self.get_or_raise(movie_id)
            
            movie.genres.clear()
            
            for genre_id in genre_ids:
                genre = self.db.query(Genre).filter(Genre.id == genre_id).first()
                if genre:
                    movie.genres.append(genre)
            
            self.db.commit()
            self.db.refresh(movie)
            return movie
        except NotFoundError:
            raise
        except Exception as e:
            self.db.rollback()
            raise DatabaseError(f"Failed to update genres for movie {movie_id}", e)
    
    def get_with_stats(self, movie_id: int) -> Optional[dict]:
        """Get movie with statistics (rating count, average)"""
        try:
            movie = self.get_with_details(movie_id)
            if not movie:
                return None
            
            stats = (
                self.db.query(
                    func.count(MovieRating.id).label('rating_count'),
                    func.avg(MovieRating.score).label('average_rating')
                )
                .filter(MovieRating.movie_id == movie_id)
                .first()
            )
            
            return {
                "movie": movie,
                "rating_count": stats.rating_count or 0,
                "average_rating": float(stats.average_rating) if stats.average_rating else None
            }
        except Exception as e:
            raise DatabaseError(f"Failed to get stats for movie {movie_id}", e)
