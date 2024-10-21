import pytest
from app import app, db
from models import User, Expense, ExpenseSplit
from utils import validate_percentage_split, generate_balance_sheet

@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
    client = app.test_client()

    with app.app_context():
        db.create_all()

    yield client

    with app.app_context():
        db.drop_all()

def test_create_user(client):
    response = client.post('/users', json={'name': 'John Doe', 'email': 'john@example.com'})
    assert response.status_code == 201
    assert 'id' in response.json

def test_get_user(client):
    client.post('/users', json={'name': 'Jane Doe', 'email': 'jane@example.com'})
    response = client.get('/users/1')
    assert response.status_code == 200
    assert response.json['name'] == 'Jane Doe'

def test_add_expense(client):
    client.post('/users', json={'name': 'Alice', 'email': 'alice@example.com'})
    client.post('/users', json={'name': 'Bob', 'email': 'bob@example.com'})
    
    expense_data = {
        'description': 'Lunch',
        'amount': 30,
        'payer_id': 1,
        'split_method': 'equal',
        'splits': [{'user_id': 1}, {'user_id': 2}]
    }
    response = client.post('/expenses', json=expense_data)
    assert response.status_code == 201
    assert 'id' in response.json

def test_get_user_expenses(client):
    client.post('/users', json={'name': 'Charlie', 'email': 'charlie@example.com'})
    client.post('/expenses', json={
        'description': 'Dinner',
        'amount': 50,
        'payer_id': 1,
        'split_method': 'equal',
        'splits': [{'user_id': 1}]
    })
    response = client.get('/expenses/user/1')
    assert response.status_code == 200
    assert len(response.json) == 1

def test_get_all_expenses(client):
    client.post('/users', json={'name': 'David', 'email': 'david@example.com'})
    client.post('/expenses', json={
        'description': 'Movie',
        'amount': 20,
        'payer_id': 1,
        'split_method': 'equal',
        'splits': [{'user_id': 1}]
    })
    response = client.get('/expenses')
    assert response.status_code == 200
    assert len(response.json) == 1

def test_validate_percentage_split():
    valid_splits = [{'percentage': 50}, {'percentage': 50}]
    assert validate_percentage_split(valid_splits) == True

    invalid_splits = [{'percentage': 60}, {'percentage': 50}]
    assert validate_percentage_split(invalid_splits) == False

def test_generate_balance_sheet(client):
    client.post('/users', json={'name': 'Eve', 'email': 'eve@example.com'})
    client.post('/users', json={'name': 'Frank', 'email': 'frank@example.com'})
    client.post('/expenses', json={
        'description': 'Groceries',
        'amount': 100,
        'payer_id': 1,
        'split_method': 'equal',
        'splits': [{'user_id': 1}, {'user_id': 2}]
    })

    with app.app_context():
        balance_sheet = generate_balance_sheet()
        assert balance_sheet['Eve'] == 50
        assert balance_sheet['Frank'] == -50

def test_download_balance_sheet(client):
    client.post('/users', json={'name': 'Grace', 'email': 'grace@example.com'})
    client.post('/users', json={'name': 'Henry', 'email': 'henry@example.com'})
    client.post('/expenses', json={
        'description': 'Utilities',
        'amount': 200,
        'payer_id': 1,
        'split_method': 'equal',
        'splits': [{'user_id': 1}, {'user_id': 2}]
    })

    response = client.get('/balance-sheet')
    assert response.status_code == 200
    assert response.headers['Content-Type'] == 'text/csv'
    assert response.headers['Content-Disposition'] == 'attachment; filename=balance_sheet.csv'