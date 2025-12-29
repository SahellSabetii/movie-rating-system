from app.exceptions.base import MovieRatingError


class NotFoundError(MovieRatingError):
    """Raised when a resource is not found"""
    def __init__(self, resource: str, resource_id: str):
        self.resource = resource
        self.resource_id = resource_id
        super().__init__(f"{resource} with id {resource_id} not found")


class AlreadyExistsError(MovieRatingError):
    """Raised when trying to create a resource that already exists"""
    def __init__(self, resource: str, identifier: str):
        self.resource = resource
        self.identifier = identifier
        super().__init__(f"{resource} '{identifier}' already exists")


class ValidationError(MovieRatingError):
    """Raised when input validation fails"""
    def __init__(self, field: str, message: str):
        self.field = field
        self.message = message
        super().__init__(f"Validation error for '{field}': {message}")
