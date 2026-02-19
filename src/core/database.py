"""
Lifeboat - Database Module
Handles all database operations using Peewee ORM
"""
from peewee import *
from datetime import datetime
from src.core.config import DATABASE_PATH, DEFAULT_THEMES, DATE_FORMAT

# Initialize database
db = SqliteDatabase(DATABASE_PATH)

class BaseModel(Model):
    """Base model class for all database models"""
    class Meta:
        database = db

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

class Expense(BaseModel):
    """Expense tracking model"""
    amount = DecimalField(decimal_places=2)
    category = CharField()
    description = TextField(null=True)
    date = DateField()
    payment_method = CharField(null=True)
    is_recurring = BooleanField(default=False)
    created_at = DateTimeField(default=datetime.now)

class Income(BaseModel):
    """Income tracking model"""
    amount = DecimalField(decimal_places=2)
    category = CharField()
    description = TextField(null=True)
    date = DateField()
    source = CharField(null=True)
    is_recurring = BooleanField(default=False)
    created_at = DateTimeField(default=datetime.now)

class Note(BaseModel):
    """Notes model"""
    title = CharField()
    content = TextField()
    tags = CharField(null=True)
    pinned = BooleanField(default=False)
    created_at = DateTimeField(default=datetime.now)
    updated_at = DateTimeField(default=datetime.now)

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

class Settings(BaseModel):
    """App settings model"""
    key = CharField(unique=True)
    value = TextField()
    updated_at = DateTimeField(default=datetime.now)

def initialize_database():
    """Initialize database and create tables"""
    import os
    db_exists = os.path.exists(DATABASE_PATH)
    
    db.connect()
    db.execute_sql('PRAGMA journal_mode=WAL')
    db.execute_sql('PRAGMA synchronous=NORMAL')
    db.execute_sql('PRAGMA cache_size=10000')
    db.execute_sql('PRAGMA temp_store=MEMORY')
    
    if not db_exists:
        db.create_tables([
            Theme, Event, Task, Expense, Income, 
            Note, Goal, Habit, HabitLog, Settings
        ])
        
        with db.atomic():
            for theme_name, theme_colors in DEFAULT_THEMES.items():
                Theme.create(
                    name=theme_name,
                    is_active=theme_name == "Dark",
                    is_custom=False,
                    **theme_colors
                )
            
            default_settings = {
                'first_run': 'true',
                'currency_symbol': '$',
                'date_format': DATE_FORMAT,
                'week_start': 'Monday'
            }
            
            for key, value in default_settings.items():
                Settings.create(key=key, value=value)
    else:
        db.create_tables([
            Theme, Event, Task, Expense, Income, 
            Note, Goal, Habit, HabitLog, Settings
        ], safe=True)
    
    db.close()

def get_active_theme():
    """Get the currently active theme"""
    try:
        return Theme.get(Theme.is_active == True)
    except:
        try:
            theme = Theme.get(Theme.name == "Dark")
            theme.is_active = True
            theme.save()
            return theme
        except:
            return None

def set_active_theme(theme_name):
    """Set a theme as active"""
    Theme.update(is_active=False).execute()
    theme = Theme.get(Theme.name == theme_name)
    theme.is_active = True
    theme.save()
    return theme
