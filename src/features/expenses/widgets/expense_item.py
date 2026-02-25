"""
Expense/Income Item Widget
"""
from PyQt6.QtWidgets import (
    QFrame, QHBoxLayout, QVBoxLayout, QLabel, QPushButton
)
from PyQt6.QtCore import Qt, pyqtSignal

from src.features.expenses.controller import ExpensesController
from src.shared.formatters import format_currency


class ExpenseItem(QFrame):
    """Widget for displaying expense or income item"""
    
    item_updated = pyqtSignal()
    item_deleted = pyqtSignal()
    
    def __init__(self, item, item_type: str, parent=None):
        super().__init__(parent)
        self.item = item
        self.item_type = item_type  # "expense" or "income"
        self.controller = ExpensesController()
        self.setup_ui()
    
    def setup_ui(self):
        """Setup item UI"""
        color = "#dc3545" if self.item_type == "expense" else "#28a745"
        
        self.setStyleSheet(f"""
            QFrame {{
                background-color: #2d2d2d;
                border: 1px solid #4d4d4d;
                border-left: 4px solid {color};
                border-radius: 8px;
                padding: 15px;
            }}
            QFrame:hover {{
                border-color: #0078d4;
            }}
        """)
        
        main_layout = QHBoxLayout(self)
        
        # Info
        info_layout = QVBoxLayout()
        
        # Category and amount
        header_layout = QHBoxLayout()
        
        category_label = QLabel(self.item.category)
        category_label.setStyleSheet("font-size: 14px; font-weight: bold;")
        header_layout.addWidget(category_label)
        
        header_layout.addStretch()
        
        amount_label = QLabel(format_currency(self.item.amount))
        amount_label.setStyleSheet(f"font-size: 16px; font-weight: bold; color: {color};")
        header_layout.addWidget(amount_label)
        
        info_layout.addLayout(header_layout)
        
        # Description and date
        if self.item.description:
            desc_label = QLabel(self.item.description)
            desc_label.setStyleSheet("font-size: 12px; color: #b0b0b0;")
            info_layout.addWidget(desc_label)
        
        date_label = QLabel(self.item.date.strftime("%d %B %Y"))
        date_label.setStyleSheet("font-size: 11px; color: #616161;")
        info_layout.addWidget(date_label)
        
        main_layout.addLayout(info_layout, 1)
        
        # Actions
        actions_layout = QHBoxLayout()
        
        edit_btn = QPushButton("Edit")
        edit_btn.setFixedWidth(60)
        edit_btn.clicked.connect(self.on_edit)
        actions_layout.addWidget(edit_btn)
        
        delete_btn = QPushButton("Delete")
        delete_btn.setFixedWidth(60)
        delete_btn.setStyleSheet("""
            QPushButton {
                background-color: #dc3545;
            }
            QPushButton:hover {
                background-color: #c82333;
            }
        """)
        delete_btn.clicked.connect(self.on_delete)
        actions_layout.addWidget(delete_btn)
        
        main_layout.addLayout(actions_layout)
    
    def on_edit(self):
        """Handle edit"""
        if self.item_type == "expense":
            from src.features.expenses.widgets.expense_dialog import ExpenseDialog
            dialog = ExpenseDialog(self, self.item)
            if dialog.exec():
                data = dialog.get_data()
                self.controller.update_expense(self.item.id, data)
                self.item_updated.emit()
        else:
            from src.features.expenses.widgets.income_dialog import IncomeDialog
            dialog = IncomeDialog(self, self.item)
            if dialog.exec():
                data = dialog.get_data()
                self.controller.update_income(self.item.id, data)
                self.item_updated.emit()
    
    def on_delete(self):
        """Handle delete"""
        if self.item_type == "expense":
            self.controller.delete_expense(self.item.id)
        else:
            self.controller.delete_income(self.item.id)
        self.item_deleted.emit()
