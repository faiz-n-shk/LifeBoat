"""
Notes Controller
Handles notes business logic
"""
from datetime import datetime
from typing import List, Optional

from src.models.note import Note
from src.core.activity_logger import activity_logger


class NotesController:
    """Controller for notes operations"""
    
    @staticmethod
    def get_all_notes(search_query: str = "", pinned_only: bool = False) -> List[Note]:
        """Get all notes with optional filtering"""
        try:
            query = Note.select().order_by(Note.pinned.desc(), Note.updated_at.desc())
            
            if pinned_only:
                query = query.where(Note.pinned == True)
            
            if search_query:
                query = query.where(
                    (Note.title.contains(search_query)) |
                    (Note.content.contains(search_query)) |
                    (Note.tags.contains(search_query))
                )
            
            return list(query)
        except Exception as e:
            print(f"Error getting notes: {e}")
            return []
    
    @staticmethod
    def get_note_by_id(note_id: int) -> Optional[Note]:
        """Get a specific note by ID"""
        try:
            return Note.get_by_id(note_id)
        except Exception as e:
            print(f"Error getting note: {e}")
            return None
    
    @staticmethod
    def create_note(title: str, content: str, tags: str = "", pinned: bool = False) -> Optional[Note]:
        """Create a new note"""
        try:
            note = Note.create(
                title=title,
                content=content,
                tags=tags,
                pinned=pinned,
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            activity_logger.log("Notes", "created", f"'{title}'")
            return note
        except Exception as e:
            print(f"Error creating note: {e}")
            return None
    
    @staticmethod
    def update_note(note_id: int, title: str, content: str, tags: str = "", pinned: bool = False) -> bool:
        """Update an existing note"""
        try:
            note = Note.get_by_id(note_id)
            note.title = title
            note.content = content
            note.tags = tags
            note.pinned = pinned
            note.updated_at = datetime.now()
            note.save()
            activity_logger.log("Notes", "updated", f"'{title}'")
            return True
        except Exception as e:
            print(f"Error updating note: {e}")
            return False
    
    @staticmethod
    def delete_note(note_id: int) -> bool:
        """Delete a note"""
        try:
            note = Note.get_by_id(note_id)
            title = note.title
            note.delete_instance()
            activity_logger.log("Notes", "deleted", f"'{title}'")
            return True
        except Exception as e:
            print(f"Error deleting note: {e}")
            return False
    
    @staticmethod
    def toggle_pin(note_id: int) -> bool:
        """Toggle pin status of a note"""
        try:
            note = Note.get_by_id(note_id)
            note.pinned = not note.pinned
            note.updated_at = datetime.now()
            note.save()
            action = "pinned" if note.pinned else "unpinned"
            activity_logger.log("Notes", action, f"'{note.title}'")
            return True
        except Exception as e:
            print(f"Error toggling pin: {e}")
            return False
    
    @staticmethod
    def get_all_tags() -> List[str]:
        """Get all unique tags from notes"""
        try:
            notes = Note.select()
            tags_set = set()
            
            for note in notes:
                if note.tags:
                    # Split tags by comma and strip whitespace
                    note_tags = [tag.strip() for tag in note.tags.split(',') if tag.strip()]
                    tags_set.update(note_tags)
            
            return sorted(list(tags_set))
        except Exception as e:
            print(f"Error getting tags: {e}")
            return []
