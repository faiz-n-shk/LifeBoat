"""
Lifeboat - Notes Module
Note-taking and management
"""
import customtkinter as ctk
from src.ui.widgets import ThemedFrame, ThemedLabel, ThemedButton, ThemedEntry, ThemedTextbox, SearchBar
from src.core.theme_manager import theme_manager
from src.core.database import Note, db
from datetime import datetime
from src.core import config
from src.utils import helpers as utils

class NotesModule(ThemedFrame):
    """Notes management module"""
    
    def __init__(self, master, **kwargs):
        super().__init__(master, color_key="bg_primary", **kwargs)
        
        self.search_query = ""
        self.selected_note = None
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=2)
        self.grid_rowconfigure(1, weight=1)
        
        self.setup_ui()
        self.load_notes()
    
    def setup_ui(self):
        """Setup notes UI"""
        # Header
        header = ThemedFrame(self, color_key="bg_primary")
        header.grid(row=0, column=0, columnspan=2, sticky="ew", padx=20, pady=20)
        header.grid_columnconfigure(1, weight=1)
        
        title = ThemedLabel(
            header,
            text="Notes",
            font=(config.FONT_FAMILY, config.FONT_SIZE_XLARGE, "bold")
        )
        title.grid(row=0, column=0, sticky="w")
        
        self.search_bar = SearchBar(header, callback=self.on_search, width=300)
        self.search_bar.grid(row=0, column=1, sticky="e", padx=(20, 0))
        
        ThemedButton(
            header,
            text="+ New Note",
            button_style="accent",
            command=self.create_new_note
        ).grid(row=0, column=2, sticky="e", padx=(10, 0))
        
        # Notes list (left)
        list_frame = ThemedFrame(self, color_key="bg_primary")
        list_frame.grid(row=1, column=0, sticky="nsew", padx=(20, 10), pady=(0, 20))
        list_frame.grid_columnconfigure(0, weight=1)
        list_frame.grid_rowconfigure(0, weight=1)
        
        self.notes_scroll = ctk.CTkScrollableFrame(
            list_frame,
            fg_color=theme_manager.get_color("bg_primary"),
            width=300
        )
        self.notes_scroll.grid(row=0, column=0, sticky="nsew")
        self.notes_scroll.grid_columnconfigure(0, weight=1)
        
        # Note editor (right)
        self.editor_frame = ThemedFrame(self, color_key="bg_secondary", corner_radius=10)
        self.editor_frame.grid(row=1, column=1, sticky="nsew", padx=(10, 20), pady=(0, 20))
        self.editor_frame.grid_columnconfigure(0, weight=1)
        self.editor_frame.grid_rowconfigure(2, weight=1)
        
        # Editor header
        editor_header = ThemedFrame(self.editor_frame, color_key="bg_secondary")
        editor_header.grid(row=0, column=0, sticky="ew", padx=20, pady=(20, 10))
        
        self.title_entry = ThemedEntry(
            editor_header,
            placeholder_text="Note Title",
            font=(config.FONT_FAMILY, config.FONT_SIZE_LARGE, "bold")
        )
        self.title_entry.pack(fill="x")
        
        # Editor toolbar
        toolbar = ThemedFrame(self.editor_frame, color_key="bg_secondary")
        toolbar.grid(row=1, column=0, sticky="ew", padx=20, pady=(0, 10))
        
        ThemedButton(
            toolbar,
            text="Save",
            button_style="accent",
            width=80,
            command=self.save_note
        ).pack(side="left", padx=(0, 5))
        
        ThemedButton(
            toolbar,
            text="Delete",
            button_style="danger",
            width=80,
            command=self.delete_note
        ).pack(side="left", padx=5)
        
        self.pin_btn = ThemedButton(
            toolbar,
            text="📌 Pin",
            width=80,
            command=self.toggle_pin
        )
        self.pin_btn.pack(side="left", padx=5)
        
        # Editor content
        self.content_text = ThemedTextbox(
            self.editor_frame,
            font=(config.FONT_FAMILY, config.FONT_SIZE_NORMAL)
        )
        self.content_text.grid(row=2, column=0, sticky="nsew", padx=20, pady=(0, 20))
        
        # Show placeholder
        self.show_placeholder()
    
    def load_notes(self):
        """Load and display notes"""
        for widget in self.notes_scroll.winfo_children():
            widget.destroy()
        
        query = Note.select()
        
        if self.search_query:
            query = query.where(
                (Note.title.contains(self.search_query)) |
                (Note.content.contains(self.search_query))
            )
        
        notes = list(query.order_by(Note.pinned.desc(), Note.updated_at.desc()))
        
        if not notes:
            no_notes = ThemedLabel(
                self.notes_scroll,
                text="No notes found",
                color_key="fg_secondary"
            )
            no_notes.pack(pady=50)
            return
        
        for note in notes:
            self.create_note_item(note)
    
    def create_note_item(self, note):
        """Create note list item"""
        item = ThemedFrame(
            self.notes_scroll,
            color_key="bg_tertiary" if self.selected_note and self.selected_note.id == note.id else "bg_secondary",
            corner_radius=8
        )
        item.pack(fill="x", pady=5, padx=5)
        item.bind("<Button-1>", lambda e: self.select_note(note))
        
        content = ThemedFrame(item, color_key="transparent")
        content.pack(fill="both", expand=True, padx=15, pady=10)
        content.bind("<Button-1>", lambda e: self.select_note(note))
        
        # Title with pin indicator
        title_text = f"📌 {note.title}" if note.pinned else note.title
        title = ThemedLabel(
            content,
            text=title_text,
            font=(config.FONT_FAMILY, config.FONT_SIZE_NORMAL, "bold"),
            wraplength=250
        )
        title.pack(anchor="w")
        title.bind("<Button-1>", lambda e: self.select_note(note))
        
        # Preview
        preview = ThemedLabel(
            content,
            text=utils.truncate_text(note.content, 80),
            color_key="fg_secondary",
            wraplength=250
        )
        preview.pack(anchor="w", pady=(5, 0))
        preview.bind("<Button-1>", lambda e: self.select_note(note))
        
        # Date
        date = ThemedLabel(
            content,
            text=utils.format_datetime(note.updated_at),
            font=(config.FONT_FAMILY, config.FONT_SIZE_SMALL),
            color_key="fg_secondary"
        )
        date.pack(anchor="w", pady=(5, 0))
        date.bind("<Button-1>", lambda e: self.select_note(note))
    
    def select_note(self, note):
        """Select and display a note"""
        self.selected_note = note
        
        # Update title and content
        self.title_entry.delete(0, "end")
        self.title_entry.insert(0, note.title)
        
        self.content_text.delete("1.0", "end")
        self.content_text.insert("1.0", note.content)
        
        # Update pin button
        if note.pinned:
            self.pin_btn.configure(text="📌 Unpin")
        else:
            self.pin_btn.configure(text="📌 Pin")
        
        # Refresh list to highlight selected
        self.load_notes()
    
    def create_new_note(self):
        """Create a new note"""
        note = Note.create(
            title="Untitled Note",
            content=""
        )
        self.selected_note = note
        self.load_notes()
        self.select_note(note)
        self.title_entry.focus()
    
    def save_note(self):
        """Save current note"""
        if not self.selected_note:
            return
        
        self.selected_note.title = self.title_entry.get() or "Untitled Note"
        self.selected_note.content = self.content_text.get("1.0", "end-1c")
        self.selected_note.updated_at = datetime.now()
        self.selected_note.save()
        
        self.load_notes()
    
    def delete_note(self):
        """Delete current note"""
        if not self.selected_note:
            return
        
        self.selected_note.delete_instance()
        self.selected_note = None
        self.show_placeholder()
        self.load_notes()
    
    def toggle_pin(self):
        """Toggle note pin status"""
        if not self.selected_note:
            return
        
        self.selected_note.pinned = not self.selected_note.pinned
        self.selected_note.save()
        
        if self.selected_note.pinned:
            self.pin_btn.configure(text="📌 Unpin")
        else:
            self.pin_btn.configure(text="📌 Pin")
        
        self.load_notes()
    
    def show_placeholder(self):
        """Show placeholder in editor"""
        self.title_entry.delete(0, "end")
        self.title_entry.configure(placeholder_text="Select or create a note")
        self.content_text.delete("1.0", "end")
        self.pin_btn.configure(text="📌 Pin")
    
    def on_search(self, query):
        """Handle search"""
        self.search_query = query
        self.load_notes()
    
    def refresh(self):
        """Refresh notes"""
        self.load_notes()
