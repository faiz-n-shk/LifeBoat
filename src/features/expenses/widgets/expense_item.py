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
        
        self.setProperty("class", f"{self.item_type}-item")
        
        main_layout = QHBoxLayout(self)
        
        # Info
        info_layout = QVBoxLayout()
        
        # Category and amount
        header_layout = QHBoxLayout()
        
        from PyQt6.QtGui import QFont
        category_label = QLabel(self.item.category)
        font = QFont()
        font.setPointSize(11)
        font.setBold(True)
        category_label.setFont(font)
        header_layout.addWidget(category_label)
        
        header_layout.addStretch()
        
        amount_label = QLabel(format_currency(self.item.amount))
        font2 = QFont()
        font2.setPointSize(12)
        font2.setBold(True)
        amount_label.setFont(font2)
        amount_label.setStyleSheet(f"color: {color};")
        header_layout.addWidget(amount_label)
        
        info_layout.addLayout(header_layout)
        
        # Description and date
        if self.item.description:
            desc_label = QLabel(self.item.description)
            desc_label.setProperty("class", "meta-text")
            info_layout.addWidget(desc_label)
        
        date_label = QLabel(self.item.date.strftime("%d %B %Y"))
        date_label.setProperty("class", "small-text")
        info_layout.addWidget(date_label)
        
        main_layout.addLayout(info_layout, 1)
        
        # Actions
        actions_layout = QHBoxLayout()
        
        edit_btn = QPushButton("Edit")
        edit_btn.clicked.connect(self.on_edit)
        actions_layout.addWidget(edit_btn)
        
        delete_btn = QPushButton("Delete")
        delete_btn.setProperty("class", "danger-button")
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
