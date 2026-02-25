"""
Note Model
"""
from peewee import CharField, TextField, BooleanField, DateTimeField
from datetime import datetime

from src.core.database import BaseModel


class Note(BaseModel):
    """Notes model"""
    title = CharField()
    content = TextField()
    tags = CharField(null=True)
    pinned = BooleanField(default=False)
    created_at = DateTimeField(default=datetime.now)
    updated_at = DateTimeField(default=datetime.now)
