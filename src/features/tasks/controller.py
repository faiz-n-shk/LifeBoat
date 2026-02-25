"""
Tasks Controller
Business logic for tasks
"""
from typing import List, Dict, Any
from datetime import datetime

from src.models.task import Task
from src.core.database import db


class TasksController:
    """Controller for tasks operations"""
    
    def get_tasks(self, filter_type: str = "All") -> List[Task]:
        """
        Get tasks based on filter
        
        Args:
            filter_type: "All", "Active", or "Completed"
        
        Returns:
            List of Task objects
        """
        try:
            db.connect(reuse_if_open=True)
            
            if filter_type == "Active":
                tasks = Task.select().where(Task.completed == False).order_by(Task.created_at.desc())
            elif filter_type == "Completed":
                tasks = Task.select().where(Task.completed == True).order_by(Task.completed_at.desc())
            else:  # All
                tasks = Task.select().order_by(Task.completed, Task.created_at.desc())
            
            return list(tasks)
        except Exception as e:
            print(f"Error getting tasks: {e}")
            return []
        finally:
            db.close()
    
    def create_task(self, task_data: Dict[str, Any]) -> Task:
        """Create a new task"""
        try:
            db.connect(reuse_if_open=True)
            task = Task.create(**task_data)
            return task
        except Exception as e:
            print(f"Error creating task: {e}")
            return None
        finally:
            db.close()
    
    def update_task(self, task_id: int, task_data: Dict[str, Any]) -> bool:
        """Update a task"""
        try:
            db.connect(reuse_if_open=True)
            task = Task.get_by_id(task_id)
            
            for key, value in task_data.items():
                setattr(task, key, value)
            
            task.updated_at = datetime.now()
            task.save()
            return True
        except Exception as e:
            print(f"Error updating task: {e}")
            return False
        finally:
            db.close()
    
    def delete_task(self, task_id: int) -> bool:
        """Delete a task"""
        try:
            db.connect(reuse_if_open=True)
            task = Task.get_by_id(task_id)
            task.delete_instance()
            return True
        except Exception as e:
            print(f"Error deleting task: {e}")
            return False
        finally:
            db.close()
    
    def toggle_complete(self, task_id: int) -> bool:
        """Toggle task completion status"""
        try:
            db.connect(reuse_if_open=True)
            task = Task.get_by_id(task_id)
            task.completed = not task.completed
            task.completed_at = datetime.now() if task.completed else None
            task.updated_at = datetime.now()
            task.save()
            return True
        except Exception as e:
            print(f"Error toggling task: {e}")
            return False
        finally:
            db.close()
