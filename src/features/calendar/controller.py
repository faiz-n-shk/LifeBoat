"""
Calendar Controller
Handles calendar business logic
"""
from datetime import datetime, timedelta
from typing import List, Optional
from peewee import DoesNotExist

from src.models.event import Event
from src.core.database import db
from src.core.activity_logger import activity_logger
from src.core.exceptions import RecordNotFoundError, DatabaseError


class CalendarController:
    """Controller for calendar operations"""
    
    def get_events_for_month(self, year: int, month: int) -> List[Event]:
        """Get all events for a specific month"""
        try:
            db.connect(reuse_if_open=True)
            
            month_start = datetime(year, month, 1)
            
            if month == 12:
                month_end = datetime(year + 1, 1, 1)
            else:
                month_end = datetime(year, month + 1, 1)
            
            events = list(Event.select().where(
                (Event.start_date >= month_start) &
                (Event.start_date < month_end)
            ).order_by(Event.start_date))
            
            db.close()
            return events
        except Exception as e:
            raise DatabaseError(f"Failed to get events for month: {str(e)}")
    
    def get_upcoming_events(self, limit: int = 20) -> List[Event]:
        """Get upcoming events"""
        try:
            db.connect(reuse_if_open=True)
            
            now = datetime.now()
            events = list(Event.select().where(
                Event.start_date >= now
            ).order_by(Event.start_date).limit(limit))
            
            db.close()
            return events
        except Exception as e:
            raise DatabaseError(f"Failed to get upcoming events: {str(e)}")
    
    def get_recent_events(self, limit: int = 20) -> List[Event]:
        """Get recent past events"""
        try:
            db.connect(reuse_if_open=True)
            
            now = datetime.now()
            events = list(Event.select().where(
                Event.start_date < now
            ).order_by(Event.start_date.desc()).limit(limit))
            
            db.close()
            return events
        except Exception as e:
            raise DatabaseError(f"Failed to get recent events: {str(e)}")
    
    def create_event(self, event_data: dict) -> Optional[Event]:
        """Create a new event"""
        try:
            db.connect(reuse_if_open=True)
            
            event = Event.create(
                title=event_data['title'],
                description=event_data.get('description'),
                start_date=event_data['start_date'],
                end_date=event_data.get('end_date'),
                all_day=event_data.get('all_day', False),
                location=event_data.get('location'),
                reminder_minutes=event_data.get('reminder_minutes'),
                color=event_data.get('color', '#0078d4')
            )
            
            # Log with formatted message
            from src.core.activity_formatter import format_event_log
            action, details = format_event_log('created', event_data['title'], event.start_date)
            activity_logger.log("Calendar", action, details)
            
            db.close()
            return event
        except Exception as e:
            raise DatabaseError(f"Failed to create event: {str(e)}")
    
    def update_event(self, event_id: int, event_data: dict) -> bool:
        """Update an existing event"""
        try:
            db.connect(reuse_if_open=True)
            
            event = Event.get_by_id(event_id)
            event.title = event_data['title']
            event.description = event_data.get('description')
            event.start_date = event_data['start_date']
            event.end_date = event_data.get('end_date')
            event.all_day = event_data.get('all_day', False)
            event.location = event_data.get('location')
            event.reminder_minutes = event_data.get('reminder_minutes')
            event.color = event_data.get('color', '#0078d4')
            event.updated_at = datetime.now()
            event.save()
            
            # Log with formatted message
            from src.core.activity_formatter import format_event_log
            action, details = format_event_log('updated', event_data['title'], event.start_date)
            activity_logger.log("Calendar", action, details)
            
            db.close()
            return True
        except DoesNotExist:
            raise RecordNotFoundError("Event not found or has been deleted")
        except Exception as e:
            raise DatabaseError(f"Failed to update event: {str(e)}")
    
    def delete_event(self, event_id: int) -> bool:
        """Delete an event"""
        try:
            db.connect(reuse_if_open=True)
            
            event = Event.get_by_id(event_id)
            title = event.title
            event.delete_instance()
            
            # Log with formatted message
            from src.core.activity_formatter import format_event_log
            action, details = format_event_log('deleted', title)
            activity_logger.log("Calendar", action, details)
            
            db.close()
            return True
        except DoesNotExist:
            raise RecordNotFoundError("Event not found or has been deleted")
        except Exception as e:
            raise DatabaseError(f"Failed to delete event: {str(e)}")
