"""
Income Dialog
"""
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout,
    QLineEdit, QTextEdit, QComboBox, QDateEdit,
    QPushButton, QFormLayout, QDoubleSpinBox
)
from PyQt6.QtCore import QDate

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
        
        layout = QVBoxLayout(self)
        
        form = QFormLayout()
        
        # Amount
        self.amount_input = QDoubleSpinBox()
        self.amount_input.setRange(0, 999999999)
        self.amount_input.setDecimals(2)
        
        # Set currency prefix from config
        currency_symbol = config.get('currency.symbol', '₹')
        self.amount_input.setPrefix(f"{currency_symbol} ")
        
        form.addRow("Amount:", self.amount_input)
        
        # Category
        self.category_combo = QComboBox()
        categories = config.get('categories.income', [])
        self.category_combo.addItems(categories)
        form.addRow("Category:", self.category_combo)
        
        # Description
        self.description_input = QTextEdit()
        self.description_input.setMaximumHeight(80)
        form.addRow("Description:", self.description_input)
        
        # Date
        self.date_input = QDateEdit()
        self.date_input.setCalendarPopup(True)
        self.date_input.setDate(QDate.currentDate())
        form.addRow("Date:", self.date_input)
        
        # Source
        self.source_input = QLineEdit()
        self.source_input.setPlaceholderText("Company, Client, etc.")
        form.addRow("Source:", self.source_input)
        
        layout.addLayout(form)
        
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
    
    def load_data(self):
        """Load income data"""
        self.amount_input.setValue(float(self.income.amount))
        self.category_combo.setCurrentText(self.income.category)
        if self.income.description:
            self.description_input.setPlainText(self.income.description)
        self.date_input.setDate(QDate(self.income.date))
        if self.income.source:
            self.source_input.setText(self.income.source)
    
    def get_data(self):
        """Get form data"""
        return {
            'amount': self.amount_input.value(),
            'category': self.category_combo.currentText(),
            'description': self.description_input.toPlainText().strip() or None,
            'date': self.date_input.date().toPyDate(),
            'source': self.source_input.text().strip() or None,
        }
