"""
Expense Pie Chart Widget
3D-style pie chart for expense categories
"""
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QHBoxLayout, QScrollArea, QFrame, QGridLayout
from PyQt6.QtCore import Qt, QRectF, QTimer, QSize
from PyQt6.QtGui import QPainter, QColor, QFont, QPen, QBrush, QConicalGradient
import math


class PieChartCanvas(QWidget):
    """Canvas for drawing the pie chart only"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.data = []
        self.total = 0
        self._animation_progress = 0
        self.setMinimumSize(280, 280)
        self.setMaximumHeight(280)
    
    def paintEvent(self, event):
        """Paint the pie chart with 3D effect"""
        if not self.data or self.total == 0:
            self.draw_empty_state()
            return
        
        if self._animation_progress == 0:
            return
        
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        width = self.width()
        height = self.height()
        size = min(width, height) - 40
        x = (width - size) / 2
        y = (height - size) / 2
        
        # Draw 3D shadow layers
        depth = 8
        for d in range(depth, 0, -1):
            offset = d * 2
            shadow_rect = QRectF(x, y + offset, size, size)
            start_angle = 0
            
            for category, amount, color in self.data:
                percentage = amount / self.total
                span_angle = int(360 * percentage * self._animation_progress * 16)
                
                shadow_color = color.darker(150 + d * 10)
                painter.setBrush(QBrush(shadow_color))
                painter.setPen(Qt.PenStyle.NoPen)
                painter.drawPie(shadow_rect, start_angle, span_angle)
                start_angle += span_angle
        
        # Draw main pie chart with conical gradient
        rect = QRectF(x, y, size, size)
        start_angle = 0
        
        for category, amount, color in self.data:
            percentage = amount / self.total
            span_angle = int(360 * percentage * self._animation_progress * 16)
            
            # Create conical gradient for 3D effect
            gradient = QConicalGradient(rect.center(), start_angle / 16)
            gradient.setColorAt(0, color.lighter(120))
            gradient.setColorAt(0.5, color)
            gradient.setColorAt(1, color.darker(120))
            
            painter.setBrush(QBrush(gradient))
            painter.setPen(QPen(QColor(40, 40, 40), 2))
            painter.drawPie(rect, start_angle, span_angle)
            start_angle += span_angle
    
    def draw_empty_state(self):
        """Draw empty state when no data"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Get theme color for text
        from src.core.theme_manager import theme_manager
        from src.models.theme import Theme
        from src.core.database import db
        try:
            db.connect(reuse_if_open=True)
            theme_obj = Theme.get(Theme.name == theme_manager.current_theme)
            text_color = QColor(theme_obj.fg_secondary)
            circle_color = QColor(theme_obj.bg_tertiary)
            db.close()
        except:
            text_color = QColor(150, 150, 150)
            circle_color = QColor(60, 60, 60, 50)
        
        width = self.width()
        height = self.height()
        size = min(width, height) - 40
        x = (width - size) / 2
        y = (height - size) / 2
        
        rect = QRectF(x, y, size, size)
        
        painter.setBrush(QBrush(circle_color))
        painter.setPen(QPen(text_color, 2))
        painter.drawEllipse(rect)
        
        font = QFont()
        font.setPointSize(11)
        painter.setFont(font)
        painter.setPen(text_color)
        
        text_rect = QRectF(0, 0, width, height)
        painter.drawText(text_rect, Qt.AlignmentFlag.AlignCenter, "No expenses\nthis month")


