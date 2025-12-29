from typing import Type, TypeVar, Generic, List, Optional, Dict, Any

from sqlalchemy.orm import Session
from sqlalchemy import asc, desc

from app.exceptions import NotFoundError, DatabaseError


ModelType = TypeVar("ModelType")


class BaseRepository(Generic[ModelType]):
    """Base repository with common CRUD operations"""
    
    def __init__(self, model: Type[ModelType], db: Session):
        self.model = model
        self.db = db
    
    def get(self, id: int) -> Optional[ModelType]:
        """Get a single record by ID"""
        try:
            return self.db.query(self.model).filter(self.model.id == id).first()
        except Exception as e:
            raise DatabaseError(f"Failed to get {self.model.__name__} with id {id}", e)
    
    def get_or_raise(self, id: int) -> ModelType:
        """Get a record by ID or raise NotFoundError"""
        obj = self.get(id)
        if not obj:
            raise NotFoundError(self.model.__name__, str(id))
        return obj
    
    def get_all(
        self, 
        skip: int = 0, 
        limit: int = 100,
        order_by: Optional[str] = None,
        order_direction: str = "asc"
    ) -> List[ModelType]:
        """Get all records with pagination and ordering"""
        try:
            query = self.db.query(self.model)
            
            if order_by:
                column = getattr(self.model, order_by, None)
                if column:
                    if order_direction.lower() == "desc":
                        query = query.order_by(desc(column))
                    else:
                        query = query.order_by(asc(column))
            
            return query.offset(skip).limit(limit).all()
        except Exception as e:
            raise DatabaseError(f"Failed to get all {self.model.__name__} records", e)
    
    def get_by_field(self, field: str, value: Any) -> Optional[ModelType]:
        """Get a record by a specific field"""
        try:
            column = getattr(self.model, field, None)
            if not column:
                raise ValueError(f"Field {field} not found in {self.model.__name__}")
            
            return self.db.query(self.model).filter(column == value).first()
        except ValueError as e:
            raise e
        except Exception as e:
            raise DatabaseError(f"Failed to get {self.model.__name__} by {field}={value}", e)
    
    def get_many_by_field(self, field: str, value: Any) -> List[ModelType]:
        """Get multiple records by a specific field"""
        try:
            column = getattr(self.model, field, None)
            if not column:
                raise ValueError(f"Field {field} not found in {self.model.__name__}")
            
            return self.db.query(self.model).filter(column == value).all()
        except ValueError as e:
            raise e
        except Exception as e:
            raise DatabaseError(f"Failed to get {self.model.__name__} records by {field}={value}", e)
    
    def create(self, obj_in: Dict[str, Any]) -> ModelType:
        """Create a new record"""
        try:
            db_obj = self.model(**obj_in)
            self.db.add(db_obj)
            self.db.commit()
            self.db.refresh(db_obj)
            return db_obj
        except Exception as e:
            self.db.rollback()
            raise DatabaseError(f"Failed to create {self.model.__name__}", e)
    
    def update(self, id: int, obj_in: Dict[str, Any]) -> ModelType:
        """Update an existing record"""
        try:
            db_obj = self.get_or_raise(id)
            
            for field, value in obj_in.items():
                if hasattr(db_obj, field) and value is not None:
                    setattr(db_obj, field, value)
            
            self.db.commit()
            self.db.refresh(db_obj)
            return db_obj
        except NotFoundError:
            raise
        except Exception as e:
            self.db.rollback()
            raise DatabaseError(f"Failed to update {self.model.__name__} with id {id}", e)
    
    def delete(self, id: int) -> bool:
        """Delete a record by ID"""
        try:
            db_obj = self.get_or_raise(id)
            self.db.delete(db_obj)
            self.db.commit()
            return True
        except NotFoundError:
            raise
        except Exception as e:
            self.db.rollback()
            raise DatabaseError(f"Failed to delete {self.model.__name__} with id {id}", e)
    
    def count(self) -> int:
        """Count total records"""
        try:
            return self.db.query(self.model).count()
        except Exception as e:
            raise DatabaseError(f"Failed to count {self.model.__name__} records", e)
    
    def exists(self, id: int) -> bool:
        """Check if a record exists by ID"""
        try:
            return self.db.query(self.model).filter(self.model.id == id).first() is not None
        except Exception as e:
            raise DatabaseError(f"Failed to check existence of {self.model.__name__} with id {id}", e)
    
    def exists_by_field(self, field: str, value: Any) -> bool:
        """Check if a record exists by field value"""
        try:
            column = getattr(self.model, field, None)
            if not column:
                raise ValueError(f"Field {field} not found in {self.model.__name__}")
            
            return self.db.query(self.model).filter(column == value).first() is not None
        except ValueError as e:
            raise e
        except Exception as e:
            raise DatabaseError(
                f"Failed to check existence of {self.model.__name__} by {field}={value}", 
                e
            )
