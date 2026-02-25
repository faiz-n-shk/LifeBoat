"""
About Settings Section
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton
)
from PyQt6.QtCore import Qt

from src.core.constants import APP_NAME, APP_VERSION, APP_AUTHOR, APP_DESCRIPTION


class AboutSection(QWidget):
    """About section"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
    
    def setup_ui(self):
        """Setup about section UI"""
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        
        # App icon/logo
        logo = QLabel("⛵")
        logo.setStyleSheet("font-size: 48px;")
        logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(logo)
        
        # App name
        name = QLabel(APP_NAME)
        name.setStyleSheet("font-size: 20px; font-weight: bold;")
        name.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(name)
        
        # Version
        version = QLabel(f"Version {APP_VERSION}")
        version.setProperty("class", "secondary-text")
        version.setStyleSheet("font-size: 14px;")
        version.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(version)
        
        # Description
        description = QLabel(APP_DESCRIPTION)
        description.setProperty("class", "secondary-text")
        description.setStyleSheet("font-size: 13px;")
        description.setAlignment(Qt.AlignmentFlag.AlignCenter)
        description.setWordWrap(True)
        layout.addWidget(description)
        
        # Author
        author = QLabel(f"Made by {APP_AUTHOR}")
        author.setProperty("class", "secondary-text")
        author.setStyleSheet("font-size: 12px;")
        author.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(author)
        
        # Buttons
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(10)
        
        # Check for updates button
        update_btn = QPushButton("Check for Updates")
        update_btn.clicked.connect(self.on_check_updates)
        buttons_layout.addWidget(update_btn)
        
        # View changelog button
        changelog_btn = QPushButton("View Changelog")
        changelog_btn.clicked.connect(self.on_view_changelog)
        buttons_layout.addWidget(changelog_btn)
        
        layout.addLayout(buttons_layout)
        
        # Copyright
        copyright_label = QLabel("© 2025 Lifeboat Team. All rights reserved.")
        copyright_label.setProperty("class", "small-text")
        copyright_label.setStyleSheet("margin-top: 20px;")
        copyright_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(copyright_label)
        
        self.setLayout(layout)
    
    def on_check_updates(self):
        """Handle check for updates"""
        # TODO: Implement update checking
        print("Checking for updates...")
    
    def on_view_changelog(self):
        """Handle view changelog"""
        # TODO: Open changelog dialog or file
        print("Opening changelog...")
