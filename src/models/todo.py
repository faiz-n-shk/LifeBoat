"""
Todo Model
Database model for todos
"""
from peewee import CharField, TextField, BooleanField, DateField, DateTimeField, IntegerField
from datetime import datetime, date
from src.core.database import BaseModel


class Todo(BaseModel):
    """Todo item model"""
    title = CharField()
    description = TextField(null=True)
    completed = BooleanField(default=False)
    priority = CharField(default="Medium")
    due_date = DateField(null=True)
    category = CharField(null=True)
    tags = CharField(null=True)
    order = IntegerField(default=0)
    created_at = DateTimeField(default=datetime.now)
    updated_at = DateTimeField(default=datetime.now)
    completed_at = DateTimeField(null=True)
    
    class Meta:
        table_name = 'todos'
    
    def toggle_complete(self):
        """Toggle completion status"""
        self.completed = not self.completed
        self.completed_at = datetime.now() if self.completed else None
        self.updated_at = datetime.now()
        self.save()
    
    def get_tags_list(self):
        """Get tags as list"""
        if not self.tags:
            return []
        return [tag.strip() for tag in self.tags.split(',') if tag.strip()]
    
    def set_tags_list(self, tags_list):
        """Set tags from list"""
        self.tags = ','.join(tags_list) if tags_list else None
