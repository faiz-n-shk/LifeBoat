"""
About Settings Section
"""
import logging
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton
)
from PyQt6.QtCore import Qt

from src.core.constants import APP_NAME, APP_VERSION, APP_AUTHOR, APP_DESCRIPTION, BUILD_TYPE

logger = logging.getLogger(__name__)


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
        from PyQt6.QtCore import QUrl, QThread, pyqtSignal, Qt, QSize
        from PyQt6.QtGui import QDesktopServices, QIcon, QCursor, QFont, QColor
        from PyQt6.QtWidgets import QMessageBox, QDialog, QVBoxLayout, QLabel, QFrame, QHBoxLayout, QPushButton, QGraphicsDropShadowEffect
        from src.core.updater import Updater
        from src.shared.dialogs import create_message_box, show_information, show_warning, show_critical
        from src.core.path_manager import get_resource_path
        from src.core.theme_manager import theme_manager
        from src.models.theme import Theme
        from src.core.database import db
        
        logger.info("User initiated update check")
        
        # Create worker thread
        class UpdateCheckWorker(QThread):
            finished = pyqtSignal(object)
            
            def run(self):
                try:
                    logger.info("Update check worker started")
                    updater = Updater()
                    result = updater.check_for_updates()
                    logger.info(f"Update check completed: {result}")
                    self.finished.emit(result)
                except Exception as e:
                    logger.error(f"Update check worker error: {e}", exc_info=True)
                    self.finished.emit({'error': str(e)})
        
        # Create a styled non-blocking progress dialog
        checking_dialog = QDialog(self)
        checking_dialog.setWindowFlags(Qt.WindowType.Dialog | Qt.WindowType.FramelessWindowHint)
        checking_dialog.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        checking_dialog.setFixedWidth(450)
        
        outer_layout = QVBoxLayout(checking_dialog)
        outer_layout.setContentsMargins(10, 10, 10, 10)
        
        container = QFrame()
        container.setObjectName("checking-dialog-container")
        outer_layout.addWidget(container)
        
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setXOffset(0)
        shadow.setYOffset(0)
        shadow.setColor(QColor(0, 0, 0, 100))
        container.setGraphicsEffect(shadow)
        
        container_layout = QVBoxLayout(container)
        container_layout.setContentsMargins(0, 0, 0, 0)
        container_layout.setSpacing(0)
        
        # Title bar
        title_bar = QFrame()
        title_bar.setObjectName("checking-dialog-title-bar")
        title_bar.setFixedHeight(50)
        title_bar_layout = QHBoxLayout(title_bar)
        title_bar_layout.setContentsMargins(20, 0, 10, 0)
        
        title_label = QLabel("Checking for Updates")
        title_label.setObjectName("checking-dialog-title")
        font = QFont()
        font.setPointSize(14)
        font.setBold(True)
        title_label.setFont(font)
        title_bar_layout.addWidget(title_label)
        
        title_bar_layout.addStretch()
        
        # Close button
        close_btn = QPushButton()
        close_btn.setIcon(QIcon(get_resource_path("assets/icons/icon_cross.svg")))
        close_btn.setFixedSize(28, 28)
        close_btn.setIconSize(QSize(16, 16))
        close_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        close_btn.setObjectName("checking-dialog-close-btn")
        close_btn.clicked.connect(checking_dialog.reject)
        title_bar_layout.addWidget(close_btn)
        
        container_layout.addWidget(title_bar)
        
        # Content
        content_widget = QWidget()
        content_widget.setObjectName("checking-dialog-content")
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(20, 30, 20, 30)
        
        message_label = QLabel("Checking for updates...\n\nPlease wait.")
        message_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        message_label.setObjectName("checking-dialog-text")
        font = QFont()
        font.setPointSize(11)
        message_label.setFont(font)
        content_layout.addWidget(message_label)
        
        container_layout.addWidget(content_widget)
        
        # Apply theme styling
        try:
            db.connect(reuse_if_open=True)
            theme_obj = Theme.get(Theme.name == theme_manager.current_theme)
            
            container.setStyleSheet(f"""
                QFrame#checking-dialog-container {{
                    background-color: {theme_obj.bg_primary};
                    border: 2px solid {theme_obj.border};
                    border-radius: 12px;
                }}
            """)
            
            title_bar.setStyleSheet(f"""
                QFrame#checking-dialog-title-bar {{
                    background-color: {theme_obj.bg_secondary};
                    border-top-left-radius: 10px;
                    border-top-right-radius: 10px;
                    border-bottom: 1px solid {theme_obj.border};
                }}
                QLabel#checking-dialog-title {{
                    color: {theme_obj.fg_primary};
                }}
            """)
            
            close_btn.setStyleSheet(f"""
                QPushButton#checking-dialog-close-btn {{
                    background-color: transparent;
                    border: none;
                    border-radius: 4px;
                    padding: 0px;
                    min-width: 28px;
                    max-width: 28px;
                    min-height: 28px;
                    max-height: 28px;
                }}
                QPushButton#checking-dialog-close-btn:hover {{
                    background-color: {theme_obj.danger};
                }}
                QPushButton#checking-dialog-close-btn:pressed {{
                    background-color: {theme_obj.danger};
                    opacity: 0.8;
                }}
            """)
            
            content_widget.setStyleSheet(f"""
                QWidget#checking-dialog-content {{
                    background-color: {theme_obj.bg_primary};
                    border-bottom-left-radius: 10px;
                    border-bottom-right-radius: 10px;
                }}
            """)
            
            message_label.setStyleSheet(f"""
                QLabel#checking-dialog-text {{
                    color: {theme_obj.fg_primary};
                }}
            """)
            
            db.close()
        except:
            pass
        
        # Store as instance variables
        self._update_worker = UpdateCheckWorker()
        self._checking_dialog = checking_dialog
        
        # Add cleanup handler if dialog is closed manually
        def on_dialog_rejected():
            """Handle dialog being closed manually"""
            logger.info("Checking dialog closed manually")
            if hasattr(self, '_update_worker') and self._update_worker:
                if self._update_worker.isRunning():
                    logger.info("Stopping update check worker")
                    self._update_worker.quit()
                    self._update_worker.wait(1000)  # Wait up to 1 second
                self._update_worker.deleteLater()
                self._update_worker = None
            if hasattr(self, '_checking_dialog') and self._checking_dialog:
                self._checking_dialog = None
        
        checking_dialog.rejected.connect(on_dialog_rejected)
        
        def on_finished(result):
            """Handle update check completion"""
            try:
                logger.info("Update check finished callback triggered")
                
                # Close checking dialog
                if hasattr(self, '_checking_dialog') and self._checking_dialog is not None:
                    logger.info("Closing checking dialog")
                    self._checking_dialog.close()
                    self._checking_dialog.deleteLater()
                    self._checking_dialog = None
                
                # Clean up worker thread
                if hasattr(self, '_update_worker') and self._update_worker is not None:
                    logger.info("Cleaning up worker thread")
                    self._update_worker.quit()
                    self._update_worker.wait()
                    self._update_worker.deleteLater()
                    self._update_worker = None
                
                # Handle error
                if result and isinstance(result, dict) and 'error' in result:
                    logger.error(f"Update check returned error: {result['error']}")
                    show_critical(self, "Error", f"An error occurred:\n{result['error']}")
                    return
                
                # Handle no result
                if result is None:
                    logger.warning("Update check returned no result")
                    show_warning(
                        self,
                        "Update Check Failed",
                        "Could not check for updates.\n\n"
                        "Please check your internet connection or visit:\n"
                        "https://github.com/faiz-n-shk/LifeBoat/releases"
                    )
                    return
                
                # Handle update available
                if result.get('available'):
                    logger.info(f"Update available: {result['latest_version']}")
                    button_result = create_message_box(
                        self,
                        "Update Available",
                        f"A new version is available!\n\n"
                        f"Current: {result['current_version']}\n"
                        f"Latest: {result['latest_version']}\n\n"
                        f"Download now?",
                        QMessageBox.Icon.Information,
                        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                    )
                    
                    if button_result == QMessageBox.StandardButton.Yes:
                        logger.info("User chose to download update")
                        try:
                            QDesktopServices.openUrl(QUrl(result['download_url']))
                        except Exception as e:
                            logger.error(f"Error opening download URL: {e}", exc_info=True)
                            show_critical(self, "Error", f"Could not open download page:\n{e}")
                else:
                    logger.info("No update available")
                    show_information(
                        self,
                        "Up to Date",
                        f"You are running the latest version ({result['current_version']})."
                    )
            except Exception as e:
                logger.error(f"Error in update check callback: {e}", exc_info=True)
                try:
                    show_critical(self, "Error", f"An unexpected error occurred:\n{e}")
                except:
                    pass  # If we can't show dialog, just log it
        
        # Connect and start
        self._update_worker.finished.connect(on_finished)
        
        # Ensure worker is cleaned up when finished
        self._update_worker.finished.connect(self._update_worker.deleteLater)
        
        logger.info("Starting update check worker")
        self._update_worker.start()
        
        # Center dialog on parent window
        from src.core.config import config
        from PyQt6.QtCore import QPropertyAnimation, QEasingCurve
        
        parent_geo = self.window().geometry()
        checking_dialog.adjustSize()
        dialog_geo = checking_dialog.geometry()
        x = parent_geo.x() + (parent_geo.width() - dialog_geo.width()) // 2
        y = parent_geo.y() + (parent_geo.height() - dialog_geo.height()) // 2
        checking_dialog.move(x, y)
        
        # Add fade-in animation
        if config.get('appearance.enable_animations', True):
            checking_dialog.setWindowOpacity(0.0)
            checking_dialog._fade_in_anim = QPropertyAnimation(checking_dialog, b"windowOpacity")
            checking_dialog._fade_in_anim.setDuration(150)
            checking_dialog._fade_in_anim.setStartValue(0.0)
            checking_dialog._fade_in_anim.setEndValue(1.0)
            checking_dialog._fade_in_anim.setEasingCurve(QEasingCurve.Type.InOutQuad)
            checking_dialog._fade_in_anim.start()
        else:
            checking_dialog.setWindowOpacity(1.0)
        
        # Show checking dialog non-blocking
        checking_dialog.show()
    
    def on_view_changelog(self):
        """Handle view changelog"""
        from PyQt6.QtWidgets import QDialog, QVBoxLayout, QTextBrowser, QPushButton, QHBoxLayout
        import requests
        
        dialog = QDialog(self)
        dialog.setWindowTitle("Changelog")
        dialog.resize(700, 500)
        
        layout = QVBoxLayout(dialog)
        
        text_browser = QTextBrowser()
        text_browser.setReadOnly(True)
        text_browser.setOpenExternalLinks(True)
        text_browser.setPlainText("Loading changelog...")
        layout.addWidget(text_browser)
        
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(dialog.accept)
        button_layout.addWidget(close_btn)
        
        layout.addLayout(button_layout)
        
        dialog.show()
        dialog.repaint()
        
        try:
            url = "https://raw.githubusercontent.com/faiz-n-shk/LifeBoat/main/changelogs/CHANGELOG.md"
            response = requests.get(url, timeout=5)
            
            if response.status_code == 200:
                text_browser.setMarkdown(response.text)
            else:
                text_browser.setMarkdown(f"""
# Changelog

## Version {APP_VERSION}

Could not fetch changelog (Status: {response.status_code}).

Visit: [https://github.com/faiz-n-shk/LifeBoat](https://github.com/faiz-n-shk/LifeBoat)
""")
        except requests.exceptions.RequestException as e:
            text_browser.setMarkdown(f"""
# Changelog

## Version {APP_VERSION}

Could not connect to GitHub.

Error: {str(e)}

Visit: [https://github.com/faiz-n-shk/LifeBoat/blob/main/changelogs/CHANGELOG.md](https://github.com/faiz-n-shk/LifeBoat/blob/main/changelogs/CHANGELOG.md)
""")
        except Exception as e:
            text_browser.setPlainText(f"Error: {str(e)}")
        
        dialog.exec()
