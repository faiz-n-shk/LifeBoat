"""
Settings View
Main settings page with sidebar navigation
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QScrollArea, QFrame, QMessageBox, QPushButton, QStackedWidget, QGraphicsOpacityEffect
)
from PyQt6.QtCore import Qt, pyqtSignal, QPropertyAnimation, QEasingCurve
from PyQt6.QtGui import QFont, QPixmap

from src.features.settings.sections.appearance import AppearanceSection
from src.features.settings.sections.locale import LocaleSection
from src.features.settings.sections.themes import ThemesSection
from src.features.settings.sections.paths import PathsSection
from src.features.settings.sections.behavior import BehaviorSection
from src.features.settings.sections.advanced import AdvancedSection
from src.features.settings.sections.about import AboutSection
from src.core.path_manager import get_resource_path
from src.core.config import config


class SettingsView(QWidget):
    """Settings main view with sidebar navigation"""
    
    navigation_requested = pyqtSignal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.nav_buttons = []
        self.setup_ui()
    
    def setup_ui(self):
        """Setup settings UI with sidebar"""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Header
        header_container = QFrame()
        header_container.setObjectName("settings-header")
        header_layout = QHBoxLayout(header_container)
        header_layout.setContentsMargins(20, 20, 20, 20)
        
        self.header_icon_label = QLabel()
        from src.shared.icon_utils import load_accent_icon
        self.header_icon_pixmap = load_accent_icon(get_resource_path("assets/icons/feature_settings.svg"), size=(28, 28))
        self.header_icon_label.setPixmap(self.header_icon_pixmap)
        header_layout.addWidget(self.header_icon_label)
        
        header = QLabel("Settings")
        font = QFont()
        font.setPointSize(18)
        font.setBold(True)
        header.setFont(font)
        header_layout.addWidget(header)
        header_layout.addStretch()
        
        main_layout.addWidget(header_container)
        
        # Search bar
        from src.shared.search_bar import SearchBar
        search_container = QWidget()
        search_layout = QHBoxLayout(search_container)
        search_layout.setContentsMargins(20, 10, 20, 10)
        
        self.search_input = SearchBar("Search settings...")
        self.search_input.textChanged.connect(self.filter_sections)
        search_layout.addWidget(self.search_input)
        
        main_layout.addWidget(search_container)
        
        # Content area with sidebar
        content_container = QWidget()
        content_layout = QHBoxLayout(content_container)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)
        
        # Sidebar
        sidebar = QFrame()
        sidebar.setObjectName("settings-sidebar")
        sidebar.setFixedWidth(220)
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(10, 10, 10, 10)
        sidebar_layout.setSpacing(5)
        sidebar_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        
        # Section definitions
        self.sections_data = [
            ("Appearance", "appearance", AppearanceSection),
            ("Themes", "themes", ThemesSection),
            ("Language && Region", "locale", LocaleSection),
            ("Storage", "paths", PathsSection),
            ("Startup && Tray", "behavior", BehaviorSection),
            ("Advanced", "advanced", AdvancedSection),
            ("About", "about", AboutSection)
        ]
        
        # Create navigation buttons
        for title, section_id, _ in self.sections_data:
            btn = QPushButton(title)
            btn.setObjectName("settings-nav-btn")
            btn.setProperty("section_id", section_id)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setCheckable(True)
            btn.clicked.connect(lambda checked, sid=section_id: self.switch_section(sid))
            sidebar_layout.addWidget(btn)
            self.nav_buttons.append(btn)
        
        content_layout.addWidget(sidebar)
        
        # Stacked widget for sections
        self.stack = QStackedWidget()
        self.stack.setObjectName("settings-stack")
        
        # Initialize sections
        self.appearance_section = AppearanceSection()
        self.themes_section = ThemesSection()
        self.locale_section = LocaleSection()
        self.paths_section = PathsSection()
        self.behavior_section = BehaviorSection()
        self.advanced_section = AdvancedSection()
        self.about_section = AboutSection()
        
        # Wrap each section in a scroll area
        for i, (title, section_id, _) in enumerate(self.sections_data):
            section_widget = getattr(self, f"{section_id}_section")
            
            scroll = QScrollArea()
            scroll.setWidgetResizable(True)
            scroll.setFrameShape(QFrame.Shape.NoFrame)
            scroll.setObjectName("settings-scroll")
            
            wrapper = QWidget()
            wrapper_layout = QVBoxLayout(wrapper)
            wrapper_layout.setContentsMargins(30, 20, 30, 20)
            wrapper_layout.setSpacing(20)
            wrapper_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
            
            # Section title
            section_title = QLabel(title)
            title_font = QFont()
            title_font.setPointSize(16)
            title_font.setBold(True)
            section_title.setFont(title_font)
            wrapper_layout.addWidget(section_title)
            
            # Section content
            wrapper_layout.addWidget(section_widget)
            
            scroll.setWidget(wrapper)
            
            # Add opacity effect for animations (same as content_area.py)
            opacity_effect = QGraphicsOpacityEffect()
            opacity_effect.setOpacity(1.0)
            scroll.setGraphicsEffect(opacity_effect)
            scroll._opacity_effect = opacity_effect
            
            self.stack.addWidget(scroll)
        
        content_layout.addWidget(self.stack, 1)
        
        main_layout.addWidget(content_container, 1)
        
        # Select first section by default
        self.switch_section("appearance")
    
    def switch_section(self, section_id: str):
        """Switch to a different settings section (exact same logic as content_area.py)"""
        # Find section index
        section_index = next((i for i, (_, sid, _) in enumerate(self.sections_data) if sid == section_id), 0)
        
        # Don't animate if already on this section
        if self.stack.currentIndex() == section_index:
            return
        
        # Update navigation buttons
        for btn in self.nav_buttons:
            btn.setChecked(btn.property("section_id") == section_id)
        
        # Check if animations are enabled
        animations_enabled = config.get('appearance.enable_animations', True)
        
        if animations_enabled:
            # Get widgets
            current_widget = self.stack.currentWidget()
            next_widget = self.stack.widget(section_index)
            
            # Ensure next widget starts at full opacity
            next_widget._opacity_effect.setOpacity(1.0)
            
            # Quick fade out current (100ms for snappy feel)
            fade_out = QPropertyAnimation(current_widget._opacity_effect, b"opacity")
            fade_out.setDuration(100)
            fade_out.setStartValue(1.0)
            fade_out.setEndValue(0.0)
            fade_out.setEasingCurve(QEasingCurve.Type.InOutQuad)
            
            # Quick fade in next (100ms)
            fade_in = QPropertyAnimation(next_widget._opacity_effect, b"opacity")
            fade_in.setDuration(100)
            fade_in.setStartValue(0.0)
            fade_in.setEndValue(1.0)
            fade_in.setEasingCurve(QEasingCurve.Type.InOutQuad)
            
            # Switch widget when fade out completes
            def on_fade_out_finished():
                self.stack.setCurrentIndex(section_index)
                # Reset current widget opacity for next time
                current_widget._opacity_effect.setOpacity(1.0)
                fade_in.start()
            
            fade_out.finished.connect(on_fade_out_finished)
            fade_out.start()
            
            # Store animations to prevent garbage collection
            self._fade_out = fade_out
            self._fade_in = fade_in
        else:
            # No animation, just switch and ensure opacity is correct
            next_widget = self.stack.widget(section_index)
            next_widget._opacity_effect.setOpacity(1.0)
            self.stack.setCurrentIndex(section_index)
    
    def filter_sections(self, search_text: str):
        """Filter settings sections based on search text"""
        search_text = search_text.lower().strip()
        
        # If search is empty, show all navigation buttons
        if not search_text:
            for btn in self.nav_buttons:
                btn.setVisible(True)
            return
        
        # Filter navigation buttons and track first visible match
        first_match_id = None
        
        for i, (title, section_id, _) in enumerate(self.sections_data):
            btn = self.nav_buttons[i]
            section_widget = getattr(self, f"{section_id}_section")
            
            # Check if search matches title
            if search_text in title.lower():
                btn.setVisible(True)
                if first_match_id is None:
                    first_match_id = section_id
                continue
            
            # Check if search matches any text in the section widget
            section_text = self.get_widget_text(section_widget).lower()
            if search_text in section_text:
                btn.setVisible(True)
                if first_match_id is None:
                    first_match_id = section_id
            else:
                btn.setVisible(False)
        
        # Automatically switch to first matching section
        if first_match_id:
            self.switch_section(first_match_id)
    
    def get_widget_text(self, widget: QWidget) -> str:
        """Recursively get all text from a widget and its children"""
        from PyQt6.QtWidgets import QLineEdit, QCheckBox, QComboBox
        text_parts = []
        
        # Get text from QLabel
        if isinstance(widget, QLabel):
            text_parts.append(widget.text())
        
        # Get text from QPushButton
        if isinstance(widget, QPushButton):
            text_parts.append(widget.text())
        
        # Get text from QCheckBox
        if isinstance(widget, QCheckBox):
            text_parts.append(widget.text())
        
        # Get text from QLineEdit
        if isinstance(widget, QLineEdit):
            if widget.text():
                text_parts.append(widget.text())
            if widget.placeholderText():
                text_parts.append(widget.placeholderText())
        
        # Get text from QComboBox
        if isinstance(widget, QComboBox):
            for i in range(widget.count()):
                text_parts.append(widget.itemText(i))
        
        # Recursively get text from all children
        for child in widget.findChildren(QWidget):
            if isinstance(child, QLabel):
                text_parts.append(child.text())
            elif isinstance(child, QPushButton):
                text_parts.append(child.text())
            elif isinstance(child, QCheckBox):
                text_parts.append(child.text())
            elif isinstance(child, QLineEdit):
                if child.text():
                    text_parts.append(child.text())
                if child.placeholderText():
                    text_parts.append(child.placeholderText())
            elif isinstance(child, QComboBox):
                for i in range(child.count()):
                    text_parts.append(child.itemText(i))
        
        return " ".join(text_parts)
    
    def eventFilter(self, obj, event):
        """Handle button hover animations"""
        from PyQt6.QtCore import QEvent
        from PyQt6.QtWidgets import QPushButton
        
        if isinstance(obj, QPushButton) and obj.objectName() == "settings-nav-btn":
            if event.type() == QEvent.Type.Enter and not obj.isChecked():
                # Subtle scale animation on hover
                if not hasattr(obj, '_hover_anim'):
                    obj._hover_anim = QPropertyAnimation(obj, b"geometry")
                    obj._hover_anim.setDuration(150)
                    obj._hover_anim.setEasingCurve(QEasingCurve.Type.OutCubic)
                
                current_geo = obj.geometry()
                obj._hover_anim.setStartValue(current_geo)
                obj._hover_anim.setEndValue(current_geo)
                obj._hover_anim.start()
                
            elif event.type() == QEvent.Type.Leave and not obj.isChecked():
                # Reset on leave
                if hasattr(obj, '_hover_anim'):
                    obj._hover_anim.stop()
        
        return super().eventFilter(obj, event)
    
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
        
        # Check behavior section
        if hasattr(self.behavior_section, 'apply_btn') and self.behavior_section.apply_btn.isEnabled():
            has_changes = True
        
        # Check advanced section
        if hasattr(self.advanced_section, 'apply_btn') and self.advanced_section.apply_btn.isEnabled():
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
            if hasattr(self.behavior_section, 'apply_btn') and self.behavior_section.apply_btn.isEnabled():
                self.behavior_section.on_apply()
            if hasattr(self.advanced_section, 'apply_btn') and self.advanced_section.apply_btn.isEnabled():
                self.advanced_section.on_apply()
            return True
        elif clicked == discard_btn:
            # Discard changes from all sections
            if hasattr(self.appearance_section, 'on_cancel'):
                self.appearance_section.on_cancel()
            if hasattr(self.locale_section, 'on_cancel'):
                self.locale_section.on_cancel()
            if hasattr(self.behavior_section, 'on_cancel'):
                self.behavior_section.on_cancel()
            if hasattr(self.advanced_section, 'on_cancel'):
                self.advanced_section.on_cancel()
            return True
        else:
            # Cancel navigation
            return False
    
    def refresh(self):
        """Refresh view to apply config changes"""
        # Reload header icon with current theme
        from src.shared.icon_utils import load_accent_icon
        self.header_icon_pixmap = load_accent_icon(get_resource_path("assets/icons/feature_settings.svg"), size=(28, 28))
        self.header_icon_label.setPixmap(self.header_icon_pixmap)

