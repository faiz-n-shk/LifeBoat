"""
Expense Pie Chart Widget
3D-style pie chart for expense categories
"""
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt6.QtCore import Qt, QRectF, QTimer
from PyQt6.QtGui import QPainter, QColor, QFont, QPen, QBrush, QConicalGradient
import math


class ExpensePieChart(QWidget):
    """3D-style pie chart for expenses by category"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.data = []  # List of (category, amount, color) tuples
        self.total = 0
        self.setMinimumSize(300, 320)
        
        # Animation
        self._animation_progress = 0
        self.animation_timer = None
    
    def set_data(self, data: list, animate: bool = True):
        """
        Set chart data
        data: List of (category, amount) tuples
        """
        # Predefined colors for categories
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
        
        # Reset animation progress to 0 FIRST
        self._animation_progress = 0
        
        self.data = []
        self.total = sum(float(amount) for _, amount in data)
        
        for i, (category, amount) in enumerate(data):
            color = colors[i % len(colors)]
            self.data.append((category, float(amount), color))
        
        # Force repaint to show empty state before animating
        self.update()
        
        if animate:
            # Small delay before starting animation
            QTimer.singleShot(10, self.animate_chart)
        else:
            self._animation_progress = 1.0
            self.update()
    
    def animate_chart(self):
        """Animate chart appearance"""
        from src.core.config import config
        if not config.get('appearance.enable_animations', True):
            self._animation_progress = 1.0
            self.update()
            return
        
        # Ensure we start from 0
        self._animation_progress = 0
        self.animation_step = 0
        self.update()
        
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
        
        self.update()
        
        if self.animation_step >= duration:
            self._animation_progress = 1.0
            self.animation_timer.stop()
            self.update()
    
    def paintEvent(self, event):
        """Paint the pie chart"""
        # Don't draw anything until we have data and animation has started
        if not self.data or self.total == 0:
            self.draw_empty_state()
            return
        
        # Don't draw if animation hasn't started yet
        if self._animation_progress == 0:
            return
        
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Calculate dimensions
        width = self.width()
        height = self.height()
        
        # Chart area (leave space for legend at bottom)
        chart_height = height - 80
        size = min(width - 40, chart_height - 40)
        x = (width - size) / 2
        y = 20
        
        # Draw 3D effect (shadow layers)
        depth = 8
        for d in range(depth, 0, -1):
            offset = d * 2
            shadow_rect = QRectF(x, y + offset, size, size)
            
            start_angle = 0
            for category, amount, color in self.data:
                if self.total == 0:
                    continue
                
                percentage = amount / self.total
                span_angle = int(360 * percentage * self._animation_progress * 16)
                
                # Darker color for shadow
                shadow_color = color.darker(150 + d * 10)
                painter.setBrush(QBrush(shadow_color))
                painter.setPen(Qt.PenStyle.NoPen)
                
                painter.drawPie(shadow_rect, start_angle, span_angle)
                start_angle += span_angle
        
        # Draw main pie chart
        main_rect = QRectF(x, y, size, size)
        start_angle = 0
        
        for category, amount, color in self.data:
            if self.total == 0:
                continue
            
            percentage = amount / self.total
            span_angle = int(360 * percentage * self._animation_progress * 16)
            
            # Create gradient for 3D effect
            gradient = QConicalGradient(main_rect.center(), start_angle / 16)
            gradient.setColorAt(0, color.lighter(120))
            gradient.setColorAt(0.5, color)
            gradient.setColorAt(1, color.darker(120))
            
            painter.setBrush(QBrush(gradient))
            painter.setPen(QPen(QColor(40, 40, 40), 2))
            
            painter.drawPie(main_rect, start_angle, span_angle)
            start_angle += span_angle
        
        # Draw legend at bottom
        self.draw_legend(painter, width, height)
    
    def draw_legend(self, painter, width, height):
        """Draw legend below chart"""
        from src.core.config import config
        currency_symbol = config.get('currency.symbol', '$')
        
        legend_y = height - 70
        legend_x = 10
        
        font = QFont()
        font.setPointSize(9)
        painter.setFont(font)
        
        # Get theme color for text
        from src.core.theme_manager import theme_manager
        from src.models.theme import Theme
        from src.core.database import db
        try:
            db.connect(reuse_if_open=True)
            theme_obj = Theme.get(Theme.name == theme_manager.current_theme)
            text_color = QColor(theme_obj.fg_primary)
            db.close()
        except:
            text_color = QColor(200, 200, 200)
        
        col_width = width / 2
        row = 0
        col = 0
        
        for i, (category, amount, color) in enumerate(self.data[:6]):  # Show max 6 in legend
            x = legend_x + (col * col_width)
            y = legend_y + (row * 25)
            
            # Color box
            painter.setBrush(QBrush(color))
            painter.setPen(QPen(color.darker(150), 1))
            painter.drawRect(int(x), int(y), 12, 12)
            
            # Category name and amount
            percentage = (amount / self.total * 100) if self.total > 0 else 0
            text = f"{category}: {currency_symbol}{amount:.0f} ({percentage:.0f}%)"
            
            painter.setPen(text_color)
            painter.drawText(int(x + 18), int(y + 10), text)
            
            col += 1
            if col >= 2:
                col = 0
                row += 1
    
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
        
        # Draw placeholder circle
        width = self.width()
        height = self.height()
        size = min(width - 40, height - 120)
        x = (width - size) / 2
        y = 20
        
        rect = QRectF(x, y, size, size)
        
        painter.setBrush(QBrush(circle_color))
        painter.setPen(QPen(text_color, 2))
        painter.drawEllipse(rect)
        
        # Draw text
        font = QFont()
        font.setPointSize(11)
        painter.setFont(font)
        painter.setPen(text_color)
        
        y = y + size + 20
        size = 40
        
        text_rect = QRectF(0, y, width, size)
        painter.drawText(text_rect, Qt.AlignmentFlag.AlignCenter, "No expenses\nthis month")
        painter.setFont(font)
        painter.setPen(QColor(150, 150, 150))
        
        text_rect = QRectF(0, y, width, size)
        painter.drawText(text_rect, Qt.AlignmentFlag.AlignCenter, "No expenses\nthis month")
