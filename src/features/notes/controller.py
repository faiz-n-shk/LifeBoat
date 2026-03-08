"""
Notes Controller
Handles notes business logic
"""
from datetime import datetime
from typing import List, Optional
from peewee import DoesNotExist

from src.models.note import Note
from src.core.activity_logger import activity_logger
from src.core.exceptions import RecordNotFoundError, DatabaseError


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
            raise DatabaseError(f"Failed to retrieve notes: {str(e)}")
    
    @staticmethod
    def get_note_by_id(note_id: int) -> Optional[Note]:
        """Get a specific note by ID"""
        try:
            return Note.get_by_id(note_id)
        except DoesNotExist:
            raise RecordNotFoundError("Note not found or has been deleted")
        except Exception as e:
            raise DatabaseError(f"Failed to get note: {str(e)}")
    
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
            
            # Log with formatted message
            from src.core.activity_formatter import format_note_log
            action, details = format_note_log('created', title, tags)
            activity_logger.log("Notes", action, details)
            
            return note
        except Exception as e:
            raise DatabaseError(f"Failed to create note: {str(e)}")
    
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
            
            # Log with formatted message
            from src.core.activity_formatter import format_note_log
            action, details = format_note_log('updated', title, tags)
            activity_logger.log("Notes", action, details)
            
            return True
        except DoesNotExist:
            raise RecordNotFoundError("Note not found or has been deleted")
        except Exception as e:
            raise DatabaseError(f"Failed to update note: {str(e)}")
    
    @staticmethod
    def delete_note(note_id: int) -> bool:
        """Delete a note"""
        try:
            note = Note.get_by_id(note_id)
            title = note.title
            note.delete_instance()
            
            # Log with formatted message
            from src.core.activity_formatter import format_note_log
            action, details = format_note_log('deleted', title)
            activity_logger.log("Notes", action, details)
            
            return True
        except DoesNotExist:
            raise RecordNotFoundError("Note not found or has been deleted")
        except Exception as e:
            raise DatabaseError(f"Failed to delete note: {str(e)}")
    
    @staticmethod
    def toggle_pin(note_id: int) -> bool:
        """Toggle pin status of a note"""
        try:
            note = Note.get_by_id(note_id)
            note.pinned = not note.pinned
            note.updated_at = datetime.now()
            note.save()
            action_type = "pinned" if note.pinned else "unpinned"
            
            # Log with formatted message
            from src.core.activity_formatter import format_note_log
            action, details = format_note_log(action_type, note.title)
            activity_logger.log("Notes", action, details)
            
            return True
        except DoesNotExist:
            raise RecordNotFoundError("Note not found or has been deleted")
        except Exception as e:
            raise DatabaseError(f"Failed to toggle pin: {str(e)}")
    
    @staticmethod
    def get_all_tags() -> List[str]:
        """Get all unique tags from notes"""
        try:
            notes = Note.select()
            tags_set = set()
            
            for note in notes:
                if note.tags:
                    note_tags = [tag.strip() for tag in note.tags.split(',') if tag.strip()]
                    tags_set.update(note_tags)
            
            return sorted(list(tags_set))
        except Exception as e:
            raise DatabaseError(f"Failed to get tags: {str(e)}")
