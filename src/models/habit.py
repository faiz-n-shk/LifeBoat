"""
Habit Models
"""
from peewee import CharField, TextField, IntegerField, DateField, BooleanField, DateTimeField, ForeignKeyField
from datetime import datetime

from src.core.database import BaseModel


class Habit(BaseModel):
    """Habit tracking model"""
    name = CharField()
    description = TextField(null=True)
    frequency = CharField(default="Daily")
    target_count = IntegerField(default=1)
    color = CharField(default="#0078d4")
    created_at = DateTimeField(default=datetime.now)


class HabitLog(BaseModel):
    """Habit completion log"""
    habit = ForeignKeyField(Habit, backref='logs')
    date = DateField()
    completed = BooleanField(default=True)
    notes = TextField(null=True)
    created_at = DateTimeField(default=datetime.now)
