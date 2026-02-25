"""
Settings View
Main settings page with change tracking
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QScrollArea, QFrame, QMessageBox, QLineEdit
)
from PyQt6.QtCore import Qt, pyqtSignal

from src.features.settings.sections.appearance import AppearanceSection
from src.features.settings.sections.locale import LocaleSection
from src.features.settings.sections.themes import ThemesSection
from src.features.settings.sections.paths import PathsSection
from src.features.settings.sections.about import AboutSection


class SettingsView(QWidget):
    """Settings main view with change tracking"""
    
    # Signal to request navigation away
    navigation_requested = pyqtSignal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.sections = []  # Store section containers for filtering
        self.setup_ui()
    
    def setup_ui(self):
        """Setup settings UI"""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)
        
        # Header
        from PyQt6.QtGui import QFont
        header = QLabel("⚙ Settings")
        font = QFont()
        font.setPointSize(18)
        font.setBold(True)
        header.setFont(font)
        main_layout.addWidget(header)
        
        # Search bar
        search_container = QFrame()
        search_layout = QHBoxLayout(search_container)
        search_layout.setContentsMargins(0, 0, 0, 0)
        search_layout.setSpacing(8)
        
        # Search icon (permanent)
        search_icon = QLabel("🔍")
        search_icon.setFixedWidth(30)
        search_icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        search_layout.addWidget(search_icon)
        
        # Search input
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search settings...")
        self.search_input.textChanged.connect(self.filter_sections)
        search_layout.addWidget(self.search_input)
        
        main_layout.addWidget(search_container)
        
        # Scroll area for settings sections
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        
        # Content widget
        content = QWidget()
        self.content_layout = QVBoxLayout(content)
        self.content_layout.setSpacing(20)
        self.content_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        
        # Add settings sections
        self.appearance_section = AppearanceSection()
        self.themes_section = ThemesSection()
        self.locale_section = LocaleSection()
        self.paths_section = PathsSection()
        self.about_section = AboutSection()
        
        # Create sections and store references
        sections_data = [
            ("Appearance", self.appearance_section),
            ("Themes", self.themes_section),
            ("Locale & Format", self.locale_section),
            ("File Locations", self.paths_section),
            ("About", self.about_section)
        ]
        
        for title, section_widget in sections_data:
            section_container = self.create_section(title, section_widget)
            self.sections.append({
                'title': title,
                'container': section_container,
                'widget': section_widget
            })
            self.content_layout.addWidget(section_container)
        
        scroll.setWidget(content)
        main_layout.addWidget(scroll)
        
        self.setLayout(main_layout)
    
    def create_section(self, title: str, section_widget: QWidget) -> QFrame:
        """Create a settings section container"""
        container = QFrame()
        container.setObjectName("settings-section")
        container.setProperty("section_title", title)  # Store title for searching
        
        layout = QVBoxLayout(container)
        layout.setSpacing(15)
        
        # Section title
        from PyQt6.QtGui import QFont
        title_label = QLabel(title)
        font = QFont()
        font.setPointSize(14)
        font.setBold(True)
        title_label.setFont(font)
        layout.addWidget(title_label)
        
        # Section content
        layout.addWidget(section_widget)
        
        container.setLayout(layout)
        return container
    
    def filter_sections(self, search_text: str):
        """Filter settings sections based on search text"""
        search_text = search_text.lower().strip()
        
        # If search is empty, show all sections
        if not search_text:
            for section in self.sections:
                section['container'].setVisible(True)
            return
        
        # Filter sections based on title and content
        for section in self.sections:
            title = section['title'].lower()
            
            # Check if search matches title
            if search_text in title:
                section['container'].setVisible(True)
                continue
            
            # Check if search matches any text in the section widget
            section_text = self.get_widget_text(section['widget']).lower()
            if search_text in section_text:
                section['container'].setVisible(True)
            else:
                section['container'].setVisible(False)
    
    def get_widget_text(self, widget: QWidget) -> str:
        """Recursively get all text from a widget and its children"""
        text_parts = []
        
        # Get text from QLabel
        if isinstance(widget, QLabel):
            text_parts.append(widget.text())
        
        # Get text from QLineEdit
        if isinstance(widget, QLineEdit):
            if widget.placeholderText():
                text_parts.append(widget.placeholderText())
        
        # Recursively get text from children
        for child in widget.findChildren(QWidget):
            if isinstance(child, QLabel):
                text_parts.append(child.text())
            elif isinstance(child, QLineEdit):
                if child.placeholderText():
                    text_parts.append(child.placeholderText())
        
        return " ".join(text_parts)
    
    def check_unsaved_changes(self) -> bool:
        """
        Check for unsaved changes and prompt user
        Returns True if navigation should proceed, False if cancelled
        """
        # Check if any section has unsaved changes (enabled Apply button)
        has_changes = False
        
        # Check appearance section
        if hasattr(self.appearance_section, 'apply_btn') and self.appearance_section.apply_btn.isEnabled():
            has_changes = True
        
        # Check locale section
        if hasattr(self.locale_section, 'apply_btn') and self.locale_section.apply_btn.isEnabled():
            has_changes = True
        
        if not has_changes:
            return True
        
        msg = QMessageBox(self)
        msg.setWindowTitle("Unsaved Changes")
        msg.setText("You have unsaved changes in Settings.")
        msg.setInformativeText("What would you like to do?")
        msg.setIcon(QMessageBox.Icon.Warning)
        
        # Style buttons with em units to prevent text cutoff
        msg.setStyleSheet("""
            QPushButton {
                min-width: 10em;
                min-height: 2.5em;
                padding: 0.5em 1em;
            }
        """)
        
        # Add custom buttons
        apply_btn = msg.addButton("Apply Changes", QMessageBox.ButtonRole.AcceptRole)
        discard_btn = msg.addButton("Discard Changes", QMessageBox.ButtonRole.DestructiveRole)
        cancel_btn = msg.addButton("Cancel", QMessageBox.ButtonRole.RejectRole)
        
        msg.exec()
        
        clicked = msg.clickedButton()
        
        if clicked == apply_btn:
            # Apply changes from all sections
            if hasattr(self.appearance_section, 'apply_btn') and self.appearance_section.apply_btn.isEnabled():
                self.appearance_section.on_apply()
            if hasattr(self.locale_section, 'apply_btn') and self.locale_section.apply_btn.isEnabled():
                self.locale_section.on_apply()
            return True
        elif clicked == discard_btn:
            # Discard changes from all sections
            if hasattr(self.appearance_section, 'on_cancel'):
                self.appearance_section.on_cancel()
            if hasattr(self.locale_section, 'on_cancel'):
                self.locale_section.on_cancel()
            return True
        else:
            # Cancel navigation
            return False
    
    def refresh(self):
        """Refresh view to apply config changes"""
        pass

