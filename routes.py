import logging
from flask import jsonify, request, send_file, make_response
from app import app, db
from models import User, Expense, ExpenseSplit
from utils import validate_percentage_split, generate_balance_sheet
import csv
import io

logging.basicConfig(level=logging.DEBUG)

@app.route('/users', methods=['POST'])
def create_user():
    try:
        data = request.json
        logging.debug(f"Received data: {data}")
        if not data or 'name' not in data or 'email' not in data:
            return jsonify({'error': 'Name and email are required'}), 400

        existing_user = User.query.filter_by(email=data['email']).first()
        if existing_user:
            return jsonify({'error': 'User with this email already exists'}), 400

        new_user = User(name=data['name'], email=data['email'])
        db.session.add(new_user)
        db.session.commit()
        return jsonify({'id': new_user.id, 'name': new_user.name, 'email': new_user.email}), 201
    except Exception as e:
        logging.error(f"Error creating user: {str(e)}")
        db.session.rollback()
        return jsonify({'error': 'Internal server error'}), 500

# ... (rest of the code remains the same)
@app.route('/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    user = User.query.get_or_404(user_id)
    return jsonify({'id': user.id, 'name': user.name, 'email': user.email})

@app.route('/expenses', methods=['POST'])
def add_expense():
    data = request.json
    if not data or 'description' not in data or 'amount' not in data or 'payer_id' not in data or 'split_method' not in data or 'splits' not in data:
        return jsonify({'error': 'Missing required fields'}), 400

    payer = User.query.get_or_404(data['payer_id'])
    
    if data['split_method'] not in ['exact', 'percentage', 'equal']:
        return jsonify({'error': 'Invalid split method'}), 400

    if data['split_method'] == 'percentage' and not validate_percentage_split(data['splits']):
        return jsonify({'error': 'Percentage splits must add up to 100%'}), 400

    new_expense = Expense(description=data['description'], amount=data['amount'], payer_id=payer.id, split_method=data['split_method'])
    db.session.add(new_expense)

    for split in data['splits']:
        user = User.query.get_or_404(split['user_id'])
        if data['split_method'] == 'exact':
            amount = split['amount']
            percentage = None
        elif data['split_method'] == 'percentage':
            amount = data['amount'] * split['percentage'] / 100
            percentage = split['percentage']
        else:  # equal split
            amount = data['amount'] / len(data['splits'])
            percentage = None

        expense_split = ExpenseSplit(expense=new_expense, user=user, amount=amount, percentage=percentage)
        db.session.add(expense_split)

    db.session.commit()
    return jsonify({'id': new_expense.id, 'description': new_expense.description, 'amount': new_expense.amount}), 201

@app.route('/expenses/user/<int:user_id>', methods=['GET'])
def get_user_expenses(user_id):
    user = User.query.get_or_404(user_id)
    expenses = Expense.query.filter_by(payer_id=user_id).all()
    expense_list = [{'id': e.id, 'description': e.description, 'amount': e.amount, 'date': e.date} for e in expenses]
    return jsonify(expense_list)

@app.route('/expenses', methods=['GET'])
def get_all_expenses():
    expenses = Expense.query.all()
    expense_list = [{'id': e.id, 'description': e.description, 'amount': e.amount, 'date': e.date, 'payer': e.payer.name} for e in expenses]
    return jsonify(expense_list)

@app.route('/balance-sheet', methods=['GET'])
def download_balance_sheet():
    balance_sheet = generate_balance_sheet()
    
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['User', 'Balance'])
    for user, balance in balance_sheet.items():
        writer.writerow([user, balance])
    
    output.seek(0)
    response = make_response(send_file(
        io.BytesIO(output.getvalue().encode()),
        mimetype='text/csv',
        as_attachment=True,
        download_name='balance_sheet.csv'
    ))
    response.headers['Content-Type'] = 'text/csv'
    return response