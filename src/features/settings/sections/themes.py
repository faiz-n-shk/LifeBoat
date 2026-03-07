"""
Themes Settings Section
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QFrame, QDialog,
    QFormLayout, QColorDialog, QLineEdit, QScrollArea
)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QColor, QFont, QIcon

from src.core.theme_manager import theme_manager
from src.core.config import config
from src.shared.dialogs import BaseDialog


class ThemesSection(QWidget):
    """Themes settings section"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
    
    def setup_ui(self):
        """Setup themes settings UI"""
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        
        # Description
        desc = QLabel("Select a theme or create your own custom theme")
        desc.setProperty("class", "secondary-text")
        layout.addWidget(desc)
        
        # Themes container (no scroll, just list)
        self.themes_container = QWidget()
        self.themes_container.setObjectName("settings-section")
        self.themes_layout = QVBoxLayout(self.themes_container)
        self.themes_layout.setSpacing(10)
        self.themes_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        
        layout.addWidget(self.themes_container)
        
        # Create custom theme button with icon
        from src.core.path_manager import get_resource_path
        
        create_btn = QPushButton(" Create Custom Theme")
        create_btn.setIcon(QIcon(get_resource_path("assets/icons/icon_plus.svg")))
        create_btn.setIconSize(QSize(16, 16))
        create_btn.clicked.connect(self.on_create_theme)
        layout.addWidget(create_btn)
        
        self.setLayout(layout)
        
        # Load themes
        self.load_themes()
    
    def load_themes(self):
        """Load and display all themes"""
        # Clear existing
        for i in reversed(range(self.themes_layout.count())):
            widget = self.themes_layout.itemAt(i).widget()
            if widget:
                widget.deleteLater()
        
        # Add System theme first
        system_item = self.create_system_theme_item()
        self.themes_layout.addWidget(system_item)
        
        # Get all themes from database
        from src.core.database import db
        try:
            db.connect(reuse_if_open=True)
            themes = theme_manager.get_all_themes()
            current_theme = theme_manager.get_active_theme()
            
            print(f"Loaded {len(themes)} themes from database")
            
            for theme in themes:
                is_active = (theme.name == current_theme) and (current_theme != "System")
                theme_item = self.create_theme_item(theme, is_active)
                self.themes_layout.addWidget(theme_item)
            
            db.close()
        except Exception as e:
            print(f"Error loading themes: {e}")
            import traceback
            traceback.print_exc()
    
    def create_system_theme_item(self):
        """Create System theme item"""
        item = QFrame()
        item.setProperty("class", "theme-item")
        
        layout = QHBoxLayout(item)
        
        # Info section
        info_layout = QVBoxLayout()
        
        name_label = QLabel("System")
        font = QFont()
        font.setPointSize(11)
        font.setBold(True)
        name_label.setFont(font)
        info_layout.addWidget(name_label)
        
        desc_label = QLabel("Automatically switches between Dark and Light based on OS theme")
        desc_label.setProperty("class", "small-text")
        info_layout.addWidget(desc_label)
        
        layout.addLayout(info_layout, 1)
        
        # Actions
        current_theme = theme_manager.get_active_theme()
        if current_theme == "System":
            active_label = QLabel("✓ Active")
            active_label.setProperty("class", "active-label")
            layout.addWidget(active_label)
        else:
            apply_btn = QPushButton("Apply")
            apply_btn.clicked.connect(lambda: self.on_apply_theme("System"))
            layout.addWidget(apply_btn)
        
        return item
    
    def create_theme_item(self, theme, is_active):
        """Create a theme item widget"""
        item = QFrame()
        item.setProperty("class", "theme-item")
        
        layout = QHBoxLayout(item)
        
        # Color preview
        preview_layout = QHBoxLayout()
        preview_layout.setSpacing(3)
        
        colors = [
            theme.bg_primary,
            theme.bg_secondary,
            theme.accent,
            theme.success,
            theme.danger
        ]
        
        for color in colors:
            color_box = QFrame()
            color_box.setFixedSize(24, 24)
            color_box.setStyleSheet(f"""
                QFrame {{
                    background-color: {color};
                    border-radius: 3px;
                }}
            """)
            preview_layout.addWidget(color_box)
        
        layout.addLayout(preview_layout)
        
        # Theme info
        info_layout = QVBoxLayout()
        
        name_label = QLabel(theme.name)
        font = QFont()
        font.setPointSize(11)
        font.setBold(True)
        name_label.setFont(font)
        info_layout.addWidget(name_label)
        
        if theme.is_custom:
            custom_label = QLabel("Custom Theme")
            custom_label.setProperty("class", "accent-label")
            info_layout.addWidget(custom_label)
        
        layout.addLayout(info_layout, 1)
        
        # Actions
        actions_layout = QHBoxLayout()
        actions_layout.setSpacing(5)
        
        if is_active:
            active_label = QLabel("✓ Active")
            active_label.setProperty("class", "active-label")
            actions_layout.addWidget(active_label)
        else:
            apply_btn = QPushButton("Apply")
            apply_btn.clicked.connect(lambda: self.on_apply_theme(theme.name))
            actions_layout.addWidget(apply_btn)
        
        if theme.is_custom:
            edit_btn = QPushButton("Edit")
            edit_btn.clicked.connect(lambda: self.on_edit_theme(theme))
            actions_layout.addWidget(edit_btn)
            
            delete_btn = QPushButton("Delete")
            delete_btn.setProperty("class", "danger-button")
            delete_btn.clicked.connect(lambda: self.on_delete_theme(theme))
            actions_layout.addWidget(delete_btn)
        else:
            customize_btn = QPushButton("Customize")
            customize_btn.clicked.connect(lambda: self.on_customize_theme(theme))
            actions_layout.addWidget(customize_btn)
        
        layout.addLayout(actions_layout)
        
        return item
    
    def on_apply_theme(self, theme_name):
        """Apply a theme"""
        old_theme = theme_manager.get_active_theme()
        theme_manager.set_theme(theme_name)
        
        # Log theme change
        if old_theme != theme_name:
            from src.core.activity_logger import activity_logger
            activity_logger.log("Settings", "changed theme", f"{old_theme} → {theme_name}")
        
        config.signals.appearance_changed.emit()
        self.load_themes()
    
    def on_create_theme(self):
        """Create a new custom theme"""
        dialog = ThemeEditorDialog(self)
        if dialog.exec():
            colors = dialog.get_colors()
            print(f"Creating custom theme with colors: {colors}")
            if theme_manager.create_custom_theme(colors):
                print("Custom theme created successfully")
                
                # Log theme creation
                from src.core.activity_logger import activity_logger
                activity_logger.log("Settings", "created custom theme", "New custom theme")
                
                self.load_themes()
            else:
                print("Failed to create custom theme")
                from src.shared.dialogs import show_warning
                show_warning(
                    self,
                    "Error",
                    "Failed to create custom theme. Check console for details."
                )
    
    def on_edit_theme(self, theme):
        """Edit an existing custom theme"""
        dialog = ThemeEditorDialog(self, theme)
        if dialog.exec():
            colors = dialog.get_colors()
            new_name = colors.get('name', theme.name)
            
            if theme_manager.update_theme(theme.name, colors):
                # Log theme edit
                from src.core.activity_logger import activity_logger
                if theme.name != new_name:
                    activity_logger.log("Settings", "renamed theme", f"'{theme.name}' → '{new_name}'")
                else:
                    activity_logger.log("Settings", "edited theme", f"'{theme.name}'")
                
                # If editing active theme, reload it with new name
                if theme.name == theme_manager.get_active_theme() or new_name == theme_manager.get_active_theme():
                    theme_manager.load_theme(new_name)
                    config.signals.appearance_changed.emit()
                self.load_themes()
            else:
                from src.shared.dialogs import show_warning
                show_warning(
                    self,
                    "Error",
                    "Failed to update theme. The name might already exist."
                )
    
    def on_customize_theme(self, theme):
        """Create a custom theme based on an existing one"""
        dialog = ThemeEditorDialog(self, theme, is_new=True)
        if dialog.exec():
            colors = dialog.get_colors()
            print(f"Customizing theme {theme.name} with colors: {colors}")
            if theme_manager.create_custom_theme(colors, theme.name):
                print(f"Custom theme based on {theme.name} created successfully")
                
                # Log theme customization
                from src.core.activity_logger import activity_logger
                activity_logger.log("Settings", "customized theme", f"Based on '{theme.name}'")
                
                self.load_themes()
            else:
                print(f"Failed to create custom theme based on {theme.name}")
                from src.shared.dialogs import show_warning
                show_warning(
                    self,
                    "Error",
                    "Failed to create custom theme. Check console for details."
                )
    
    def on_delete_theme(self, theme):
        """Delete a custom theme"""
        from src.shared.dialogs import show_question
        from PyQt6.QtWidgets import QMessageBox
        
        result = show_question(
            self,
            "Confirm Delete",
            f"Delete theme '{theme.name}'?\n\nThis action cannot be undone."
        )
        
        if result == QMessageBox.StandardButton.Yes:
            if theme_manager.delete_theme(theme.name):
                # Log theme deletion
                from src.core.activity_logger import activity_logger
                activity_logger.log("Settings", "deleted theme", f"'{theme.name}'")
                
                self.load_themes()


