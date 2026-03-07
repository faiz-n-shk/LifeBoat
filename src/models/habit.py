"""
Habit Models
"""
from peewee import CharField, TextField, IntegerField, DateField, BooleanField, DateTimeField, ForeignKeyField
from datetime import datetime

from src.core.database import BaseModel


class Habit(BaseModel):
    """Habit tracking model - Goal-based habits"""
    name = CharField()
    description = TextField(null=True)
    habit_type = CharField(default="Good")  # "Good" or "Bad"
    target_days = IntegerField(default=7)  # Target duration in days
    start_date = DateField(default=datetime.now().date)  # When habit tracking started
    frequency = CharField(default="Daily")  # Keep for backward compatibility
    target_count = IntegerField(default=1)  # Keep for backward compatibility
    color = CharField(default="#0078d4")
    created_at = DateTimeField(default=datetime.now)
    
    # New frequency fields
    frequency_count = IntegerField(default=1)  # n number of times for frequency of the habit, for n number of period
    frequency_period = CharField(default="day")  # Period: "day", "week", "month", "year"


class HabitLog(BaseModel):
    """Habit completion log"""
    habit = ForeignKeyField(Habit, backref='logs')
    date = DateField()
    completed = BooleanField(default=True)
    notes = TextField(null=True)
    created_at = DateTimeField(default=datetime.now)
    count = IntegerField(default=1)  # Number of times completed on this date
