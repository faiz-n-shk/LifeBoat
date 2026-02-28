"""
Todos Controller
Business logic for todo management
"""
from datetime import datetime, date
from typing import List, Dict, Any
from peewee import DoesNotExist

from src.models.todo import Todo
from src.core.database import db
from src.core.activity_logger import activity_logger
from src.core.exceptions import RecordNotFoundError, DatabaseError


class TodosController:
    """Controller for todos operations"""
    
    def get_todos(self, filter_type: str = "all", category: str = None) -> List[Todo]:
        """Get todos with optional filtering"""
        try:
            db.connect(reuse_if_open=True)
            
            query = Todo.select()
            
            if filter_type == "active":
                query = query.where(Todo.completed == False)
            elif filter_type == "completed":
                query = query.where(Todo.completed == True)
            elif filter_type == "today":
                query = query.where(
                    (Todo.completed == False) & 
                    (Todo.due_date == date.today())
                )
            elif filter_type == "overdue":
                query = query.where(
                    (Todo.completed == False) & 
                    (Todo.due_date < date.today())
                )
            
            if category and category != "All":
                query = query.where(Todo.category == category)
            
            todos = list(query.order_by(Todo.order, Todo.created_at.desc()))
            db.close()
            return todos
        except Exception as e:
            raise DatabaseError(f"Failed to retrieve todos: {str(e)}")
    
    def create_todo(self, data: Dict[str, Any]) -> Todo:
        """Create a new todo"""
        try:
            db.connect(reuse_if_open=True)
            
            todo = Todo.create(
                title=data.get('title'),
                description=data.get('description'),
                priority=data.get('priority', 'Medium'),
                due_date=data.get('due_date'),
                category=data.get('category'),
                tags=data.get('tags'),
                order=data.get('order', 0)
            )
            
            db.close()
            
            activity_logger.log('Todos', 'Created', todo.title)
            
            return todo
        except Exception as e:
            raise DatabaseError(f"Failed to create todo: {str(e)}")
    
    def update_todo(self, todo_id: int, data: Dict[str, Any]) -> bool:
        """Update a todo"""
        try:
            db.connect(reuse_if_open=True)
            
            todo = Todo.get_by_id(todo_id)
            title = todo.title
            
            for key, value in data.items():
                if hasattr(todo, key):
                    setattr(todo, key, value)
            
            todo.updated_at = datetime.now()
            todo.save()
            
            db.close()
            
            activity_logger.log('Todos', 'Updated', title)
            
            return True
        except DoesNotExist:
            raise RecordNotFoundError("Todo not found or has been deleted")
        except Exception as e:
            raise DatabaseError(f"Failed to update todo: {str(e)}")
    
    def delete_todo(self, todo_id: int) -> bool:
        """Delete a todo"""
        try:
            db.connect(reuse_if_open=True)
            
            todo = Todo.get_by_id(todo_id)
            title = todo.title
            todo.delete_instance()
            
            db.close()
            
            activity_logger.log('Todos', 'Deleted', title)
            
            return True
        except DoesNotExist:
            raise RecordNotFoundError("Todo not found or has been deleted")
        except Exception as e:
            raise DatabaseError(f"Failed to delete todo: {str(e)}")
    
    def toggle_complete(self, todo_id: int) -> bool:
        """Toggle todo completion"""
        try:
            db.connect(reuse_if_open=True)
            
            todo = Todo.get_by_id(todo_id)
            todo.toggle_complete()
            
            status = "Completed" if todo.completed else "Uncompleted"
            activity_logger.log('Todos', status, todo.title)
            
            db.close()
            return True
        except DoesNotExist:
            raise RecordNotFoundError("Todo not found or has been deleted")
        except Exception as e:
            raise DatabaseError(f"Failed to toggle todo: {str(e)}")
    
    def get_categories(self) -> List[str]:
        """Get all unique categories"""
        try:
            db.connect(reuse_if_open=True)
            
            categories = set()
            todos = Todo.select()
            for todo in todos:
                if todo.category:
                    categories.add(todo.category)
            
            db.close()
            return sorted(list(categories))
        except Exception as e:
            raise DatabaseError(f"Failed to get categories: {str(e)}")
    
    def get_stats(self) -> Dict[str, int]:
        """Get todo statistics"""
        try:
            db.connect(reuse_if_open=True)
            
            total = Todo.select().count()
            active = Todo.select().where(Todo.completed == False).count()
            completed = Todo.select().where(Todo.completed == True).count()
            today = Todo.select().where(
                (Todo.completed == False) & 
                (Todo.due_date == date.today())
            ).count()
            overdue = Todo.select().where(
                (Todo.completed == False) & 
                (Todo.due_date < date.today())
            ).count()
            
            db.close()
            
            return {
                'total': total,
                'active': active,
                'completed': completed,
                'today': today,
                'overdue': overdue
            }
        except Exception as e:
            raise DatabaseError(f"Failed to get stats: {str(e)}")
    
    def reorder_todos(self, todo_ids: List[int]) -> bool:
        """Reorder todos"""
        try:
            db.connect(reuse_if_open=True)
            
            for order, todo_id in enumerate(todo_ids):
                todo = Todo.get_by_id(todo_id)
                todo.order = order
                todo.save()
            
            db.close()
            return True
        except DoesNotExist:
            raise RecordNotFoundError("One or more todos not found")
        except Exception as e:
            raise DatabaseError(f"Failed to reorder todos: {str(e)}")