class ThemeEditorDialog(BaseDialog):
    """Dialog for creating/editing themes"""
    
    def __init__(self, parent=None, base_theme=None, is_new=False):
        self.base_theme = base_theme
        self.is_new = is_new
        self.color_inputs = {}
        
        if self.is_new and self.base_theme:
            title = f"Customize {self.base_theme.name}"
        elif self.base_theme:
            title = f"Edit {self.base_theme.name}"
        else:
            title = "Create Custom Theme"
        
        super().__init__(parent, title=title, width=500, height=700)
        self.setup_content()
    
    def setup_content(self):
        """Setup dialog content"""
        # Theme name input
        name_layout = QHBoxLayout()
        name_label = QLabel("Theme Name:")
        name_label.setFixedWidth(120)
        name_layout.addWidget(name_label)
        
        self.name_input = QLineEdit()
        if self.base_theme and not self.is_new:
            self.name_input.setText(self.base_theme.name)
        else:
            self.name_input.setPlaceholderText("Enter theme name...")
            if self.base_theme:
                self.name_input.setText(f"{self.base_theme.name} Custom")
        name_layout.addWidget(self.name_input)
        self.layout.addLayout(name_layout)
        
        # Color fields form
        form_widget = QWidget()
        form = QFormLayout(form_widget)
        form.setSpacing(15)
        
        color_fields = [
            ("bg_primary", "Background Primary"),
            ("bg_secondary", "Background Secondary"),
            ("bg_tertiary", "Background Tertiary"),
            ("fg_primary", "Text Primary"),
            ("fg_secondary", "Text Secondary"),
            ("accent", "Accent Color"),
            ("accent_hover", "Accent Hover"),
            ("success", "Success Color"),
            ("warning", "Warning Color"),
            ("danger", "Danger Color"),
            ("border", "Border Color")
        ]
        
        for field, label in color_fields:
            initial_color = getattr(self.base_theme, field) if self.base_theme else "#000000"
            color_input = ColorPickerInput(initial_color)
            self.color_inputs[field] = color_input
            form.addRow(label + ":", color_input)
        
        self.layout.addWidget(form_widget)
        
        # Buttons
        self.add_buttons(save_text="Save", cancel_text="Cancel")
    
    def get_colors(self):
        """Get color values and theme name from inputs"""
        colors = {field: input.get_color() for field, input in self.color_inputs.items()}
        colors['name'] = self.name_input.text().strip()
        return colors


