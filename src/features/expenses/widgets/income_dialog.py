"""
Income Dialog
"""
from PyQt6.QtWidgets import QLabel, QComboBox, QDoubleSpinBox, QLineEdit
from PyQt6.QtCore import QTime

from src.core.config import config
from src.shared.dialogs import BaseDialog


class IncomeDialog(BaseDialog):
    """Dialog for creating/editing income"""
    
    def __init__(self, parent=None, income=None):
        self.income = income
        self.is_edit = income is not None
        
        title = "Edit Income" if self.is_edit else "New Income"
        super().__init__(parent, title=title, width=450, height=550)
        
        self.setup_fields()
        
        if self.is_edit:
            self.load_data()
    
    def setup_fields(self):
        """Setup income-specific fields"""
        # Amount
        amount_label = QLabel("Amount:")
        self.amount_input = QDoubleSpinBox()
        self.amount_input.setRange(0, 999999999)
        
        # Get decimal places from config
        decimal_places = config.get('currency.decimal_places', 2)
        self.amount_input.setDecimals(decimal_places)
        
        # Set currency symbol and position from config
        currency_symbol = config.get('currency.symbol', '₹')
        currency_position = config.get('currency.position', 'prefix')
        
        if currency_position == 'prefix':
            self.amount_input.setPrefix(f"{currency_symbol} ")
            self.amount_input.setSuffix("")
        else:  # suffix
            self.amount_input.setPrefix("")
            self.amount_input.setSuffix(f" {currency_symbol}")
        
        self.layout.addWidget(amount_label)
        self.layout.addWidget(self.amount_input)
        
        # Category
        category_label = QLabel("Category:")
        self.category_combo = QComboBox()
        categories = config.get('categories.income', [])
        self.category_combo.addItems(categories)
        self.layout.addWidget(category_label)
        self.layout.addWidget(self.category_combo)
        
        # Description
        self.add_description_field()
        
        # Date and time
        self.add_date_time_field()
        
        # Source
        source_label = QLabel("Source:")
        self.source_input = QLineEdit()
        self.source_input.setPlaceholderText("Income source (optional)")
        self.layout.addWidget(source_label)
        self.layout.addWidget(self.source_input)
        
        # Buttons
        save_text = "Save" if self.is_edit else "Add Income"
        self.add_buttons(save_text=save_text, on_save=self.on_save)
    
    def load_data(self):
        """Load income data into form"""
        self.amount_input.setValue(float(self.income.amount))
        self.category_combo.setCurrentText(self.income.category)
        if self.income.description:
            self.description_input.setPlainText(self.income.description)
        
        # Set date
        self.date_input.setDate(self.income.date)
        
        # Set time
        if self.income.time:
            time = QTime(self.income.time)
            self.time_input.setTime(time)
        
        if self.income.source:
            self.source_input.setText(self.income.source)
    
    def on_save(self):
        """Validate and save"""
        if self.amount_input.value() <= 0:
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.warning(self, "Validation Error", "Please enter a valid amount.")
            return
        
        self.accept()
    
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
            'source': self.source_input.text().strip() or None
        }
