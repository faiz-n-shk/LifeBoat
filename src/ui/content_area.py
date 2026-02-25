"""
Content Area
Displays the active feature module
"""
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QStackedWidget, QLabel
from PyQt6.QtCore import Qt


class ContentArea(QWidget):
    """Content area that displays active feature"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        self.features = {}
    
    def setup_ui(self):
        """Setup content area UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Stacked widget to switch between features
        self.stack = QStackedWidget()
        layout.addWidget(self.stack)
        
        # Default placeholder
        placeholder = QLabel("Select a feature from the sidebar")
        placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
        placeholder.setProperty("class", "secondary-text")
        placeholder.setStyleSheet("font-size: 18px;")
        self.stack.addWidget(placeholder)
        
        self.setLayout(layout)
    
    def register_feature(self, name: str, widget: QWidget):
        """Register a feature widget"""
        self.features[name] = widget
        self.stack.addWidget(widget)
    
    def show_feature(self, name: str):
        """Show a specific feature"""
        if name in self.features:
            widget = self.features[name]
            self.stack.setCurrentWidget(widget)
        else:
            print(f"Feature not found: {name}")
    
    def refresh_all_features(self):
        """Refresh all registered features to apply config changes"""
        for name, widget in self.features.items():
            # Check if widget has a refresh method
            if hasattr(widget, 'refresh'):
                widget.refresh()
            # Otherwise, try to reload the widget's data
            elif hasattr(widget, 'load_data'):
                widget.load_data()