class ExpensePieChart(QWidget):
    """3D-style pie chart for expenses by category with scrollable legend"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.data = []
        self.total = 0
        self.setMinimumSize(300, 450)
        self.current_columns = 1  # Track current column count
        
        # Animation
        self._animation_progress = 0
        self.animation_timer = None
        
        # Setup layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(15)
        
        # Pie chart canvas
        self.canvas = PieChartCanvas()
        layout.addWidget(self.canvas)
        
        # Scrollable legend area
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setFrameShape(QFrame.Shape.NoFrame)
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scroll.setMaximumHeight(140)
        
        # Legend container
        self.legend_widget = QWidget()
        self.legend_layout = QGridLayout(self.legend_widget)
        self.legend_layout.setContentsMargins(8, 0, 8, 0)
        self.legend_layout.setSpacing(8)
        self.legend_layout.setHorizontalSpacing(16)
        
        self.scroll.setWidget(self.legend_widget)
        layout.addWidget(self.scroll)
        
        # Apply styling to scroll area
        self.apply_scroll_styling()
    
    def resizeEvent(self, event):
        """Handle resize to adjust legend columns"""
        super().resizeEvent(event)
        
        # Determine how many columns can fit
        # Minimum width per category item is approximately 200px
        available_width = self.width() - 40  # Account for margins
        
        if available_width >= 450:  # Enough space for 2 columns
            new_columns = 2
        else:  # Only 1 column
            new_columns = 1
        
        # Rebuild legend if column count changed
        if new_columns != self.current_columns:
            self.current_columns = new_columns
            if self.data:
                # Get theme color for text
                from src.core.theme_manager import theme_manager
                from src.models.theme import Theme
                from src.core.database import db
                try:
                    db.connect(reuse_if_open=True)
                    theme_obj = Theme.get(Theme.name == theme_manager.current_theme)
                    text_color = theme_obj.fg_primary
                    db.close()
                except:
                    text_color = "#ffffff"
                
                self.clear_legend()
                self.build_legend(text_color)
    
    def apply_scroll_styling(self):
        """Apply theme-aware styling to scroll area"""
        self.scroll.setStyleSheet("""
            QScrollArea {
                background-color: transparent;
                border: none;
            }
            QWidget {
                background-color: transparent;
            }
        """)
    
    def set_data(self, data: list, animate: bool = True):
        """
        Set chart data
        data: List of (category, amount) tuples
        """
        # Get theme-based colors
        from src.core.theme_manager import theme_manager
        from src.models.theme import Theme
        from src.core.database import db
        
        try:
            db.connect(reuse_if_open=True)
            theme_obj = Theme.get(Theme.name == theme_manager.current_theme)
            accent = theme_obj.accent
            text_color = theme_obj.fg_primary
            db.close()
            
            # Parse accent color
            accent_color = QColor(accent)
            h, s, v, _ = accent_color.getHsv()
            
            # Generate color palette based on theme accent
            colors = []
            for i in range(10):
                # Vary hue around accent color
                new_h = (h + (i * 36)) % 360  # Spread colors around color wheel
                color = QColor.fromHsv(new_h, s, v)
                colors.append(color)
        except:
            # Fallback colors
            colors = [
                QColor(100, 150, 255),  # Blue
                QColor(255, 100, 150),  # Pink
                QColor(150, 255, 100),  # Green
                QColor(255, 200, 100),  # Orange
                QColor(200, 100, 255),  # Purple
                QColor(100, 255, 200),  # Cyan
                QColor(255, 150, 100),  # Coral
                QColor(150, 100, 255),  # Violet
                QColor(255, 255, 100),  # Yellow
                QColor(100, 200, 255),  # Sky Blue
            ]
            text_color = "#ffffff"
        
        # Reset animation progress to 0 FIRST
        self._animation_progress = 0
        
        self.data = []
        self.total = sum(float(amount) for _, amount in data)
        
        for i, (category, amount) in enumerate(data):
            color = colors[i % len(colors)]
            self.data.append((category, float(amount), color))
        
        # Update canvas data
        self.canvas.data = self.data
        self.canvas.total = self.total
        self.canvas._animation_progress = 0
        
        # Clear and rebuild legend
        self.clear_legend()
        self.build_legend(text_color)
        
        # Force repaint to show empty state before animating
        self.canvas.update()
        
        if animate:
            # Small delay before starting animation
            QTimer.singleShot(10, self.animate_chart)
        else:
            self._animation_progress = 1.0
            self.canvas._animation_progress = 1.0
            self.canvas.update()
    
    def clear_legend(self):
        """Clear all legend items"""
        while self.legend_layout.count():
            item = self.legend_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
    
    def build_legend(self, text_color):
        """Build legend with dynamic columns based on available width"""
        from src.shared.formatters import format_currency
        
        row = 0
        col = 0
        
        for category, amount, color in self.data:
            # Create legend item
            item_widget = QWidget()
            item_widget.setStyleSheet("background: transparent;")
            item_layout = QHBoxLayout(item_widget)
            item_layout.setContentsMargins(0, 0, 0, 0)
            item_layout.setSpacing(6)
            
            # Color indicator - circular
            color_box = QLabel()
            color_box.setFixedSize(8, 8)
            color_box.setStyleSheet(f"""
                background-color: {color.name()};
                border-radius: 4px;
                border: none;
            """)
            item_layout.addWidget(color_box, 0, Qt.AlignmentFlag.AlignVCenter)
            
            # Category name and amount
            percentage = (amount / self.total * 100) if self.total > 0 else 0
            text = f"{category}: {format_currency(amount)} ({percentage:.0f}%)"
            
            label = QLabel(text)
            label.setStyleSheet(f"color: {text_color}; background: transparent;")
            font = QFont()
            font.setPointSize(8)
            label.setFont(font)
            item_layout.addWidget(label, 1)
            
            # Add to grid layout using current_columns
            self.legend_layout.addWidget(item_widget, row, col)
            
            col += 1
            if col >= self.current_columns:
                col = 0
                row += 1
        
        # Add stretch at the end
        self.legend_layout.setRowStretch(row + 1, 1)
    
    def animate_chart(self):
        """Animate chart appearance"""
        from src.core.config import config
        if not config.get('appearance.enable_animations', True):
            self._animation_progress = 1.0
            self.canvas._animation_progress = 1.0
            self.canvas.update()
            return
        
        # Ensure we start from 0
        self._animation_progress = 0
        self.canvas._animation_progress = 0
        self.animation_step = 0
        self.canvas.update()
        
        if self.animation_timer:
            self.animation_timer.stop()
        
        self.animation_timer = QTimer()
        self.animation_timer.timeout.connect(self._update_animation)
        self.animation_timer.start(16)  # ~60 FPS
    
    def _update_animation(self):
        """Update animation frame"""
        self.animation_step += 1
        duration = 60  # frames (1 second at 60fps)
        
        # Ease out cubic
        progress = self.animation_step / duration
        self._animation_progress = 1 - pow(1 - progress, 3)
        self.canvas._animation_progress = self._animation_progress
        
        self.canvas.update()
        
        if self.animation_step >= duration:
            self._animation_progress = 1.0
            self.canvas._animation_progress = 1.0
            self.animation_timer.stop()
            self.canvas.update()
    