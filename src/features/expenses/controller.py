"""
Expenses Controller
Business logic for expenses and income
"""
from typing import List, Dict, Any
from datetime import datetime, date
from peewee import DoesNotExist

from src.models.expense import Expense, Income
from src.core.database import db
from src.core.activity_logger import activity_logger
from src.core.exceptions import RecordNotFoundError, DatabaseError


class ExpensesController:
    """Controller for expenses and income operations"""
    
    def get_expenses(self, start_date: date = None, end_date: date = None) -> List[Expense]:
        """Get expenses within date range"""
        try:
            db.connect(reuse_if_open=True)
            
            query = Expense.select().order_by(Expense.date.desc(), Expense.created_at.desc())
            
            if start_date:
                query = query.where(Expense.date >= start_date)
            if end_date:
                query = query.where(Expense.date <= end_date)
            
            return list(query)
        except Exception as e:
            raise DatabaseError(f"Failed to retrieve expenses: {str(e)}")
        finally:
            db.close()
    
    def get_income(self, start_date: date = None, end_date: date = None) -> List[Income]:
        """Get income within date range"""
        try:
            db.connect(reuse_if_open=True)
            
            query = Income.select().order_by(Income.date.desc(), Income.created_at.desc())
            
            if start_date:
                query = query.where(Income.date >= start_date)
            if end_date:
                query = query.where(Income.date <= end_date)
            
            return list(query)
        except Exception as e:
            raise DatabaseError(f"Failed to retrieve income: {str(e)}")
        finally:
            db.close()
    
    def get_monthly_summary(self, month_start: datetime) -> Dict[str, float]:
        """Get monthly summary"""
        try:
            db.connect(reuse_if_open=True)
            
            # Calculate month end
            if month_start.month == 12:
                month_end = month_start.replace(year=month_start.year + 1, month=1, day=1)
            else:
                month_end = month_start.replace(month=month_start.month + 1, day=1)
            
            # Get expenses
            expenses = Expense.select().where(
                (Expense.date >= month_start.date()) &
                (Expense.date < month_end.date())
            )
            total_expenses = sum(e.amount for e in expenses)
            
            # Get income
            income = Income.select().where(
                (Income.date >= month_start.date()) &
                (Income.date < month_end.date())
            )
            total_income = sum(i.amount for i in income)
            
            return {
                'expenses': float(total_expenses),
                'income': float(total_income),
                'balance': float(total_income - total_expenses)
            }
        except Exception as e:
            raise DatabaseError(f"Failed to get monthly summary: {str(e)}")
        finally:
            db.close()
    
    def create_expense(self, data: Dict[str, Any]) -> Expense:
        """Create expense"""
        try:
            db.connect(reuse_if_open=True)
            expense = Expense.create(**data)
            activity_logger.log("Expenses", "created", f"{data.get('category', 'Expense')} - {data.get('amount', 0)}")
            return expense
        except Exception as e:
            raise DatabaseError(f"Failed to create expense: {str(e)}")
        finally:
            db.close()
    
    def create_income(self, data: Dict[str, Any]) -> Income:
        """Create income"""
        try:
            db.connect(reuse_if_open=True)
            income = Income.create(**data)
            activity_logger.log("Expenses", "created income", f"{data.get('source', 'Income')} - {data.get('amount', 0)}")
            return income
        except Exception as e:
            raise DatabaseError(f"Failed to create income: {str(e)}")
        finally:
            db.close()
    
    def update_expense(self, expense_id: int, data: Dict[str, Any]) -> bool:
        """Update expense"""
        try:
            db.connect(reuse_if_open=True)
            expense = Expense.get_by_id(expense_id)
            for key, value in data.items():
                setattr(expense, key, value)
            expense.save()
            activity_logger.log("Expenses", "updated", f"{data.get('category', 'Expense')} - {data.get('amount', 0)}")
            return True
        except DoesNotExist:
            raise RecordNotFoundError("Expense not found or has been deleted")
        except Exception as e:
            raise DatabaseError(f"Failed to update expense: {str(e)}")
        finally:
            db.close()
    
    def update_income(self, income_id: int, data: Dict[str, Any]) -> bool:
        """Update income"""
        try:
            db.connect(reuse_if_open=True)
            income = Income.get_by_id(income_id)
            for key, value in data.items():
                setattr(income, key, value)
            income.save()
            activity_logger.log("Expenses", "updated income", f"{data.get('source', 'Income')} - {data.get('amount', 0)}")
            return True
        except DoesNotExist:
            raise RecordNotFoundError("Income not found or has been deleted")
        except Exception as e:
            raise DatabaseError(f"Failed to update income: {str(e)}")
        finally:
            db.close()
    
    def delete_expense(self, expense_id: int) -> bool:
        """Delete expense"""
        try:
            db.connect(reuse_if_open=True)
            expense = Expense.get_by_id(expense_id)
            category = expense.category
            amount = expense.amount
            expense.delete_instance()
            activity_logger.log("Expenses", "deleted", f"{category} - {amount}")
            return True
        except DoesNotExist:
            raise RecordNotFoundError("Expense not found or has been deleted")
        except Exception as e:
            raise DatabaseError(f"Failed to delete expense: {str(e)}")
        finally:
            db.close()
    
    def delete_income(self, income_id: int) -> bool:
        """Delete income"""
        try:
            db.connect(reuse_if_open=True)
            income = Income.get_by_id(income_id)
            source = income.source
            amount = income.amount
            income.delete_instance()
            activity_logger.log("Expenses", "deleted income", f"{source} - {amount}")
            return True
        except DoesNotExist:
            raise RecordNotFoundError("Income not found or has been deleted")
        except Exception as e:
            raise DatabaseError(f"Failed to delete income: {str(e)}")
        finally:
            db.close()
