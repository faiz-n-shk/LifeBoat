"""
Income Dialog
"""
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QTextEdit, QComboBox, QDateEdit,
    QPushButton, QDoubleSpinBox, QTimeEdit
)
from PyQt6.QtCore import QDate, QTime, Qt

from src.core.config import config


class IncomeDialog(QDialog):
    """Dialog for creating/editing income"""
    
    def __init__(self, parent=None, income=None):
        super().__init__(parent)
        self.income = income
        self.is_edit = income is not None
        self.setup_ui()
        
        if self.is_edit:
            self.load_data()
    
    def setup_ui(self):
        """Setup dialog UI"""
        self.setWindowTitle("Edit Income" if self.is_edit else "New Income")
        self.setMinimumWidth(450)
        self.setFixedHeight(550)  # Fixed height to prevent initial scrollbar
        
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Scroll area for content
        from PyQt6.QtWidgets import QScrollArea, QWidget
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QScrollArea.Shape.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        
        # Content widget
        content = QWidget()
        layout = QVBoxLayout(content)
        layout.setSpacing(8)
        layout.setContentsMargins(15, 15, 15, 15)
        
        # Amount
        amount_label = QLabel("Amount:")
        self.amount_input = QDoubleSpinBox()
        self.amount_input.setRange(0, 999999999)
        self.amount_input.setDecimals(2)
        
        # Set currency prefix from config
        currency_symbol = config.get('currency.symbol', '₹')
        self.amount_input.setPrefix(f"{currency_symbol} ")
        
        layout.addWidget(amount_label)
        layout.addWidget(self.amount_input)
        
        # Category
        category_label = QLabel("Category:")
        self.category_combo = QComboBox()
        categories = config.get('categories.income', [])
        self.category_combo.addItems(categories)
        layout.addWidget(category_label)
        layout.addWidget(self.category_combo)
        
        # Description
        desc_label = QLabel("Description:")
        self.description_input = QTextEdit()
        self.description_input.setMinimumHeight(60)
        self.description_input.setMaximumHeight(200)  # Allow expansion up to 200px
        from PyQt6.QtWidgets import QSizePolicy
        self.description_input.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Expanding
        )
        # Force visible border with inline stylesheet
        from src.core.theme_manager import theme_manager
        from src.models.theme import Theme
        from src.core.database import db
        theme = theme_manager.current_theme
        if theme:
            try:
                db.connect(reuse_if_open=True)
                theme_obj = Theme.get(Theme.name == theme)
                self.description_input.setStyleSheet(f"""
                    QTextEdit {{
                        background-color: {theme_obj.bg_secondary};
                        color: {theme_obj.fg_primary};
                        border: 2px solid {theme_obj.border};
                        border-radius: 6px;
                        padding: 8px 12px;
                    }}
                    QTextEdit::corner {{
                        background-color: {theme_obj.bg_tertiary};
                        border: 1px solid {theme_obj.border};
                    }}
                """)
                db.close()
            except:
                pass
        
        # Add resize handle indicator
        desc_container = QVBoxLayout()
        desc_container.setSpacing(0)
        desc_container.addWidget(self.description_input)
        
        # Create a custom resize handle with icon
        from PyQt6.QtGui import QPixmap
        resize_handle = QLabel()
        pixmap = QPixmap("assets/icons/resize-grip.svg")
        resize_handle.setPixmap(pixmap.scaled(16, 16, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
        resize_handle.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignBottom)
        resize_handle.setFixedHeight(20)
        resize_handle.setStyleSheet("padding-right: 5px; padding-bottom: 2px;")
        resize_handle.setCursor(Qt.CursorShape.SizeVerCursor)
        
        # Make description resizable by dragging
        resize_handle.mousePressEvent = lambda e: self.start_resize(e)
        resize_handle.mouseMoveEvent = lambda e: self.do_resize(e)
        
        desc_container.addWidget(resize_handle)
        
        layout.addWidget(desc_label)
        layout.addLayout(desc_container)
        
        # Date and Time row
        datetime_label = QLabel("Date & Time:")
        layout.addWidget(datetime_label)
        
        datetime_row = QHBoxLayout()
        datetime_row.setSpacing(10)
        
        self.date_input = QDateEdit()
        self.date_input.setCalendarPopup(True)
        self.date_input.setDate(QDate.currentDate())
        
        # Apply locale settings for calendar
        self.apply_locale_to_calendar()
        
        datetime_row.addWidget(self.date_input, 1)
        
        self.time_input = QTimeEdit(self)
        self.time_input.setTime(QTime.currentTime())
        
        # Set display format based on config
        time_mode = config.get('datetime.time_mode', '12hr')
        if time_mode == '12hr':
            self.time_input.setDisplayFormat("hh:mm AP")
        else:
            self.time_input.setDisplayFormat("HH:mm")
        
        datetime_row.addWidget(self.time_input, 0)
        
        layout.addLayout(datetime_row)
        
        # Source
        source_label = QLabel("Source:")
        self.source_input = QLineEdit()
        self.source_input.setPlaceholderText("Company, Client, etc.")
        layout.addWidget(source_label)
        layout.addWidget(self.source_input)
        
        # Buttons
        buttons = QHBoxLayout()
        buttons.addStretch()
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        buttons.addWidget(cancel_btn)
        
        save_btn = QPushButton("Save")
        save_btn.clicked.connect(self.accept)
        buttons.addWidget(save_btn)
        
        layout.addLayout(buttons)
        
        # Set content widget and add to scroll area
        scroll.setWidget(content)
        main_layout.addWidget(scroll)
        
        self.setLayout(main_layout)
    
    def load_data(self):
        """Load income data"""
        self.amount_input.setValue(float(self.income.amount))
        self.category_combo.setCurrentText(self.income.category)
        if self.income.description:
            self.description_input.setPlainText(self.income.description)
        self.date_input.setDate(QDate(self.income.date))
        if self.income.time:
            time = QTime(self.income.time)
            self.time_input.setTime(time)
        if self.income.source:
            self.source_input.setText(self.income.source)
    
    def get_data(self):
        """Get form data"""
        time = self.time_input.time()
        time_obj = QTime(time.hour(), time.minute())
        
        return {
            'amount': self.amount_input.value(),
            'category': self.category_combo.currentText(),
            'description': self.description_input.toPlainText().strip() or None,
            'date': self.date_input.date().toPyDate(),
            'time': time_obj.toPyTime(),
            'source': self.source_input.text().strip() or None,
        }
    
    def apply_locale_to_calendar(self):
        """Apply locale settings to calendar widget"""
        from PyQt6.QtCore import Qt
        
        # Get week start setting
        week_start = config.get('datetime.week_start', 'Monday')
        
        # Get the calendar widget
        calendar = self.date_input.calendarWidget()
        if calendar:
            if week_start == 'Sunday':
                calendar.setFirstDayOfWeek(Qt.DayOfWeek.Sunday)
            else:
                calendar.setFirstDayOfWeek(Qt.DayOfWeek.Monday)
    
    def start_resize(self, event):
        """Start resizing description box"""
        self.resize_start_y = event.globalPosition().y()
        self.resize_start_height = self.description_input.height()
    
    def do_resize(self, event):
        """Resize description box"""
        if hasattr(self, 'resize_start_y'):
            delta = event.globalPosition().y() - self.resize_start_y
            new_height = max(60, min(200, self.resize_start_height + delta))
            self.description_input.setFixedHeight(int(new_height))
