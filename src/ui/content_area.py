"""
Content Area
Displays the active feature module with smooth transitions
"""
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QStackedWidget, QLabel, QGraphicsOpacityEffect
from PyQt6.QtCore import Qt, QPropertyAnimation, QEasingCurve


class ContentArea(QWidget):
    """Content area that displays active feature"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        self.features = {}
        self.current_feature = None
    
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
        from PyQt6.QtGui import QFont
        font = QFont()
        font.setPointSize(18)
        placeholder.setFont(font)
        self.stack.addWidget(placeholder)
        
        self.setLayout(layout)
    
    def register_feature(self, name: str, widget: QWidget):
        """Register a feature widget"""
        self.features[name] = widget
        
        # Only add opacity effect to all features, except settings, as it has its own opacity effects, so qtpainter errors occurs bruh
        if name != "Settings":
            opacity_effect = QGraphicsOpacityEffect()
            opacity_effect.setOpacity(1.0)
            widget.setGraphicsEffect(opacity_effect)
            widget._opacity_effect = opacity_effect
        
        self.stack.addWidget(widget)
    
    def show_feature(self, name: str):
        """Show a specific feature with smooth animation"""
        if name in self.features:
            widget = self.features[name]
            
            # Don't animate if already on this feature
            if self.stack.currentWidget() == widget:
                return
            
            # Check if animations are enabled
            from src.core.config import config
            animations_enabled = config.get('appearance.enable_animations', True)
            
            # Only animate if widget has opacity effect (not Settings)
            if animations_enabled and self.current_feature is not None and hasattr(widget, '_opacity_effect'):
                # Get widgets
                current_widget = self.stack.currentWidget()
                next_widget = widget
                
                # Only animate if current also has opacity effect
                if hasattr(current_widget, '_opacity_effect'):
                    # Ensure next widget starts at full opacity
                    next_widget._opacity_effect.setOpacity(1.0)
                    
                    # Quick fade out current
                    fade_out = QPropertyAnimation(current_widget._opacity_effect, b"opacity")
                    fade_out.setDuration(100)
                    fade_out.setStartValue(1.0)
                    fade_out.setEndValue(0.0)
                    fade_out.setEasingCurve(QEasingCurve.Type.InOutQuad)
                    
                    # Quick fade in next
                    fade_in = QPropertyAnimation(next_widget._opacity_effect, b"opacity")
                    fade_in.setDuration(100)
                    fade_in.setStartValue(0.0)
                    fade_in.setEndValue(1.0)
                    fade_in.setEasingCurve(QEasingCurve.Type.InOutQuad)
                    
                    # Switch widget when fade out completes
                    def on_fade_out_finished():
                        self.stack.setCurrentWidget(widget)
                        # Reset current widget opacity for next time
                        current_widget._opacity_effect.setOpacity(1.0)
                        fade_in.start()
                    
                    fade_out.finished.connect(on_fade_out_finished)
                    fade_out.start()
                    
                    # Store animations to prevent garbage collection
                    self._fade_out = fade_out
                    self._fade_in = fade_in
                else:
                    # Current doesn't have effect, just switch
                    self.stack.setCurrentWidget(widget)
            else:
                # No animation or no opacity effect, just switch
                if hasattr(widget, '_opacity_effect'):
                    widget._opacity_effect.setOpacity(1.0)
                self.stack.setCurrentWidget(widget)
            
            self.current_feature = name
        else:
            print(f"Feature not found: {name}")
    
    def get_feature_widget(self, name: str):
        """Get a feature widget by name"""
        return self.features.get(name)
    
    def refresh_feature(self, name: str):
        """Refresh a specific feature"""
        if name in self.features:
            widget = self.features[name]
            if hasattr(widget, 'refresh'):
                widget.refresh()
            elif hasattr(widget, 'load_data'):
                widget.load_data()
            elif hasattr(widget, 'load_tasks'):
                widget.load_tasks()
            elif hasattr(widget, 'load_calendar'):
                widget.load_calendar()
    
    def refresh_all_features(self):
        """Refresh all registered features to apply config changes"""
        for name, widget in self.features.items():
            # Check if widget has a refresh method
            if hasattr(widget, 'refresh'):
                widget.refresh()
            # Otherwise, try to reload the widget's data
            elif hasattr(widget, 'load_data'):
                widget.load_data()
