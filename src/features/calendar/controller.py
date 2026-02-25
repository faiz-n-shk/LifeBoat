"""
Calendar Controller
Handles calendar business logic
"""
from datetime import datetime, timedelta
from typing import List, Optional

from src.models.event import Event
from src.core.database import db


class CalendarController:
    """Controller for calendar operations"""
    
    def get_events_for_month(self, year: int, month: int) -> List[Event]:
        """Get all events for a specific month"""
        try:
            db.connect(reuse_if_open=True)
            
            # First day of month
            month_start = datetime(year, month, 1)
            
            # First day of next month
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
            print(f"Error getting events for month: {e}")
            return []
    
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
            print(f"Error getting upcoming events: {e}")
            return []
    
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
            print(f"Error getting recent events: {e}")
            return []
    
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
            
            db.close()
            return event
        except Exception as e:
            print(f"Error creating event: {e}")
            return None
    
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
            
            db.close()
            return True
        except Exception as e:
            print(f"Error updating event: {e}")
            return False
    
    def delete_event(self, event_id: int) -> bool:
        """Delete an event"""
        try:
            db.connect(reuse_if_open=True)
            
            event = Event.get_by_id(event_id)
            event.delete_instance()
            
            db.close()
            return True
        except Exception as e:
            print(f"Error deleting event: {e}")
            return False
