"""
Goal Item Widget
Individual goal display component
"""
from PyQt6.QtWidgets import (
    QFrame, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton
)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer, QPropertyAnimation, QEasingCurve, QObject, pyqtProperty, QEvent
from PyQt6.QtGui import QFont


class AnimatedProgress(QObject):
    """Helper class for animating progress value"""
    
    progress_changed = pyqtSignal(int)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._progress = 0
    
    @pyqtProperty(int)
    def progress(self):
        return self._progress
    
    @progress.setter
    def progress(self, value):
        self._progress = value
        self.progress_changed.emit(value)


class GoalItem(QFrame):
    """Widget for displaying a single goal"""
    
    edit_requested = pyqtSignal(int)
    delete_requested = pyqtSignal(int)
    toggle_requested = pyqtSignal(int)
    progress_updated = pyqtSignal(int, int)  # goal_id, new_progress
    
    def __init__(self, goal, parent=None):
        super().__init__(parent)
        self.goal = goal
        self._current_progress = 0
        self._target_progress = goal.progress
        self._hold_timer = None
        self._hold_speed = 1
        self._hold_direction = 0  # 1 for increase, -1 for decrease
        self.setup_ui()
        self.animate_progress()
    
    def animate_progress(self):
        """Animate progress bar from 0 to target"""
        from src.core.config import config
        
        if not config.get('appearance.enable_animations', True):
            # No animation, set directly
            self._current_progress = self._target_progress
            self.update_progress_display(self._target_progress)
            return
        
        # Animate from 0 to target
        self.animated_progress = AnimatedProgress(self)
        self.animated_progress.progress_changed.connect(self.update_progress_display)
        
        self.animation = QPropertyAnimation(self.animated_progress, b"progress")
        self.animation.setDuration(800)
        self.animation.setStartValue(0)
        self.animation.setEndValue(self._target_progress)
        self.animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        self.animation.start()
    
    def update_progress_display(self, progress):
        """Update the visual progress bar and percentage"""
        self._current_progress = progress
        
        # Update percentage label
        if hasattr(self, 'progress_percent'):
            self.progress_percent.setText(f"{progress}%")
            
            # Update color based on progress
            if progress >= 100:
                self.progress_percent.setProperty("class", "active-label")
            elif progress >= 75:
                self.progress_percent.setProperty("class", "accent-label")
            else:
                self.progress_percent.setProperty("class", "")
            
            # Force style update
            self.progress_percent.style().unpolish(self.progress_percent)
            self.progress_percent.style().polish(self.progress_percent)
        
        # Update progress bar fill
        if hasattr(self, 'progress_bar_container') and hasattr(self, 'progress_fill'):
            # Account for 2px border (1px on each side)
            container_width = self.progress_bar_container.width() - 2
            
            # Calculate fill width
            if progress >= 100:
                fill_width = container_width
            elif progress > 0:
                fill_width = max(4, int((progress / 100) * container_width))
            else:
                fill_width = 0
            
            # Update geometry (x=1, y=1 to account for border, height=6)
            self.progress_fill.setGeometry(1, 1, fill_width, 6)
            
            # Update color
            from src.core.theme_manager import theme_manager
            theme = theme_manager.get_theme_by_name(theme_manager.get_active_theme())
            if theme:
                if progress >= 100:
                    progress_color = theme.success
                else:
                    progress_color = theme.accent
                
                self.progress_fill.setStyleSheet(f"""
                    QFrame {{
                        background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                            stop:0 {progress_color},
                            stop:1 {theme.accent_hover});
                        border: none;
                        border-radius: 3px;
                    }}
                """)
    
    def setup_ui(self):
        """Setup goal item UI"""
        self.setObjectName("task-item")
        
        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        layout.setContentsMargins(20, 15, 20, 15)
        
        # Header row with title and buttons
        header_row = QHBoxLayout()
        header_row.setSpacing(12)
        
        # Title
        title = QLabel(self.goal.title)
        title.setWordWrap(True)
        font = QFont()
        font.setPointSize(13)
        font.setBold(True)
        title.setFont(font)
        
        if self.goal.completed:
            title.setProperty("class", "secondary-text")
            title.setStyleSheet("text-decoration: line-through;")
        
        header_row.addWidget(title, 1)
        
        # Interactive progress button (hold to increase/decrease)
        progress_btn = QPushButton("⚡")
        progress_btn.setToolTip("Hold Left Click: Increase Progress | Hold Right Click: Decrease Progress")
        progress_btn.setFixedSize(32, 32)
        progress_btn.installEventFilter(self)
        self.progress_btn = progress_btn
        header_row.addWidget(progress_btn)
        
        # Complete button
        complete_btn = QPushButton("✓" if not self.goal.completed else "↻")
        complete_btn.setToolTip("Mark as complete" if not self.goal.completed else "Mark as incomplete")
        complete_btn.setFixedSize(32, 32)
        complete_btn.clicked.connect(lambda: self.toggle_requested.emit(self.goal.id))
        if self.goal.completed:
            complete_btn.setProperty("class", "success-button")
        header_row.addWidget(complete_btn)
        
        layout.addLayout(header_row)
        
        # Progress section with modern styling
        progress_container = QFrame()
        progress_container.setStyleSheet("""
            QFrame {
                background: transparent;
                border: none;
            }
        """)
        progress_layout = QVBoxLayout(progress_container)
        progress_layout.setSpacing(6)
        progress_layout.setContentsMargins(0, 8, 0, 0)
        
        # Progress label and percentage
        progress_header = QHBoxLayout()
        progress_label = QLabel("Progress")
        progress_label.setProperty("class", "meta-text")
        font = QFont()
        font.setPointSize(9)
        progress_label.setFont(font)
        progress_header.addWidget(progress_label)
        
        progress_header.addStretch()
        
        progress_percent = QLabel(f"{self.goal.progress}%")
        font = QFont()
        font.setPointSize(11)
        font.setBold(True)
        progress_percent.setFont(font)
        
        # Color based on progress
        if self.goal.progress >= 100:
            progress_percent.setProperty("class", "active-label")
        elif self.goal.progress >= 75:
            progress_percent.setProperty("class", "accent-label")
        
        progress_header.addWidget(progress_percent)
        progress_layout.addLayout(progress_header)
        
        # Store reference for updates
        self.progress_percent = progress_percent
        
        # Custom progress bar with absolute positioning
        progress_bar_container = QFrame()
        progress_bar_container.setFixedHeight(10)
        progress_bar_container.setMinimumWidth(200)
        
        from src.core.theme_manager import theme_manager
        theme = theme_manager.get_theme_by_name(theme_manager.get_active_theme())
        
        if theme:
            progress_bar_container.setStyleSheet(f"""
                QFrame {{
                    background-color: {theme.bg_tertiary};
                    border: 1px solid {theme.border};
                    border-radius: 4px;
                }}
            """)
            
            # Inner progress fill (positioned absolutely)
            progress_fill = QFrame(progress_bar_container)
            progress_fill.setFixedHeight(6)
            
            # Determine progress color
            if self.goal.progress >= 100:
                progress_color = theme.success
            else:
                progress_color = theme.accent
            
            progress_fill.setStyleSheet(f"""
                QFrame {{
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                        stop:0 {progress_color},
                        stop:1 {theme.accent_hover});
                    border: none;
                    border-radius: 3px;
                }}
            """)
            
            # Store for updates
            self.progress_bar_container = progress_bar_container
            self.progress_fill = progress_fill
        
        progress_layout.addWidget(progress_bar_container)
        layout.addWidget(progress_container)
        
        # Meta info row
        meta_row = QHBoxLayout()
        meta_row.setSpacing(15)
        
        # Category
        if self.goal.category:
            category = QLabel(f"📁 {self.goal.category}")
            category.setProperty("class", "meta-text")
            font = QFont()
            font.setPointSize(9)
            category.setFont(font)
            meta_row.addWidget(category)
        
        # Target date
        if self.goal.target_date:
            from datetime import date
            today = date.today()
            days_left = (self.goal.target_date - today).days
            
            if days_left < 0:
                date_text = f"⏰ Overdue by {abs(days_left)} days"
            elif days_left == 0:
                date_text = "⏰ Due today"
            else:
                date_text = f"📅 {days_left} days left"
            
            target = QLabel(date_text)
            target.setProperty("class", "meta-text")
            font = QFont()
            font.setPointSize(9)
            target.setFont(font)
            meta_row.addWidget(target)
        
        meta_row.addStretch()
        layout.addLayout(meta_row)
        
        # Description (if exists)
        if self.goal.description:
            desc = QLabel(self.goal.description)
            desc.setProperty("class", "secondary-text")
            desc.setWordWrap(True)
            font = QFont()
            font.setPointSize(10)
            desc.setFont(font)
            layout.addWidget(desc)
        
        # Action buttons
        actions_row = QHBoxLayout()
        actions_row.addStretch()
        
        edit_btn = QPushButton("✏ Edit")
        edit_btn.clicked.connect(lambda: self.edit_requested.emit(self.goal.id))
        actions_row.addWidget(edit_btn)
        
        delete_btn = QPushButton("🗑 Delete")
        delete_btn.setProperty("class", "danger-button")
        delete_btn.clicked.connect(lambda: self.delete_requested.emit(self.goal.id))
        actions_row.addWidget(delete_btn)
        
        layout.addLayout(actions_row)
        
        self.setLayout(layout)
    
    def resizeEvent(self, event):
        """Handle resize to update progress bar width"""
        super().resizeEvent(event)
        
        # Update progress display on resize
        if hasattr(self, '_current_progress'):
            self.update_progress_display(self._current_progress)
    
    def eventFilter(self, obj, event):
        """Handle mouse events for progress button"""
        if obj == self.progress_btn:
            if event.type() == QEvent.Type.MouseButtonPress:
                if event.button() == Qt.MouseButton.LeftButton:
                    # Start increasing progress
                    self._hold_direction = 1
                    self._hold_speed = 1
                    self.start_hold_timer()
                    return True
                elif event.button() == Qt.MouseButton.RightButton:
                    # Start decreasing progress
                    self._hold_direction = -1
                    self._hold_speed = 1
                    self.start_hold_timer()
                    return True
            
            elif event.type() == QEvent.Type.MouseButtonRelease:
                # Stop the timer
                self.stop_hold_timer()
                return True
        
        return super().eventFilter(obj, event)
    
    def start_hold_timer(self):
        """Start the hold timer for gradual progress change"""
        if self._hold_timer is None:
            self._hold_timer = QTimer(self)
            self._hold_timer.timeout.connect(self.on_hold_tick)
        
        self._hold_timer.start(50)  # Tick every 50ms
    
    def stop_hold_timer(self):
        """Stop the hold timer and save progress"""
        if self._hold_timer:
            self._hold_timer.stop()
            # Emit signal to save progress
            self.progress_updated.emit(self.goal.id, self._current_progress)
    
    def on_hold_tick(self):
        """Handle each tick of the hold timer"""
        # Gradually increase speed (starts slow, gets faster)
        self._hold_speed = min(self._hold_speed + 0.1, 5)
        
        # Calculate new progress
        new_progress = self._current_progress + (self._hold_direction * self._hold_speed)
        new_progress = max(0, min(100, int(new_progress)))  # Clamp between 0-100
        
        if new_progress != self._current_progress:
            self._current_progress = new_progress
            self._target_progress = new_progress
            self.goal.progress = new_progress
            self.update_progress_display(new_progress)
