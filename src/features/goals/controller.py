"""
Goals Controller
Business logic for goals management
"""
from datetime import datetime
from src.models.goal import Goal
from src.core.database import db
from src.core.activity_logger import activity_logger


class GoalsController:
    """Controller for goals operations"""
    
    def get_goals(self, completed=None):
        """Get goals, optionally filtered by completion status"""
        try:
            db.connect(reuse_if_open=True)
            query = Goal.select().order_by(Goal.created_at.desc())
            
            if completed is not None:
                query = query.where(Goal.completed == completed)
            
            goals = list(query)
            db.close()
            return goals
        except Exception as e:
            print(f"Error getting goals: {e}")
            return []
    
    def create_goal(self, title, description=None, target_date=None, category=None):
        """Create a new goal"""
        try:
            db.connect(reuse_if_open=True)
            goal = Goal.create(
                title=title,
                description=description,
                target_date=target_date,
                category=category,
                progress=0,
                completed=False
            )
            db.close()
            activity_logger.log('Goals', 'Created', title)
            return goal
        except Exception as e:
            print(f"Error creating goal: {e}")
            return None
    
    def update_goal(self, goal_id, **kwargs):
        """Update a goal"""
        try:
            db.connect(reuse_if_open=True)
            goal = Goal.get_by_id(goal_id)
            title = goal.title
            
            for key, value in kwargs.items():
                if hasattr(goal, key):
                    setattr(goal, key, value)
            
            goal.updated_at = datetime.now()
            goal.save()
            db.close()
            activity_logger.log('Goals', 'Updated', title)
            return goal
        except Exception as e:
            print(f"Error updating goal: {e}")
            return None
    
    def delete_goal(self, goal_id):
        """Delete a goal"""
        try:
            db.connect(reuse_if_open=True)
            goal = Goal.get_by_id(goal_id)
            title = goal.title
            goal.delete_instance()
            db.close()
            activity_logger.log('Goals', 'Deleted', title)
            return True
        except Exception as e:
            print(f"Error deleting goal: {e}")
            return False
    
    def update_progress(self, goal_id, progress):
        """Update goal progress (0-100)"""
        try:
            db.connect(reuse_if_open=True)
            goal = Goal.get_by_id(goal_id)
            goal.progress = max(0, min(100, progress))
            
            # Update completed status based on progress
            if goal.progress >= 100:
                goal.completed = True
            else:
                goal.completed = False
            
            goal.updated_at = datetime.now()
            goal.save()
            db.close()
            return goal
        except Exception as e:
            print(f"Error updating progress: {e}")
            return None
    
    def toggle_complete(self, goal_id):
        """Toggle goal completion status"""
        try:
            db.connect(reuse_if_open=True)
            goal = Goal.get_by_id(goal_id)
            goal.completed = not goal.completed
            
            if goal.completed:
                goal.progress = 100
            
            goal.updated_at = datetime.now()
            goal.save()
            db.close()
            return goal
        except Exception as e:
            print(f"Error toggling completion: {e}")
            return None
