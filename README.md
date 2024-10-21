# Expenses Sharing Application

This is a backend application for managing expenses and splitting them among users. It allows users to add expenses and split them based on three different methods: exact amounts, percentages, and equal splits.

## Setup and Installation

1. Clone the repository:
   ```
   git clone https://github.com/chrisvinsonk/expense-sharing.git
   cd daily-expenses-sharing
   ```

2. Create a virtual environment and activate it:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
   ```

3. Install the required packages:
   ```
   pip install -r requirements.txt
   ```

4. Initialize the database:
   ```
   flask db init
   flask db migrate
   flask db upgrade
   ```

5. Run the application:
   ```
   python app.py
   ```

The application will be available at `http://localhost:5000`.

## API Endpoints

### User Endpoints

- Create user: `POST /users`
- Retrieve user details: `GET /users/<user_id>`

### Expense Endpoints

- Add expense: `POST /expenses`
- Retrieve individual user expenses: `GET /expenses/user/<user_id>`
- Retrieve overall expenses: `GET /expenses`
- Download balance sheet as CSV: `GET /balance-sheet`

## Running Tests

To run the test cases, use the following command:

```
pytest test_app.py
```
