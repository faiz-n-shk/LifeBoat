"""
Theme Model
"""
from peewee import CharField, BooleanField, DateTimeField
from datetime import datetime

from src.core.database import BaseModel


class Theme(BaseModel):
    """Theme storage model"""
    name = CharField(unique=True)
    bg_primary = CharField()
    bg_secondary = CharField()
    bg_tertiary = CharField()
    fg_primary = CharField()
    fg_secondary = CharField()
    accent = CharField()
    accent_hover = CharField()
    success = CharField()
    warning = CharField()
    danger = CharField()
    border = CharField()
    is_active = BooleanField(default=False)
    is_custom = BooleanField(default=False)
    created_at = DateTimeField(default=datetime.now)
