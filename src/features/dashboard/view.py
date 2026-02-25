"""
Dashboard View
Main overview page
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QFrame, QScrollArea
)
from PyQt6.QtCore import Qt


class DashboardView(QWidget):
    """Dashboard main view"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
    
    def setup_ui(self):
        """Setup dashboard UI"""
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)
        
        # Header
        from PyQt6.QtGui import QFont
        header = QLabel("📊 Dashboard")
        font = QFont()
        font.setPointSize(18)
        font.setBold(True)
        header.setFont(font)
        main_layout.addWidget(header)
        
        # Scroll area for content
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        
        # Content widget
        content = QWidget()
        content_layout = QVBoxLayout(content)
        content_layout.setSpacing(20)
        
        # Summary cards row
        cards_layout = QHBoxLayout()
        cards_layout.setSpacing(20)
        
        # Create summary cards with real data
        self.tasks_card = self.create_summary_card("Tasks", "0", "📝")
        self.events_card = self.create_summary_card("Events", "0", "📅")
        self.goals_card = self.create_summary_card("Goals", "0", "🎯")
        self.habits_card = self.create_summary_card("Habits", "0", "🔄")
        
        cards_layout.addWidget(self.tasks_card)
        cards_layout.addWidget(self.events_card)
        cards_layout.addWidget(self.goals_card)
        cards_layout.addWidget(self.habits_card)
        
        content_layout.addLayout(cards_layout)
        
        # Recent activity section
        from PyQt6.QtGui import QFont
        recent_label = QLabel("Recent Activity")
        font = QFont()
        font.setPointSize(14)
        font.setBold(True)
        recent_label.setFont(font)
        content_layout.addWidget(recent_label)
        
        # Placeholder for recent items
        self.recent_placeholder = QLabel("No recent activity")
        self.recent_placeholder.setProperty("class", "secondary-text")
        self.recent_placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
        content_layout.addWidget(self.recent_placeholder)
        
        content_layout.addStretch()
        
        scroll.setWidget(content)
        main_layout.addWidget(scroll)
        
        self.setLayout(main_layout)
        
        # Load real data
        self.load_data()
    
    def load_data(self):
        """Load data from database and update UI"""
        from src.models import Task, Event, Goal, Habit
        from src.core.database import db
        
        try:
            db.connect(reuse_if_open=True)
            
            # Count tasks
            task_count = Task.select().where(Task.completed == False).count()
            self.update_card_value(self.tasks_card, str(task_count))
            
            # Count events
            event_count = Event.select().count()
            self.update_card_value(self.events_card, str(event_count))
            
            # Count goals
            goal_count = Goal.select().where(Goal.completed == False).count()
            self.update_card_value(self.goals_card, str(goal_count))
            
            # Count habits
            habit_count = Habit.select().count()
            self.update_card_value(self.habits_card, str(habit_count))
            
            db.close()
        except Exception as e:
            print(f"Error loading dashboard data: {e}")
    
    def update_card_value(self, card: QFrame, value: str):
        """Update the value in a summary card"""
        # Find the value label (second child in layout)
        layout = card.layout()
        if layout and layout.count() >= 2:
            value_label = layout.itemAt(1).widget()
            if isinstance(value_label, QLabel):
                value_label.setText(value)
    
    def create_summary_card(self, title: str, value: str, icon: str) -> QFrame:
        """Create a summary card widget"""
        card = QFrame()
        card.setObjectName("summary-card")
        
        layout = QVBoxLayout(card)
        layout.setSpacing(10)
        
        # Icon
        from PyQt6.QtGui import QFont
        icon_label = QLabel(icon)
        font = QFont()
        font.setPointSize(24)
        icon_label.setFont(font)
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(icon_label)
        
        # Value
        value_label = QLabel(value)
        font2 = QFont()
        font2.setPointSize(21)
        font2.setBold(True)
        value_label.setFont(font2)
        value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(value_label)
        
        # Title
        title_label = QLabel(title)
        title_label.setProperty("class", "title-text")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)
        
        card.setLayout(layout)
        return card
    
    def refresh(self):
        """Refresh view to apply config changes"""
        self.load_data()
