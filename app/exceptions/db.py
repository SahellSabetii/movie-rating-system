from app.exceptions.base import MovieRatingError


class DatabaseError(MovieRatingError):
    """Raised when a database operation fails"""
    def __init__(self, message: str, operation: str = None):
        self.message = message
        self.operation = operation
        if operation:
            super().__init__(f"Database error during {operation}: {message}")
        else:
            super().__init__(f"Database error: {message}")
