"""
Task Model
"""
from peewee import CharField, TextField, DateTimeField, BooleanField
from datetime import datetime

from src.core.database import BaseModel


class Task(BaseModel):
    """Tasks and todo items model"""
    title = CharField()
    description = TextField(null=True)
    priority = CharField(default="Medium")
    status = CharField(default="Not Started")
    due_date = DateTimeField(null=True)
    completed = BooleanField(default=False)
    completed_at = DateTimeField(null=True)
    tags = CharField(null=True)
    created_at = DateTimeField(default=datetime.now)
    updated_at = DateTimeField(default=datetime.now)
