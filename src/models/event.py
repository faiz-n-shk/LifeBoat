"""
Event Model
"""
from peewee import CharField, TextField, DateTimeField, BooleanField, IntegerField
from datetime import datetime

from src.core.database import BaseModel


class Event(BaseModel):
    """Calendar events model"""
    title = CharField()
    description = TextField(null=True)
    start_date = DateTimeField()
    end_date = DateTimeField(null=True)
    all_day = BooleanField(default=False)
    location = CharField(null=True)
    reminder_minutes = IntegerField(null=True)
    color = CharField(default="#0078d4")
    created_at = DateTimeField(default=datetime.now)
    updated_at = DateTimeField(default=datetime.now)
