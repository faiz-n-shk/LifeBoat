"""
Expense and Income Models
"""
from peewee import CharField, TextField, DecimalField, DateField, TimeField, BooleanField, DateTimeField
from datetime import datetime

from src.core.database import BaseModel


class Expense(BaseModel):
    """Expense tracking model"""
    amount = DecimalField(decimal_places=2)
    category = CharField()
    description = TextField(null=True)
    date = DateField()
    time = TimeField(null=True)
    payment_method = CharField(null=True)
    is_recurring = BooleanField(default=False)
    created_at = DateTimeField(default=datetime.now)


class Income(BaseModel):
    """Income tracking model"""
    amount = DecimalField(decimal_places=2)
    category = CharField()
    description = TextField(null=True)
    date = DateField()
    time = TimeField(null=True)
    source = CharField(null=True)
    is_recurring = BooleanField(default=False)
    created_at = DateTimeField(default=datetime.now)
