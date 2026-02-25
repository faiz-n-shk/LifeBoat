"""
Settings View
Main settings page
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QScrollArea, QFrame
)
from PyQt6.QtCore import Qt

from src.features.settings.sections.appearance import AppearanceSection
from src.features.settings.sections.locale import LocaleSection
from src.features.settings.sections.themes import ThemesSection
from src.features.settings.sections.paths import PathsSection
from src.features.settings.sections.about import AboutSection


class SettingsView(QWidget):
    """Settings main view"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
    
    def setup_ui(self):
        """Setup settings UI"""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)
        
        # Header
        header = QLabel("⚙ Settings")
        header.setStyleSheet("font-size: 24px; font-weight: bold;")
        main_layout.addWidget(header)
        
        # Scroll area for settings sections
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        
        # Content widget
        content = QWidget()
        content_layout = QVBoxLayout(content)
        content_layout.setSpacing(20)
        content_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        
        # Add settings sections
        content_layout.addWidget(self.create_section("Appearance", AppearanceSection()))
        content_layout.addWidget(self.create_section("Themes", ThemesSection()))
        content_layout.addWidget(self.create_section("Locale & Format", LocaleSection()))
        content_layout.addWidget(self.create_section("File Locations", PathsSection()))
        content_layout.addWidget(self.create_section("About", AboutSection()))
        
        scroll.setWidget(content)
        main_layout.addWidget(scroll)
        
        self.setLayout(main_layout)
    
    def create_section(self, title: str, section_widget: QWidget) -> QFrame:
        """Create a settings section container"""
        container = QFrame()
        container.setObjectName("settings-section")
        container.setStyleSheet("""
            #settings-section {
                background-color: #2d2d2d;
                border: 1px solid #4d4d4d;
                border-radius: 8px;
                padding: 20px;
            }
        """)
        
        layout = QVBoxLayout(container)
        layout.setSpacing(15)
        
        # Section title
        title_label = QLabel(title)
        title_label.setStyleSheet("font-size: 18px; font-weight: bold;")
        layout.addWidget(title_label)
        
        # Section content
        layout.addWidget(section_widget)
        
        container.setLayout(layout)
        return container
    
    def refresh(self):
        """Refresh view to apply config changes"""
        # Settings view doesn't need to refresh data
        pass
