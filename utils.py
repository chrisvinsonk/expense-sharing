from models import User, Expense, ExpenseSplit
from app import db

def validate_percentage_split(splits):
    total_percentage = sum(split['percentage'] for split in splits)
    return abs(total_percentage - 100) < 0.01  # Allow for small floating-point errors

def generate_balance_sheet():
    users = User.query.all()
    balance_sheet = {user.name: 0 for user in users}

    expenses = Expense.query.all()
    for expense in expenses:
        balance_sheet[expense.payer.name] += expense.amount
        for split in expense.splits:
            balance_sheet[split.user.name] -= split.amount

    return balance_sheet