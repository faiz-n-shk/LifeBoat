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
    
    def create_habit(self, name, description=None, habit_type="Good", target_days=7, color="#0078d4", frequency_count=1, frequency_period="day"):
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
                color=color,
                frequency_count=frequency_count,
                frequency_period=frequency_period
            )
            db.close()
            
            # Log with formatted message
            from src.core.activity_formatter import format_habit_log
            action, details = format_habit_log('created', name, habit_type)
            activity_logger.log('Habits', action, details)
            
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
            
            # Log with formatted message
            from src.core.activity_formatter import format_habit_log
            action, details = format_habit_log('updated', name)
            activity_logger.log('Habits', action, details)
            
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
            
            # Log with formatted message
            from src.core.activity_formatter import format_habit_log
            action, details = format_habit_log('deleted', name)
            activity_logger.log('Habits', action, details)
            
            return True
        except DoesNotExist:
            raise RecordNotFoundError("Habit not found or has been deleted")
        except Exception as e:
            raise DatabaseError(f"Failed to delete habit: {str(e)}")
    
    def increment_habit(self, habit_id, log_date=None):
        """Increment habit count"""
        try:
            if log_date is None:
                log_date = date.today()
            
            db.connect(reuse_if_open=True)
            habit = Habit.get_by_id(habit_id)
            
            existing = HabitLog.select().where(
                (HabitLog.habit == habit) & (HabitLog.date == log_date)
            ).first()
            
            if existing:
                existing.count += 1
                existing.completed = True
                existing.save()
            else:
                HabitLog.create(
                    habit=habit,
                    date=log_date,
                    completed=True,
                    count=1
                )
            
            db.close()
            
            # Log with formatted message
            from src.core.activity_formatter import format_habit_log
            action, details = format_habit_log('incremented', habit.name)
            activity_logger.log('Habits', action, details)
        except Exception as e:
            raise DatabaseError(f"Failed to increment habit: {str(e)}")
    
    def decrement_habit(self, habit_id, log_date=None):
        """Decrement habit count"""
        try:
            if log_date is None:
                log_date = date.today()
            
            db.connect(reuse_if_open=True)
            habit = Habit.get_by_id(habit_id)
            
            existing = HabitLog.select().where(
                (HabitLog.habit == habit) & (HabitLog.date == log_date)
            ).first()
            
            # Only decrement if count is more than zero, and log exists
            if existing and existing.count > 0:
                existing.count -= 1
                if existing.count == 0:
                    existing.completed = False
                existing.save()
                db.close()
                
                # Log with formatted message
                from src.core.activity_formatter import format_habit_log
                action, details = format_habit_log('decremented', habit.name)
                activity_logger.log('Habits', action, details)
            else:
                db.close()
                # Don't log if nothing was decremented
        except Exception as e:
            raise DatabaseError(f"Failed to decrement habit: {str(e)}")
    
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
        """Check if habit frequency goal is met today"""
        try:
            db.connect(reuse_if_open=True)
            habit = Habit.get_by_id(habit_id)
            
            freq_count = getattr(habit, 'frequency_count', 1)
            freq_period = getattr(habit, 'frequency_period', 'day')
            
            if freq_period == 'day':
                log = HabitLog.select().where(
                    (HabitLog.habit == habit) & 
                    (HabitLog.date == date.today())
                ).first()
                
                db.close()
                if not log:
                    return False
                
                count = getattr(log, 'count', 1) if log.completed else 0
                return count >= freq_count
            else:
                today = date.today()
                
                if freq_period == 'week':
                    start_date = today - timedelta(days=today.weekday())
                elif freq_period == 'month':
                    start_date = today.replace(day=1)
                elif freq_period == 'year':
                    start_date = today.replace(month=1, day=1)
                else:
                    start_date = today
                
                logs = HabitLog.select().where(
                    (HabitLog.habit == habit) & 
                    (HabitLog.date >= start_date) &
                    (HabitLog.date <= today) &
                    (HabitLog.completed == True)
                )
                
                total_count = sum(getattr(log, 'count', 1) for log in logs)
                db.close()
                return total_count >= freq_count
                
        except Exception as e:
            print(f"Error checking completion: {e}")
            return False
    
    def get_today_count(self, habit_id):
        """Get the count of completions for today or current period"""
        try:
            db.connect(reuse_if_open=True)
            habit = Habit.get_by_id(habit_id)
            
            freq_period = getattr(habit, 'frequency_period', 'day')
            today = date.today()
            
            if freq_period == 'day':
                log = HabitLog.select().where(
                    (HabitLog.habit == habit) & 
                    (HabitLog.date == today)
                ).first()
                
                db.close()
                if not log or not log.completed:
                    return 0
                return getattr(log, 'count', 1)
            else:
                if freq_period == 'week':
                    start_date = today - timedelta(days=today.weekday())
                elif freq_period == 'month':
                    start_date = today.replace(day=1)
                elif freq_period == 'year':
                    start_date = today.replace(month=1, day=1)
                else:
                    start_date = today
                
                logs = HabitLog.select().where(
                    (HabitLog.habit == habit) & 
                    (HabitLog.date >= start_date) &
                    (HabitLog.date <= today) &
                    (HabitLog.completed == True)
                )
                
                total_count = sum(getattr(log, 'count', 1) for log in logs)
                db.close()
                return total_count
                
        except Exception as e:
            print(f"Error getting today count: {e}")
            return 0
    
    def get_current_streak(self, habit_id):
        """Calculate current streak for a habit - only counts periods where goal was fully met"""
        try:
            db.connect(reuse_if_open=True)
            habit = Habit.get_by_id(habit_id)
            is_bad_habit = habit.habit_type == "Bad"
            freq_count = getattr(habit, 'frequency_count', 1)
            freq_period = getattr(habit, 'frequency_period', 'day')
            
            today = date.today()
            streak = 0
            
            if freq_period == 'day':
                # Daily habits: check each day
                check_date = today
                max_days = min(365, habit.target_days * 2)
                days_checked = 0
                
                while days_checked < max_days:
                    if check_date < habit.start_date:
                        break
                    
                    log = HabitLog.select().where(
                        (HabitLog.habit == habit) & (HabitLog.date == check_date)
                    ).first()
                    
                    if is_bad_habit:
                        # Bad habit: streak continues if count is BELOW goal (did it less than X times)
                        if log:
                            count = getattr(log, 'count', 1) if log.completed else 0
                        else:
                            count = 0
                        
                        goal_met = count < freq_count
                        
                        if goal_met:
                            streak += 1
                            check_date -= timedelta(days=1)
                            days_checked += 1
                        else:
                            break
                    else:
                        # Good habit: check if goal was fully met
                        if log:
                            count = getattr(log, 'count', 1) if log.completed else 0
                            goal_met = count >= freq_count
                        else:
                            goal_met = False
                        
                        if goal_met:
                            streak += 1
                            check_date -= timedelta(days=1)
                            days_checked += 1
                        else:
                            break
            else:
                # Weekly/Monthly/Yearly habits: check each period
                check_date = today
                max_periods = 52 if freq_period == 'week' else (12 if freq_period == 'month' else 5)
                
                for _ in range(max_periods):
                    if check_date < habit.start_date:
                        break
                    
                    # Calculate period start
                    if freq_period == 'week':
                        period_start = check_date - timedelta(days=check_date.weekday())
                        period_end = period_start + timedelta(days=6)
                    elif freq_period == 'month':
                        period_start = check_date.replace(day=1)
                        next_month = period_start + timedelta(days=32)
                        period_end = next_month.replace(day=1) - timedelta(days=1)
                    elif freq_period == 'year':
                        period_start = check_date.replace(month=1, day=1)
                        period_end = check_date.replace(month=12, day=31)
                    else:
                        break
                    
                    # Count completions in this period
                    logs = HabitLog.select().where(
                        (HabitLog.habit == habit) & 
                        (HabitLog.date >= period_start) &
                        (HabitLog.date <= period_end) &
                        (HabitLog.completed == True)
                    )
                    
                    total_count = sum(getattr(log, 'count', 1) for log in logs)
                    
                    if is_bad_habit:
                        # Bad habit: streak continues if count is BELOW goal (didn't do it too much, aukaat mai)
                        goal_met = total_count < freq_count
                    else:
                        # Good habit: streak continues if count meets or exceeds goal
                        goal_met = total_count >= freq_count
                    
                    if goal_met:
                        streak += 1
                        # Move to previous period
                        if freq_period == 'week':
                            check_date = period_start - timedelta(days=1)
                        elif freq_period == 'month':
                            check_date = period_start - timedelta(days=1)
                        elif freq_period == 'year':
                            check_date = period_start - timedelta(days=1)
                    else:
                        break
            
            db.close()
            return streak
        except Exception as e:
            print(f"Error calculating streak: {e}")
            return 0
    
    def calculate_daily_score(self):
        """Calculate today's habit score (0-100) based on frequency goals weighted by frequency count"""
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
            
            if good_habits:
                # Calculate weighted score for good habits
                total_good_weight = sum(getattr(h, 'frequency_count', 1) for h in good_habits)
                achieved_good_weight = 0
                
                for habit in good_habits:
                    freq_count = getattr(habit, 'frequency_count', 1)
                    current_count = self.get_today_count(habit.id)
                    
                    # Calculate completion ratio (capped at 100%)
                    completion_ratio = min(current_count / freq_count, 1.0)
                    achieved_good_weight += completion_ratio * freq_count
                
                good_score = (achieved_good_weight / total_good_weight) * 50
            else:
                good_score = 50
            
            if bad_habits:
                # Calculate weighted score for bad habits (inverse - lower count is better)
                total_bad_weight = sum(getattr(h, 'frequency_count', 1) for h in bad_habits)
                achieved_bad_weight = 0
                
                for habit in bad_habits:
                    freq_count = getattr(habit, 'frequency_count', 1)
                    current_count = self.get_today_count(habit.id)
                    
                    # For bad habits, staying below the threshold is good
                    # If count < freq_count, full points; if count >= freq_count, no points
                    if current_count < freq_count:
                        achieved_bad_weight += freq_count
                    # Partial credit if they're at or above threshold (0 points)
                
                bad_score = (achieved_bad_weight / total_bad_weight) * 50
            else:
                bad_score = 50
            
            db.close()
            
            total_score = good_score + bad_score
            return round(total_score, 1)
        except Exception as e:
            print(f"Error calculating score: {e}")
            return 0.0
    
    def get_score_breakdown(self):
        """Get detailed score breakdown based on frequency goals"""
        try:
            db.connect(reuse_if_open=True)
            habits = list(Habit.select())
            
            good_completed = 0
            good_total = 0
            bad_completed = 0
            bad_total = 0
            
            for habit in habits:
                if habit.habit_type == "Good":
                    good_total += 1
                    if self.is_completed_today(habit.id):
                        good_completed += 1
                else:
                    bad_total += 1
                    if self.is_completed_today(habit.id):
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
