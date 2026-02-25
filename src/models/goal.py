"""
Goal Model
"""
from peewee import CharField, TextField, DateField, IntegerField, BooleanField, DateTimeField
from datetime import datetime

from src.core.database import BaseModel


class Goal(BaseModel):
    """Goals tracking model"""
    title = CharField()
    description = TextField(null=True)
    target_date = DateField(null=True)
    progress = IntegerField(default=0)
    category = CharField(null=True)
    completed = BooleanField(default=False)
    created_at = DateTimeField(default=datetime.now)
    updated_at = DateTimeField(default=datetime.now)
