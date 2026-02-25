"""
Expenses View
Expense and income tracking
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QLabel, QScrollArea, QFrame, QTabWidget
)
from PyQt6.QtCore import Qt
from datetime import datetime, timedelta

from src.features.expenses.controller import ExpensesController
from src.features.expenses.widgets.expense_item import ExpenseItem
from src.features.expenses.widgets.expense_dialog import ExpenseDialog
from src.features.expenses.widgets.income_dialog import IncomeDialog
from src.shared.formatters import format_currency


class ExpensesView(QWidget):
    """Expenses main view"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.controller = ExpensesController()
        self.setup_ui()
        self.load_data()
    
    def setup_ui(self):
        """Setup expenses UI"""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)
        
        # Header
        header_layout = QHBoxLayout()
        
        from PyQt6.QtGui import QFont
        title = QLabel("💰 Expenses")
        font = QFont()
        font.setPointSize(18)
        font.setBold(True)
        title.setFont(font)
        header_layout.addWidget(title)
        
        header_layout.addStretch()
        
        # Add buttons
        add_income_btn = QPushButton("+ Add Income")
        add_income_btn.clicked.connect(self.on_add_income)
        header_layout.addWidget(add_income_btn)
        
        add_expense_btn = QPushButton("+ Add Expense")
        add_expense_btn.clicked.connect(self.on_add_expense)
        header_layout.addWidget(add_expense_btn)
        
        main_layout.addLayout(header_layout)
        
        # Summary cards
        summary_layout = QHBoxLayout()
        summary_layout.setSpacing(20)
        
        self.income_card = self.create_summary_card("Total Income", format_currency(0), "#28a745")
        self.expense_card = self.create_summary_card("Total Expenses", format_currency(0), "#dc3545")
        self.balance_card = self.create_summary_card("Balance", format_currency(0), "#0078d4")
        
        summary_layout.addWidget(self.income_card)
        summary_layout.addWidget(self.expense_card)
        summary_layout.addWidget(self.balance_card)
        
        main_layout.addLayout(summary_layout)
        
        # Tabs for expenses and income
        self.tabs = QTabWidget()
        
        # Expenses tab
        expenses_tab = QWidget()
        expenses_layout = QVBoxLayout(expenses_tab)
        
        expenses_scroll = QScrollArea()
        expenses_scroll.setWidgetResizable(True)
        expenses_scroll.setFrameShape(QFrame.Shape.NoFrame)
        
        self.expenses_container = QWidget()
        self.expenses_layout = QVBoxLayout(self.expenses_container)
        self.expenses_layout.setSpacing(10)
        self.expenses_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        
        expenses_scroll.setWidget(self.expenses_container)
        expenses_layout.addWidget(expenses_scroll)
        
        self.tabs.addTab(expenses_tab, "Expenses")
        
        # Income tab
        income_tab = QWidget()
        income_layout = QVBoxLayout(income_tab)
        
        income_scroll = QScrollArea()
        income_scroll.setWidgetResizable(True)
        income_scroll.setFrameShape(QFrame.Shape.NoFrame)
        
        self.income_container = QWidget()
        self.income_layout = QVBoxLayout(self.income_container)
        self.income_layout.setSpacing(10)
        self.income_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        
        income_scroll.setWidget(self.income_container)
        income_layout.addWidget(income_scroll)
        
        self.tabs.addTab(income_tab, "Income")
        
        main_layout.addWidget(self.tabs)
        
        self.setLayout(main_layout)
    
    def create_summary_card(self, title: str, value: str, color: str) -> QFrame:
        """Create a summary card"""
        card = QFrame()
        card.setObjectName("summary-card")
        card.setProperty("border-color", color)
        
        layout = QVBoxLayout(card)
        
        title_label = QLabel(title)
        title_label.setProperty("class", "title-text")
        layout.addWidget(title_label)
        
        value_label = QLabel(value)
        value_label.setObjectName("value")
        from PyQt6.QtGui import QFont
        font = QFont()
        font.setPointSize(18)
        font.setBold(True)
        value_label.setFont(font)
        layout.addWidget(value_label)
        
        return card
    
    def load_data(self):
        """Load expenses and income data"""
        # Get current month data
        now = datetime.now()
        start_date = now.replace(day=1)
        
        # Load summary
        summary = self.controller.get_monthly_summary(start_date)
        
        # Update cards
        self.update_card_value(self.income_card, format_currency(summary['income']))
        self.update_card_value(self.expense_card, format_currency(summary['expenses']))
        self.update_card_value(self.balance_card, format_currency(summary['balance']))
        
        # Load expenses
        self.load_expenses()
        
        # Load income
        self.load_income()
    
    def load_expenses(self):
        """Load expenses list"""
        # Clear existing
        for i in reversed(range(self.expenses_layout.count())):
            widget = self.expenses_layout.itemAt(i).widget()
            if widget:
                widget.deleteLater()
        
        expenses = self.controller.get_expenses()
        
        if not expenses:
            empty = QLabel("No expenses yet")
            empty.setProperty("class", "secondary-text")
            empty.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.expenses_layout.addWidget(empty)
        else:
            for expense in expenses:
                item = ExpenseItem(expense, "expense", self)
                item.item_updated.connect(self.on_item_updated)
                item.item_deleted.connect(self.on_item_deleted)
                self.expenses_layout.addWidget(item)
    
    def load_income(self):
        """Load income list"""
        # Clear existing
        for i in reversed(range(self.income_layout.count())):
            widget = self.income_layout.itemAt(i).widget()
            if widget:
                widget.deleteLater()
        
        income = self.controller.get_income()
        
        if not income:
            empty = QLabel("No income yet")
            empty.setProperty("class", "secondary-text")
            empty.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.income_layout.addWidget(empty)
        else:
            for inc in income:
                item = ExpenseItem(inc, "income", self)
                item.item_updated.connect(self.on_item_updated)
                item.item_deleted.connect(self.on_item_deleted)
                self.income_layout.addWidget(item)
    
    def update_card_value(self, card: QFrame, value: str):
        """Update card value"""
        value_label = card.findChild(QLabel, "value")
        if value_label:
            value_label.setText(value)
    
    def on_add_expense(self):
        """Handle add expense"""
        dialog = ExpenseDialog(self)
        if dialog.exec():
            data = dialog.get_data()
            self.controller.create_expense(data)
            self.load_data()
    
    def on_add_income(self):
        """Handle add income"""
        dialog = IncomeDialog(self)
        if dialog.exec():
            data = dialog.get_data()
            self.controller.create_income(data)
            self.load_data()
    
    def on_item_updated(self):
        """Handle item update"""
        self.load_data()
    
    def on_item_deleted(self):
        """Handle item deletion"""
        self.load_data()
    
    def refresh(self):
        """Refresh view to apply config changes"""
        self.load_data()
