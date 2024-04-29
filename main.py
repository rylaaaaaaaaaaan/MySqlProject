import sqlite3
from decimal import Decimal

# Define transaction type constants
DEPOSIT = 1
WITHDRAW = 2
TRANSFER = 3

def create_database():
    """Create the database and necessary tables."""
    conn = sqlite3.connect('example.db')
    c = conn.cursor()

    # Create the users table if not exists
    c.execute('''CREATE TABLE IF NOT EXISTS users (
                 account_number INTEGER PRIMARY KEY,
                 pin INTEGER NOT NULL,
                 name VARCHAR(100) NOT NULL,
                 balance DECIMAL(10,2) NOT NULL
                 )''')

    # Create the transactions table if not exists
    c.execute('''CREATE TABLE IF NOT EXISTS transactions (
                 transactions_id INTEGER PRIMARY KEY AUTOINCREMENT,
                 sender_account_number INTEGER,
                 receiver_account_number INTEGER,
                 amount DECIMAL(10,2) NOT NULL,
                 transaction_type INTEGER NOT NULL,
                 transaction_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                 )''')
    conn.commit()
    conn.close()

def add_user(conn, cursor, name, account_number, pin, balance):
    """Add a new user to the users table."""
    insert_statement = "INSERT INTO users (name, account_number, pin, balance) VALUES (?, ?, ?, ?)"
    cursor.execute(insert_statement, (name, account_number, int(pin), balance))
    conn.commit()

def add_transaction(conn, cursor, sender_account_number, receiver_account_number, amount, transaction_type):
    """Add a new transaction to the transactions table."""
    insert_statement = "INSERT INTO transactions (sender_account_number, receiver_account_number, amount, transaction_type) VALUES (?, ?, ?, ?)"
    cursor.execute(insert_statement, (sender_account_number, receiver_account_number, amount, transaction_type))
    conn.commit()

def deposit(conn, cursor, account_number, amount):
    """Deposit funds into a user's account."""
    cursor.execute("UPDATE users SET balance = balance + ? WHERE account_number = ?", (amount, account_number))
    conn.commit()
    add_transaction(conn, cursor, None, account_number, amount, DEPOSIT)

def withdraw(conn, cursor, account_number, amount):
    """Withdraw funds from a user's account."""
    cursor.execute("SELECT balance FROM users WHERE account_number = ?", (account_number,))
    balance = cursor.fetchone()[0]
    if balance < amount:
        print("Insufficient balance.")
        return
    cursor.execute("UPDATE users SET balance = balance - ? WHERE account_number = ?", (amount, account_number))
    conn.commit()
    add_transaction(conn, cursor, account_number, None, amount, WITHDRAW)

def transfer(conn, cursor, sender_account_number, receiver_account_number, amount):
    """Transfer funds from one account to another."""
    cursor.execute("SELECT balance FROM users WHERE account_number = ?", (sender_account_number,))
    sender_balance = cursor.fetchone()[0]
    if sender_balance < amount:
        print("Insufficient balance for transfer.")
        return
    cursor.execute("UPDATE users SET balance = balance - ? WHERE account_number = ?", (amount, sender_account_number))
    cursor.execute("UPDATE users SET balance = balance + ? WHERE account_number = ?", (amount, receiver_account_number))
    conn.commit()
    add_transaction(conn, cursor, sender_account_number, receiver_account_number, amount, TRANSFER)

def perform_transactions(conn, cursor, account_number):
    """Perform various transactions based on user input."""
    while True:
        print("\nChoose a transaction:")
        print("1. Deposit")
        print("2. Withdraw")
        print("3. Transfer")
        print("4. Exit")
        choice = input("Enter your choice: ")
        if choice == "1":
            amount_str = input("Enter the amount to deposit: ")
            try:
                amount = Decimal(amount_str)
                deposit(conn, cursor, account_number, amount)
            except ValueError:
                print("Invalid input for amount. Please enter a valid number.")
        elif choice == "2":
            amount_str = input("Enter the amount to withdraw: ")
            try:
                amount = Decimal(amount_str)
                withdraw(conn, cursor, account_number, amount)
            except ValueError:
                print("Invalid input for amount. Please enter a valid number.")
        elif choice == "3":
            receiver_account_number = int(input("Enter the receiver's account number: "))
            amount_str = input("Enter the amount to transfer: ")
            try:
                amount = Decimal(amount_str)
                transfer(conn, cursor, account_number, receiver_account_number, amount)
            except ValueError:
                print("Invalid input for amount. Please enter a valid number.")
        elif choice == "4":
            break
        else:
            print("Invalid choice. Please enter a valid option.")

def main():
    create_database()
    conn = sqlite3.connect('example.db')
    c = conn.cursor()
    name = input("Enter your username: ")
    account_number = int(input("Enter your account number: "))
    pin = int(input("Enter your PIN: "))
    balance_str = input("Enter your current balance: ")
    try:
        balance = Decimal(balance_str)
        add_user(conn, c, name, account_number, pin, balance)
        perform_transactions(conn, c, account_number)
    except ValueError:
        print("Invalid input for balance. Please enter a valid number.")
    finally:
        c.close()
        conn.close()

if __name__ == '__main__':
    main()
