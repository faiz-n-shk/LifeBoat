"""
Settings Model
"""
from peewee import CharField, TextField, DateTimeField
from datetime import datetime

from src.core.database import BaseModel


class Settings(BaseModel):
    """App settings model"""
    key = CharField(unique=True)
    value = TextField()
    updated_at = DateTimeField(default=datetime.now)
