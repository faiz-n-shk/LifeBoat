"""
Habits Controller
Business logic for habit tracking
"""
from datetime import datetime, date, timedelta
from peewee import DoesNotExist

from src.models.habit import Habit, HabitLog
from src.core.database import db
from src.core.activity_logger import activity_logger
from src.core.exceptions import RecordNotFoundError, DatabaseError


class HabitsController:
    """Controller for habits operations"""
    
    def get_habits(self):
        """Get all habits"""
        try:
            db.connect(reuse_if_open=True)
            habits = list(Habit.select().order_by(Habit.created_at.desc()))
            db.close()
            return habits
        except Exception as e:
            raise DatabaseError(f"Failed to retrieve habits: {str(e)}")
    
    def create_habit(self, name, description=None, habit_type="Good", target_days=7, color="#0078d4"):
        """Create a new habit"""
        try:
            db.connect(reuse_if_open=True)
            habit = Habit.create(
                name=name,
                description=description,
                habit_type=habit_type,
                target_days=target_days,
                start_date=date.today(),
                frequency="Daily",
                target_count=1,
                color=color
            )
            db.close()
            activity_logger.log('Habits', 'Created', name)
            return habit
        except Exception as e:
            raise DatabaseError(f"Failed to create habit: {str(e)}")
    
    def update_habit(self, habit_id, **kwargs):
        """Update a habit"""
        try:
            db.connect(reuse_if_open=True)
            habit = Habit.get_by_id(habit_id)
            name = habit.name
            
            for key, value in kwargs.items():
                if hasattr(habit, key):
                    setattr(habit, key, value)
            
            habit.save()
            db.close()
            activity_logger.log('Habits', 'Updated', name)
            return habit
        except DoesNotExist:
            raise RecordNotFoundError("Habit not found or has been deleted")
        except Exception as e:
            raise DatabaseError(f"Failed to update habit: {str(e)}")
    
    def delete_habit(self, habit_id):
        """Delete a habit and all its logs"""
        try:
            db.connect(reuse_if_open=True)
            habit = Habit.get_by_id(habit_id)
            name = habit.name
            
            HabitLog.delete().where(HabitLog.habit == habit).execute()
            
            habit.delete_instance()
            db.close()
            activity_logger.log('Habits', 'Deleted', name)
            return True
        except DoesNotExist:
            raise RecordNotFoundError("Habit not found or has been deleted")
        except Exception as e:
            raise DatabaseError(f"Failed to delete habit: {str(e)}")
    
    def log_habit(self, habit_id, log_date=None, notes=None):
        """Log habit completion for a date"""
        try:
            if log_date is None:
                log_date = date.today()
            
            db.connect(reuse_if_open=True)
            habit = Habit.get_by_id(habit_id)
            
            existing = HabitLog.select().where(
                (HabitLog.habit == habit) & (HabitLog.date == log_date)
            ).first()
            
            if existing:
                existing.completed = not existing.completed
                if notes:
                    existing.notes = notes
                existing.save()
                log = existing
                status = "Logged" if existing.completed else "Unlogged"
            else:
                log = HabitLog.create(
                    habit=habit,
                    date=log_date,
                    completed=True,
                    notes=notes
                )
                status = "Logged"
            
            db.close()
            activity_logger.log('Habits', status, habit.name)
            return log
        except DoesNotExist:
            raise RecordNotFoundError("Habit not found or has been deleted")
        except Exception as e:
            raise DatabaseError(f"Failed to log habit: {str(e)}")
    
    def get_habit_logs(self, habit_id, days=30):
        """Get habit logs for the last N days"""
        try:
            db.connect(reuse_if_open=True)
            habit = Habit.get_by_id(habit_id)
            
            start_date = date.today() - timedelta(days=days)
            logs = list(HabitLog.select().where(
                (HabitLog.habit == habit) & (HabitLog.date >= start_date)
            ).order_by(HabitLog.date.desc()))
            
            db.close()
            return logs
        except Exception as e:
            print(f"Error getting habit logs: {e}")
            return []
    
    def is_completed_today(self, habit_id):
        """Check if habit is completed today"""
        try:
            db.connect(reuse_if_open=True)
            habit = Habit.get_by_id(habit_id)
            
            log = HabitLog.select().where(
                (HabitLog.habit == habit) & 
                (HabitLog.date == date.today()) &
                (HabitLog.completed == True)
            ).first()
            
            db.close()
            return log is not None
        except Exception as e:
            print(f"Error checking completion: {e}")
            return False
    
    def get_current_streak(self, habit_id):
        """Calculate current streak for a habit"""
        try:
            db.connect(reuse_if_open=True)
            habit = Habit.get_by_id(habit_id)
            is_bad_habit = habit.habit_type == "Bad"
            
            today = date.today()
            streak = 0
            check_date = today
            max_days = min(365, habit.target_days * 2)
            days_checked = 0
            
            while days_checked < max_days:
                # Don't check before habit start date
                if check_date < habit.start_date:
                    break
                
                log = HabitLog.select().where(
                    (HabitLog.habit == habit) & (HabitLog.date == check_date)
                ).first()
                
                # For good habits: streak continues if completed
                # For bad habits: streak continues if NOT completed (avoided)
                if is_bad_habit:
                    if not log or not log.completed:
                        streak += 1
                        check_date -= timedelta(days=1)
                        days_checked += 1
                    else:
                        break  # Did the bad habit, streak broken
                else:
                    if log and log.completed:
                        streak += 1
                        check_date -= timedelta(days=1)
                        days_checked += 1
                    else:
                        break  # Didn't do the good habit, streak broken
            
            db.close()
            return streak
        except Exception as e:
            print(f"Error calculating streak: {e}")
            return 0
    
    def get_completion_rate(self, habit_id):
        """Calculate completion rate based on habit's target period"""
        try:
            db.connect(reuse_if_open=True)
            habit = Habit.get_by_id(habit_id)
            is_bad_habit = habit.habit_type == "Bad"
            
            # Calculate days since start
            days_elapsed = (date.today() - habit.start_date).days + 1
            days_to_check = min(days_elapsed, habit.target_days)
            
            if days_to_check <= 0:
                db.close()
                return 0.0
            
            if is_bad_habit:
                # For bad habits: count days where NOT done
                days_with_log = HabitLog.select().where(
                    (HabitLog.habit == habit) & 
                    (HabitLog.date >= habit.start_date) &
                    (HabitLog.date < habit.start_date + timedelta(days=habit.target_days)) &
                    (HabitLog.completed == True)
                ).count()
                completed_count = days_to_check - days_with_log
            else:
                # For good habits: count days where done
                completed_count = HabitLog.select().where(
                    (HabitLog.habit == habit) & 
                    (HabitLog.date >= habit.start_date) &
                    (HabitLog.date < habit.start_date + timedelta(days=habit.target_days)) &
                    (HabitLog.completed == True)
                ).count()
            
            db.close()
            
            rate = (completed_count / days_to_check) * 100
            return round(rate, 1)
        except Exception as e:
            print(f"Error calculating completion rate: {e}")
            return 0.0
    
    def get_days_remaining(self, habit_id):
        """Get days remaining in habit target period"""
        try:
            db.connect(reuse_if_open=True)
            habit = Habit.get_by_id(habit_id)
            db.close()
            
            end_date = habit.start_date + timedelta(days=habit.target_days)
            days_left = (end_date - date.today()).days
            
            return max(0, days_left)
        except Exception as e:
            print(f"Error calculating days remaining: {e}")
            return 0
    
    def get_days_completed(self, habit_id):
        """Get number of days completed in target period"""
        try:
            db.connect(reuse_if_open=True)
            habit = Habit.get_by_id(habit_id)
            is_bad_habit = habit.habit_type == "Bad"
            
            # Calculate days in target period
            start = habit.start_date
            end = habit.start_date + timedelta(days=habit.target_days)
            today = date.today()
            
            # Only count up to today
            actual_end = min(end, today)
            
            if is_bad_habit:
                # For bad habits: count days where NOT done (no log or not completed)
                total_days = (actual_end - start).days + 1
                days_with_log = HabitLog.select().where(
                    (HabitLog.habit == habit) & 
                    (HabitLog.date >= start) &
                    (HabitLog.date <= actual_end) &
                    (HabitLog.completed == True)
                ).count()
                completed_count = total_days - days_with_log
            else:
                # For good habits: count days where done
                completed_count = HabitLog.select().where(
                    (HabitLog.habit == habit) & 
                    (HabitLog.date >= start) &
                    (HabitLog.date <= actual_end) &
                    (HabitLog.completed == True)
                ).count()
            
            db.close()
            return completed_count
        except Exception as e:
            print(f"Error getting completed days: {e}")
            return 0
    
    def is_habit_completed(self, habit_id):
        """Check if habit target period is completed"""
        try:
            db.connect(reuse_if_open=True)
            habit = Habit.get_by_id(habit_id)
            db.close()
            
            end_date = habit.start_date + timedelta(days=habit.target_days)
            return date.today() >= end_date
        except Exception as e:
            print(f"Error checking habit completion: {e}")
            return False
    
    def calculate_daily_score(self):
        """Calculate today's habit score (0-100)"""
        try:
            db.connect(reuse_if_open=True)
            habits = list(Habit.select())
            
            if not habits:
                db.close()
                return 100
            
            good_habits = [h for h in habits if h.habit_type == "Good"]
            bad_habits = [h for h in habits if h.habit_type == "Bad"]
            
            good_score = 0
            bad_score = 0
            
            today = date.today()
            
            # Calculate good habits score (completed = positive)
            if good_habits:
                completed_good = 0
                for habit in good_habits:
                    log = HabitLog.select().where(
                        (HabitLog.habit == habit) & 
                        (HabitLog.date == today) &
                        (HabitLog.completed == True)
                    ).first()
                    if log:
                        completed_good += 1
                good_score = (completed_good / len(good_habits)) * 50
            else:
                good_score = 50
            
            # Calculate bad habits score (completed = negative)
            if bad_habits:
                completed_bad = 0
                for habit in bad_habits:
                    log = HabitLog.select().where(
                        (HabitLog.habit == habit) & 
                        (HabitLog.date == today) &
                        (HabitLog.completed == True)
                    ).first()
                    if log:
                        completed_bad += 1
                # Inverse: fewer bad habits = higher score
                bad_score = ((len(bad_habits) - completed_bad) / len(bad_habits)) * 50
            else:
                bad_score = 50
            
            db.close()
            
            total_score = good_score + bad_score
            return round(total_score, 1)
        except Exception as e:
            print(f"Error calculating score: {e}")
            return 0.0
    
    def get_score_breakdown(self):
        """Get detailed score breakdown"""
        try:
            db.connect(reuse_if_open=True)
            habits = list(Habit.select())
            
            today = date.today()
            
            good_completed = 0
            good_total = 0
            bad_completed = 0
            bad_total = 0
            
            for habit in habits:
                log = HabitLog.select().where(
                    (HabitLog.habit == habit) & 
                    (HabitLog.date == today) &
                    (HabitLog.completed == True)
                ).first()
                
                if habit.habit_type == "Good":
                    good_total += 1
                    if log:
                        good_completed += 1
                else:
                    bad_total += 1
                    if log:
                        bad_completed += 1
            
            db.close()
            
            return {
                'good_completed': good_completed,
                'good_total': good_total,
                'bad_completed': bad_completed,
                'bad_total': bad_total
            }
        except Exception as e:
            print(f"Error getting score breakdown: {e}")
            return {
                'good_completed': 0,
                'good_total': 0,
                'bad_completed': 0,
                'bad_total': 0
            }
