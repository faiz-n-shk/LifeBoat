"""
Note Viewer
Read-only viewer for notes with markdown support
"""
from PyQt6.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QTextEdit, QCheckBox, QSizePolicy, QScrollArea, QFrame
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QTextDocument, QTextOption

from src.shared.dialogs import BaseDialog
from src.shared.formatters import format_datetime


class NoteViewer(BaseDialog):
    """Read-only viewer for notes with markdown rendering"""
    
    edit_requested = pyqtSignal(int)
    delete_requested = pyqtSignal(int)
    pin_toggled = pyqtSignal(int)
    
    def __init__(self, parent=None, note=None, controller=None):
        self.note = note
        self.controller = controller
        self.markdown_mode = False
        
        super().__init__(parent, note.title if note else "Note", width=700, height=600)
        self.setup_content()
        self.add_action_buttons()
    
    def setup_content(self):
        """Setup viewer content"""
        # Header with title and metadata
        header_layout = QHBoxLayout()
        
        # Title
        title_label = QLabel(self.note.title)
        font = QFont()
        font.setPointSize(16)
        font.setBold(True)
        title_label.setFont(font)
        title_label.setWordWrap(True)
        header_layout.addWidget(title_label, 1)
        
        # Pin indicator
        if self.note.pinned:
            pin_label = QLabel("📌")
            font = QFont()
            font.setPointSize(16)
            pin_label.setFont(font)
            header_layout.addWidget(pin_label)
        
        self.layout.addLayout(header_layout)
        
        # Metadata
        meta_layout = QHBoxLayout()
        
        created_label = QLabel(f"Created: {format_datetime(self.note.created_at)}")
        created_label.setProperty("class", "meta-text")
        font = QFont()
        font.setPointSize(9)
        created_label.setFont(font)
        meta_layout.addWidget(created_label)
        
        meta_layout.addStretch()
        
        updated_label = QLabel(f"Updated: {format_datetime(self.note.updated_at)}")
        updated_label.setProperty("class", "meta-text")
        font = QFont()
        font.setPointSize(9)
        updated_label.setFont(font)
        meta_layout.addWidget(updated_label)
        
        self.layout.addLayout(meta_layout)
        
        # Tags
        if self.note.tags:
            tags_layout = QHBoxLayout()
            tags_layout.setSpacing(6)
            
            tags_title = QLabel("Tags:")
            font = QFont()
            font.setPointSize(9)
            font.setBold(True)
            tags_title.setFont(font)
            tags_layout.addWidget(tags_title)
            
            for tag in self.note.tags.split(','):
                tag = tag.strip()
                if tag:
                    tag_pill = QLabel(f"#{tag}")
                    font = QFont()
                    font.setPointSize(8)
                    font.setBold(True)
                    tag_pill.setFont(font)
                    tag_pill.setStyleSheet("""
                        QLabel {
                            padding: 0.3em 0.8em;
                            border-radius: 10px;
                            background-color: rgba(100, 150, 255, 0.2);
                            border: 1px solid rgba(100, 150, 255, 0.4);
                            color: rgba(100, 150, 255, 1.0);
                        }
                    """)
                    tags_layout.addWidget(tag_pill)
            
            tags_layout.addStretch()
            self.layout.addLayout(tags_layout)
        
        # Markdown toggle
        toggle_layout = QHBoxLayout()
        toggle_layout.addStretch()
        
        self.markdown_toggle = QCheckBox("📝 Render Markdown")
        self.markdown_toggle.setChecked(False)
        self.markdown_toggle.stateChanged.connect(self.toggle_markdown)
        toggle_layout.addWidget(self.markdown_toggle)
        
        self.layout.addLayout(toggle_layout)
        
        # Content viewer
        self.content_viewer = QTextEdit()
        self.content_viewer.setReadOnly(True)
        self.content_viewer.setPlainText(self.note.content)
        self.content_viewer.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Expanding
        )
        self.content_viewer.setWordWrapMode(QTextOption.WrapMode.WordWrap)
        self.content_viewer.setLineWrapMode(QTextEdit.LineWrapMode.WidgetWidth)
        
        # Apply theme styling
        self._apply_content_styling()
        
        self.layout.addWidget(self.content_viewer, 1)
    
    def add_action_buttons(self):
        """Add action buttons at the bottom"""
        actions_layout = QHBoxLayout()
        actions_layout.setSpacing(10)
        
        # Pin/Unpin button
        pin_text = "📍 Unpin" if self.note.pinned else "📌 Pin"
        self.pin_btn = QPushButton(pin_text)
        self.pin_btn.setMinimumWidth(100)
        self.pin_btn.setMinimumHeight(36)
        self.pin_btn.clicked.connect(self.on_pin_toggle)
        actions_layout.addWidget(self.pin_btn)
        
        actions_layout.addStretch()
        
        # Edit button
        edit_btn = QPushButton("✏️ Edit")
        edit_btn.setMinimumWidth(100)
        edit_btn.setMinimumHeight(36)
        edit_btn.clicked.connect(self.on_edit)
        actions_layout.addWidget(edit_btn)
        
        # Delete button
        delete_btn = QPushButton("🗑️ Delete")
        delete_btn.setMinimumWidth(100)
        delete_btn.setMinimumHeight(36)
        delete_btn.clicked.connect(self.on_delete)
        actions_layout.addWidget(delete_btn)
        
        # Close button
        close_btn = QPushButton("Close")
        close_btn.setMinimumWidth(100)
        close_btn.setMinimumHeight(36)
        close_btn.clicked.connect(self.reject)
        actions_layout.addWidget(close_btn)
        
        self.layout.addLayout(actions_layout)
    
    def toggle_markdown(self, state):
        """Toggle between plain text and markdown rendering"""
        self.markdown_mode = state == Qt.CheckState.Checked.value
        
        if self.markdown_mode:
            # Render as markdown
            html = self._markdown_to_html(self.note.content)
            self.content_viewer.setHtml(html)
        else:
            # Show plain text
            self.content_viewer.setPlainText(self.note.content)
    
    def _markdown_to_html(self, text):
        """Convert markdown to HTML using proper markdown library"""
        # Get theme colors
        from src.core.theme_manager import theme_manager
        from src.models.theme import Theme
        from src.core.database import db
        
        # Default colors (fallback)
        bg_primary = "#36393f"
        bg_secondary = "#2f3136"
        bg_tertiary = "#202225"
        fg_primary = "#dcddde"
        fg_secondary = "#b9bbbe"
        border_color = "#202225"
        accent_color = "#5865f2"
        
        try:
            db.connect(reuse_if_open=True)
            theme_obj = Theme.get(Theme.name == theme_manager.current_theme)
            bg_primary = theme_obj.bg_primary
            bg_secondary = theme_obj.bg_secondary
            bg_tertiary = theme_obj.bg_tertiary
            fg_primary = theme_obj.fg_primary
            fg_secondary = theme_obj.fg_secondary
            border_color = theme_obj.border
            accent_color = theme_obj.accent
            db.close()
        except:
            pass
        
        try:
            import re
            
            # Escape HTML in text first
            def escape_html(text):
                return text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
            
            # Process code blocks FIRST before any other markdown
            def process_code_blocks(text):
                # Match fenced code blocks with optional language
                pattern = r'```(\w*)\n(.*?)```'
                
                def replace_code_block(match):
                    lang = match.group(1)
                    code = match.group(2).rstrip('\n')  # Remove trailing newline
                    # Escape HTML in code
                    code_escaped = escape_html(code)
                    return f'<pre><code>{code_escaped}</code></pre>'
                
                return re.sub(pattern, replace_code_block, text, flags=re.DOTALL)
            
            # Process inline code
            def process_inline_code(text):
                # Match inline code `code`
                pattern = r'`([^`]+)`'
                def replace_inline(match):
                    code = escape_html(match.group(1))
                    return f'<code>{code}</code>'
                return re.sub(pattern, replace_inline, text)
            
            # Process the text
            html_content = text
            
            # 1. Process code blocks first (so they don't get affected by other processing)
            html_content = process_code_blocks(html_content)
            
            # 2. Process inline code
            html_content = process_inline_code(html_content)
            
            # 3. Process headers
            html_content = re.sub(r'^### (.*?)$', r'<h3>\1</h3>', html_content, flags=re.MULTILINE)
            html_content = re.sub(r'^## (.*?)$', r'<h2>\1</h2>', html_content, flags=re.MULTILINE)
            html_content = re.sub(r'^# (.*?)$', r'<h1>\1</h1>', html_content, flags=re.MULTILINE)
            
            # 4. Process bold and italic
            html_content = re.sub(r'\*\*\*(.+?)\*\*\*', r'<strong><em>\1</em></strong>', html_content)
            html_content = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', html_content)
            html_content = re.sub(r'\*(.+?)\*', r'<em>\1</em>', html_content)
            html_content = re.sub(r'___(.+?)___', r'<strong><em>\1</em></strong>', html_content)
            html_content = re.sub(r'__(.+?)__', r'<strong>\1</strong>', html_content)
            html_content = re.sub(r'_(.+?)_', r'<em>\1</em>', html_content)
            
            # 5. Process links
            html_content = re.sub(r'\[([^\]]+)\]\(([^\)]+)\)', r'<a href="\2">\1</a>', html_content)
            
            # 6. Process lists
            html_content = re.sub(r'^\* (.+)$', r'<li>\1</li>', html_content, flags=re.MULTILINE)
            html_content = re.sub(r'^\- (.+)$', r'<li>\1</li>', html_content, flags=re.MULTILINE)
            html_content = re.sub(r'(<li>.*</li>)', r'<ul>\1</ul>', html_content, flags=re.DOTALL)
            
            # 7. Process paragraphs (but NOT inside pre blocks)
            lines = html_content.split('\n')
            processed_lines = []
            in_pre = False
            
            for line in lines:
                if '<pre>' in line:
                    in_pre = True
                    processed_lines.append(line)
                elif '</pre>' in line:
                    in_pre = False
                    processed_lines.append(line)
                elif in_pre:
                    processed_lines.append(line)
                elif line.strip() and not line.startswith('<'):
                    processed_lines.append(f'<p>{line}</p>')
                else:
                    processed_lines.append(line)
            
            html_content = '\n'.join(processed_lines)
            
            # Wrap with theme-aware styling
            styled_html = f'''
<!DOCTYPE html>
<html>
<head>
<style>
    * {{
        margin: 0;
        padding: 0;
        box-sizing: border-box;
    }}
    
    body {{
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "Noto Sans", Helvetica, Arial, sans-serif;
        font-size: 16px;
        line-height: 1.6;
        color: {fg_primary};
        background-color: transparent;
        padding: 16px;
        word-wrap: break-word;
    }}
    
    h1, h2, h3, h4, h5, h6 {{
        margin-top: 24px;
        margin-bottom: 16px;
        font-weight: 600;
        line-height: 1.25;
        color: {fg_primary};
    }}
    
    h1 {{
        font-size: 2em;
        padding-bottom: 0.3em;
        border-bottom: 2px solid {border_color};
    }}
    
    h2 {{
        font-size: 1.5em;
        padding-bottom: 0.3em;
        border-bottom: 1px solid {border_color};
    }}
    
    h3 {{ font-size: 1.25em; }}
    
    p {{
        margin-top: 0;
        margin-bottom: 16px;
        color: {fg_primary};
    }}
    
    a {{
        color: {accent_color};
        text-decoration: none;
    }}
    
    a:hover {{
        text-decoration: underline;
    }}
    
    code {{
        padding: 0.2em 0.4em;
        margin: 0;
        font-size: 85%;
        background-color: {bg_tertiary};
        border-radius: 3px;
        font-family: "Consolas", "Courier New", "Courier", monospace;
        color: {fg_primary};
        border: 1px solid {border_color};
    }}
    
    pre {{
        padding: 12px;
        overflow-x: auto;
        font-size: 14px;
        line-height: 1.4;
        background-color: {bg_tertiary};
        border: 1px solid {border_color};
        border-radius: 4px;
        margin: 8px 0 16px 0;
        font-family: "Consolas", "Courier New", "Courier", monospace;
    }}
    
    pre code {{
        padding: 0;
        margin: 0;
        background-color: transparent;
        border: none;
        font-size: 14px;
        color: {fg_primary};
        display: block;
        white-space: pre;
        line-height: 1.4;
    }}
    
    ul, ol {{
        padding-left: 2em;
        margin-top: 0;
        margin-bottom: 16px;
        color: {fg_primary};
    }}
    
    li {{
        margin-top: 0.25em;
        color: {fg_primary};
    }}
    
    strong {{
        font-weight: 700;
        color: {fg_primary};
    }}
    
    em {{
        font-style: italic;
    }}
    
    blockquote {{
        padding: 8px 16px;
        color: {fg_secondary};
        border-left: 4px solid {border_color};
        margin-top: 0;
        margin-bottom: 16px;
        background-color: {bg_secondary};
        border-radius: 0 4px 4px 0;
    }}
    
    hr {{
        height: 1px;
        padding: 0;
        margin: 24px 0;
        background-color: {border_color};
        border: 0;
    }}
</style>
</head>
<body>
{html_content}
</body>
</html>
            '''
            
            return styled_html
            
        except Exception as e:
            # Fallback
            return f'''
<!DOCTYPE html>
<html>
<head>
<style>
    body {{
        font-family: monospace;
        padding: 16px;
        color: {fg_primary};
        background-color: transparent;
    }}
    pre {{
        background: {bg_tertiary};
        border: 1px solid {border_color};
        padding: 16px;
        border-radius: 4px;
        overflow-x: auto;
        white-space: pre;
        color: {fg_primary};
    }}
</style>
</head>
<body>
    <p style="color: #f04747;">Error: {str(e)}</p>
    <pre>{text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')}</pre>
</body>
</html>
            '''
    
    def _apply_content_styling(self):
        """Apply theme styling to content viewer"""
        from src.core.theme_manager import theme_manager
        from src.models.theme import Theme
        from src.core.database import db
        
        theme = theme_manager.current_theme
        if theme:
            try:
                db.connect(reuse_if_open=True)
                theme_obj = Theme.get(Theme.name == theme)
                self.content_viewer.setStyleSheet(f"""
                    QTextEdit {{
                        background-color: {theme_obj.bg_secondary};
                        color: {theme_obj.fg_primary};
                        border: 2px solid {theme_obj.border};
                        border-radius: 6px;
                        padding: 12px 16px;
                        font-size: 11pt;
                        line-height: 1.6;
                    }}
                    QTextEdit::corner {{
                        background-color: {theme_obj.bg_tertiary};
                        border: 1px solid {theme_obj.border};
                    }}
                """)
                db.close()
            except:
                pass
    
    def on_pin_toggle(self):
        """Handle pin toggle"""
        self.pin_toggled.emit(self.note.id)
        self.note.pinned = not self.note.pinned
        pin_text = "📍 Unpin" if self.note.pinned else "📌 Pin"
        self.pin_btn.setText(pin_text)
    
    def on_edit(self):
        """Handle edit button"""
        self.edit_requested.emit(self.note.id)
        self.accept()
    
    def on_delete(self):
        """Handle delete button"""
        from PyQt6.QtWidgets import QMessageBox
        reply = QMessageBox.question(
            self,
            "Delete Note",
            "Are you sure you want to delete this note?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.delete_requested.emit(self.note.id)
            self.accept()