class ColorPickerInput(QWidget):
    """Color picker input widget"""
    
    def __init__(self, initial_color="#000000", parent=None):
        super().__init__(parent)
        self.current_color = initial_color
        self.setup_ui()
    
    def setup_ui(self):
        """Setup color picker UI"""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)
        
        # Color preview
        self.preview = QFrame()
        self.preview.setFixedSize(40, 30)
        self.preview.setStyleSheet(f"""
            QFrame {{
                background-color: {self.current_color};
                border: 1px solid #4d4d4d;
                border-radius: 4px;
            }}
        """)
        layout.addWidget(self.preview)
        
        # Color code input
        self.color_input = QLineEdit()
        self.color_input.setText(self.current_color)
        self.color_input.setFixedWidth(100)
        self.color_input.textChanged.connect(self.on_text_changed)
        layout.addWidget(self.color_input)
        
        # Pick button
        pick_btn = QPushButton("Pick Color")
        pick_btn.clicked.connect(self.on_pick_color)
        layout.addWidget(pick_btn)
        
        layout.addStretch()
        
        self.setLayout(layout)
    
    def on_text_changed(self, text):
        """Handle text input change"""
        if text.startswith('#') and len(text) == 7:
            self.current_color = text
            self.preview.setStyleSheet(f"""
                QFrame {{
                    background-color: {self.current_color};
                    border: 1px solid #4d4d4d;
                    border-radius: 4px;
                }}
            """)
    
    def on_pick_color(self):
        """Open color picker dialog"""
        color = QColorDialog.getColor(
            QColor(self.current_color),
            self,
            "Pick Color"
        )
        
        if color.isValid():
            self.current_color = color.name()
            self.color_input.setText(self.current_color)
            self.preview.setStyleSheet(f"""
                QFrame {{
                    background-color: {self.current_color};
                    border: 1px solid #4d4d4d;
                    border-radius: 4px;
                }}
            """)
    
    def get_color(self):
        """Get current color value"""
        return self.current_color
