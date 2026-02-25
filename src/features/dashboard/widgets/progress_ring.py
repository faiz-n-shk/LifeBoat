"""
Progress Ring Widget
Circular progress indicator with animation
"""
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt6.QtCore import Qt, QPropertyAnimation, QEasingCurve, pyqtProperty, QRectF
from PyQt6.QtGui import QPainter, QPen, QColor, QFont


class ProgressRing(QWidget):
    """Animated circular progress ring"""
    
    def __init__(self, title: str = "", parent=None):
        super().__init__(parent)
        self.title = title
        self._progress = 0
        self._target_progress = 0
        self.setMinimumSize(160, 180)
        
        # Setup layout for title
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        layout.addSpacing(160)
        
        if self.title:
            self.title_label = QLabel(self.title)
            font = QFont()
            font.setPointSize(10)
            self.title_label.setFont(font)
            self.title_label.setProperty("class", "secondary-text")
            self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.title_label.setWordWrap(True)
            layout.addWidget(self.title_label)
        
        layout.addStretch()
    
    def set_progress(self, value: float, animate: bool = True):
        """Set progress value (0-100) with optional animation"""
        self._target_progress = max(0, min(100, value))
        
        # Don't update display immediately if animating
        if animate:
            self.animate_progress()
        else:
            self._progress = self._target_progress
            self.update()
    
    def reset_and_animate(self):
        """Reset progress to 0 and animate to target"""
        self._progress = 0
        self.update()
        self.animate_progress()
    
    def animate_progress(self):
        """Animate progress change"""
        from src.core.config import config
        if not config.get('appearance.enable_animations', True):
            self._progress = self._target_progress
            self.update()
            return
        
        # Ensure we start from current progress value
        self.animation = QPropertyAnimation(self, b"progress")
        self.animation.setDuration(1200)
        self.animation.setStartValue(float(self._progress))
        self.animation.setEndValue(float(self._target_progress))
        self.animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        self.animation.start()
    
    @pyqtProperty(float)
    def progress(self):
        return self._progress
    
    @progress.setter
    def progress(self, value):
        self._progress = value
        self.update()
    
    def paintEvent(self, event):
        """Paint the progress ring"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Get theme colors
        from src.core.theme_manager import theme_manager
        from src.models.theme import Theme
        from src.core.database import db
        try:
            db.connect(reuse_if_open=True)
            theme_obj = Theme.get(Theme.name == theme_manager.current_theme)
            bg_color = QColor(theme_obj.bg_tertiary)
            progress_color = QColor(theme_obj.accent)
            text_color = QColor(theme_obj.fg_primary)
            db.close()
        except:
            bg_color = QColor(60, 60, 60, 80)
            progress_color = QColor(100, 150, 255)
            text_color = QColor(255, 255, 255)
        
        # Calculate dimensions for ring only (not including title)
        width = self.width()
        ring_height = 140  # Fixed height for ring area
        size = min(width, ring_height) - 30
        x = (width - size) / 2
        y = (ring_height - size) / 2
        
        rect = QRectF(x, y, size, size)
        
        # Draw background circle
        pen = QPen(bg_color)
        pen.setWidth(10)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(pen)
        painter.drawArc(rect, 90 * 16, -360 * 16)
        
        # Draw progress arc with gradient effect (only if progress > 0)
        if self._progress > 0:
            # Main progress arc
            pen = QPen(progress_color)
            pen.setWidth(10)
            pen.setCapStyle(Qt.PenCapStyle.RoundCap)
            painter.setPen(pen)
            
            span_angle = -int(self._progress * 3.6 * 16)
            painter.drawArc(rect, 90 * 16, span_angle)
            
            # Glow effect
            glow_color = QColor(progress_color)
            glow_color.setAlpha(50)
            pen = QPen(glow_color)
            pen.setWidth(14)
            pen.setCapStyle(Qt.PenCapStyle.RoundCap)
            painter.setPen(pen)
            painter.drawArc(rect, 90 * 16, span_angle)
        
        # Draw percentage text in center
        painter.setPen(text_color)
        font = QFont()
        font.setPointSize(20)
        font.setBold(True)
        painter.setFont(font)
        
        text = f"{int(self._progress)}%"
        text_rect = QRectF(x, y, size, size)
        painter.drawText(text_rect, Qt.AlignmentFlag.AlignCenter, text)
