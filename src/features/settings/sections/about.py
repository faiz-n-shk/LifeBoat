"""
About Settings Section
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton
)
from PyQt6.QtCore import Qt

from src.core.constants import APP_NAME, APP_VERSION, APP_AUTHOR, APP_DESCRIPTION, BUILD_TYPE


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
        from PyQt6.QtGui import QPixmap
        from PyQt6.QtCore import Qt as QtCore
        from src.core.path_manager import get_resource_path
        
        logo = QLabel()
        icon_pixmap = QPixmap(get_resource_path("assets/icons/lifeboat.svg"))
        logo.setPixmap(icon_pixmap.scaled(64, 64, QtCore.AspectRatioMode.KeepAspectRatio, QtCore.TransformationMode.SmoothTransformation))
        logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(logo)
        
        # App name
        from PyQt6.QtGui import QFont
        name = QLabel(APP_NAME)
        font2 = QFont()
        font2.setPointSize(15)
        font2.setBold(True)
        name.setFont(font2)
        name.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(name)
        
        # Version
        version = QLabel(f"Version {APP_VERSION}")
        version.setProperty("class", "title-text")
        version.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(version)
        
        # Build type
        import sys
        if getattr(sys, 'frozen', False):
            build_text = f"Production Build ({BUILD_TYPE.capitalize()})"
        else:
            build_text = f"Development Build ({BUILD_TYPE.capitalize()})"
        build_label = QLabel(build_text)
        build_label.setProperty("class", "secondary-text")
        build_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(build_label)
        
        # Description
        description = QLabel(APP_DESCRIPTION)
        description.setProperty("class", "secondary-text")
        description.setAlignment(Qt.AlignmentFlag.AlignCenter)
        description.setWordWrap(True)
        layout.addWidget(description)
        
        # Author
        author = QLabel(f"Made by {APP_AUTHOR}")
        author.setProperty("class", "meta-text")
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
        copyright_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(copyright_label)
        
        self.setLayout(layout)
    
    def on_check_updates(self):
        """Handle check for updates"""
        from PyQt6.QtWidgets import QMessageBox
        from PyQt6.QtCore import QUrl
        from PyQt6.QtGui import QDesktopServices
        import requests
        
        try:
            # Show checking message
            msg = QMessageBox(self)
            msg.setWindowTitle("Checking for Updates")
            msg.setText("Checking for updates...")
            msg.setStandardButtons(QMessageBox.StandardButton.NoButton)
            msg.show()
            msg.repaint()
            
            # Fetch latest version from GitHub API
            # Using lifeboat repo latest releases page
            api_url = "https://api.github.com/repos/faiz-n-shk/LifeBoat/releases/latest"
            response = requests.get(api_url, timeout=5)
            
            msg.close()
            
            if response.status_code == 200:
                data = response.json()
                latest_version = data.get('tag_name', '').lstrip('v')
                release_url = data.get('html_url', '')
                release_notes = data.get('body', 'No release notes available.')
                
                # Compare versions
                if latest_version > APP_VERSION:
                    # New version available
                    result = QMessageBox.information(
                        self,
                        "Update Available",
                        f"A new version is available!\n\n"
                        f"Current Version: {APP_VERSION}\n"
                        f"Latest Version: {latest_version}\n\n"
                        f"Would you like to download it?",
                        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                    )
                    
                    if result == QMessageBox.StandardButton.Yes:
                        QDesktopServices.openUrl(QUrl(release_url))
                else:
                    # Already up to date
                    QMessageBox.information(
                        self,
                        "Up to Date",
                        f"You are running the latest version ({APP_VERSION})."
                    )
            else:
                # API error
                QMessageBox.warning(
                    self,
                    "Update Check Failed",
                    f"Could not check for updates.\n\n"
                    f"Status Code: {response.status_code}\n\n"
                    f"Please check manually at:\n"
                    f"https://github.com/faiz-n-shk/LifeBoat/releases"
                )
        
        except requests.exceptions.RequestException as e:
            # Network error
            QMessageBox.warning(
                self,
                "Connection Error",
                f"Could not connect to update server.\n\n"
                f"Error: {str(e)}\n\n"
                f"Please check your internet connection or visit:\n"
                f"https://github.com/faiz-n-shk/LifeBoat/releases"
            )
        except Exception as e:
            # Other errors
            QMessageBox.critical(
                self,
                "Error",
                f"An error occurred while checking for updates:\n{str(e)}"
            )
    
    def on_view_changelog(self):
        """Handle view changelog"""
        from PyQt6.QtWidgets import QDialog, QVBoxLayout, QTextEdit, QPushButton, QHBoxLayout, QMessageBox
        from PyQt6.QtCore import Qt
        import requests
        
        # Create changelog dialog
        dialog = QDialog(self)
        dialog.setWindowTitle("Changelog")
        dialog.resize(700, 500)
        
        layout = QVBoxLayout(dialog)
        
        # Text area for changelog
        text_edit = QTextEdit()
        text_edit.setReadOnly(True)
        text_edit.setPlainText("Loading changelog from GitHub...")
        
        layout.addWidget(text_edit)
        
        # Close button
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(dialog.accept)
        button_layout.addWidget(close_btn)
        
        layout.addLayout(button_layout)
        
        # Show dialog
        dialog.show()
        dialog.repaint()
        
        # Fetch changelog from GitHub
        try:
            # Fetch CHANGELOG.md from GitHub repository
            # Using the CHANGELOG.md file in git repo
            changelog_url = "https://raw.githubusercontent.com/faiz-n-shk/LifeBoat/main/documentations/CHANGELOG.md"
            response = requests.get(changelog_url, timeout=5)
            
            if response.status_code == 200:
                # Successfully fetched changelog
                changelog_content = response.text
                text_edit.setMarkdown(changelog_content)
            else:
                # File not found or other error
                text_edit.setMarkdown(f"""
# Changelog

## Version {APP_VERSION}

**Note:** Could not fetch changelog from GitHub (Status: {response.status_code}).

The changelog file should be at:
`documentation/CHANGELOG.md` in the main branch of the Lifeboat repository.

Visit the repository for full changelog:
https://github.com/faiz-n-shk/LifeBoat
""")
        
        except requests.exceptions.RequestException as e:
            # Network error
            text_edit.setMarkdown(f"""
# Changelog

## Version {APP_VERSION}

**Note:** Could not connect to GitHub to fetch changelog.

Error: {str(e)}

Please check your internet connection or visit:
https://github.com/faiz-n-shk/LifeBoat/blob/main/documentations/CHANGELOG.md
""")
        
        except Exception as e:
            # Other errors
            text_edit.setPlainText(f"Error loading changelog: {str(e)}")
        
        dialog.exec()
