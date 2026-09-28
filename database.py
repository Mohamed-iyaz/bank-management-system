"""Database layer for the Bank Management System."""

import os
import hashlib
import secrets
from contextlib import contextmanager
from decimal import Decimal, InvalidOperation

import mysql.connector

from dotenv import load_dotenv

load_dotenv()

# ============================================================
# DATABASE CONFIGURATION
# ============================================================

DB_NAME = "bank_db"

DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "port": int(os.getenv("DB_PORT", "3306")),
    "user": os.getenv("DB_USER", "root"),
    "password": os.getenv("DB_PASSWORD", ""),
}


# ============================================================
# DATABASE CONNECTION
# ============================================================

def connect(use_database=True):
    config = DB_CONFIG.copy()

    if use_database:
        config["database"] = DB_NAME

    return mysql.connector.connect(**config)


@contextmanager
def db_cursor():
    """Create a database connection and handle transactions."""

    connection = connect()
    cursor = connection.cursor(dictionary=True)

    try:
        yield cursor
        connection.commit()

    except Exception:
        connection.rollback()
        raise

    finally:
        cursor.close()
        connection.close()


# ============================================================
# DATABASE INITIALIZATION
# ============================================================

def init_db():
    """Create database and tables if they don't exist."""

    connection = connect(use_database=False)
    cursor = connection.cursor()

    # Create database
    cursor.execute(
        f"CREATE DATABASE IF NOT EXISTS `{DB_NAME}`"
    )

    cursor.execute(
        f"USE `{DB_NAME}`"
    )

    # Accounts table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS accounts (
            account_no INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            phone VARCHAR(15) NOT NULL UNIQUE,
            pin_hash VARCHAR(200) NOT NULL,
            balance DECIMAL(15,2) NOT NULL DEFAULT 0.00,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        ) AUTO_INCREMENT = 1001000
    """)

    # Transactions table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS transactions (
            id INT AUTO_INCREMENT PRIMARY KEY,
            account_no INT NOT NULL,
            type ENUM(
                'DEPOSIT',
                'WITHDRAW',
                'TRANSFER_OUT',
                'TRANSFER_IN'
            ) NOT NULL,
            amount DECIMAL(15,2) NOT NULL,
            balance_after DECIMAL(15,2) NOT NULL,
            description VARCHAR(200),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

            FOREIGN KEY (account_no)
            REFERENCES accounts(account_no)
        )
    """)

    connection.commit()

    cursor.close()
    connection.close()


# ============================================================
# PIN SECURITY
# ============================================================

def hash_pin(pin, salt=None):
    """Hash a PIN before storing it."""

    salt = salt or secrets.token_hex(16)

    hashed = hashlib.pbkdf2_hmac(
        "sha256",
        pin.encode(),
        salt.encode(),
        100_000
    ).hex()

    return f"{salt}${hashed}"


def verify_pin(pin, stored_hash):
    """Verify entered PIN against stored hash."""

    salt, _ = stored_hash.split("$")

    new_hash = hash_pin(pin, salt)

    return secrets.compare_digest(
        new_hash,
        stored_hash
    )


# ============================================================
# AMOUNT VALIDATION
# ============================================================

def validate_amount(value):
    try:
        amount = Decimal(str(value)).quantize(
            Decimal("0.01")
        )

    except InvalidOperation:
        return None

    if amount <= 0:
        return None

    return amount


# ============================================================
# CREATE ACCOUNT
# ============================================================

def create_account(name, phone, pin, initial_deposit=0):

    name = name.strip()
    phone = phone.strip()
    pin = pin.strip()

    # Basic validation
    if not name:
        return False, "Please enter your name.", None

    if not phone.isdigit() or len(phone) != 10:
        return False, "Phone number must contain exactly 10 digits.", None

    if not pin.isdigit() or len(pin) != 4:
        return False, "PIN must be exactly 4 digits.", None

    try:
        initial = Decimal(
            str(initial_deposit or 0)
        ).quantize(Decimal("0.01"))

    except InvalidOperation:
        return False, "Invalid initial deposit.", None

    if initial < 0:
        return False, "Initial deposit cannot be negative.", None

    try:

        with db_cursor() as cursor:

            cursor.execute(
                """
                INSERT INTO accounts
                (name, phone, pin_hash, balance)
                VALUES (%s, %s, %s, %s)
                """,
                (
                    name,
                    phone,
                    hash_pin(pin),
                    initial
                )
            )

            account_no = cursor.lastrowid

            # Record initial deposit
            if initial > 0:

                cursor.execute(
                    """
                    INSERT INTO transactions
                    (
                        account_no,
                        type,
                        amount,
                        balance_after,
                        description
                    )
                    VALUES
                    (%s, 'DEPOSIT', %s, %s, %s)
                    """,
                    (
                        account_no,
                        initial,
                        initial,
                        "Initial deposit"
                    )
                )

        return (
            True,
            "Account created successfully!",
            account_no
        )

    except mysql.connector.IntegrityError:

        return (
            False,
            "This phone number is already registered.",
            None
        )


# ============================================================
# LOGIN
# ============================================================

def authenticate(account_no, pin):

    try:
        account_no = int(account_no)

    except (TypeError, ValueError):
        return None

    with db_cursor() as cursor:

        cursor.execute(
            """
            SELECT *
            FROM accounts
            WHERE account_no = %s
            """,
            (account_no,)
        )

        account = cursor.fetchone()

    if account:

        if verify_pin(
            pin,
            account["pin_hash"]
        ):
            return account["account_no"]

    return None


# ============================================================
# GET ACCOUNT
# ============================================================

def get_account(account_no):

    with db_cursor() as cursor:

        cursor.execute(
            """
            SELECT
                account_no,
                name,
                phone,
                balance,
                created_at
            FROM accounts
            WHERE account_no = %s
            """,
            (account_no,)
        )

        return cursor.fetchone()


# ============================================================
# LOCK ACCOUNT BALANCE
# ============================================================

def lock_balance(cursor, account_no):

    cursor.execute(
        """
        SELECT balance
        FROM accounts
        WHERE account_no = %s
        FOR UPDATE
        """,
        (account_no,)
    )

    row = cursor.fetchone()

    if row:
        return row["balance"]

    return None


# ============================================================
# TRANSACTION LOG
# ============================================================

def log_transaction(
    cursor,
    account_no,
    transaction_type,
    amount,
    balance_after,
    description
):

    cursor.execute(
        """
        INSERT INTO transactions
        (
            account_no,
            type,
            amount,
            balance_after,
            description
        )
        VALUES (%s, %s, %s, %s, %s)
        """,
        (
            account_no,
            transaction_type,
            amount,
            balance_after,
            description
        )
    )


# ============================================================
# DEPOSIT
# ============================================================

def deposit(account_no, amount):

    amount = validate_amount(amount)

    if amount is None:
        return False, "Enter an amount greater than zero."

    with db_cursor() as cursor:

        balance = lock_balance(
            cursor,
            account_no
        )

        if balance is None:
            return False, "Account not found."

        new_balance = balance + amount

        cursor.execute(
            """
            UPDATE accounts
            SET balance = %s
            WHERE account_no = %s
            """,
            (
                new_balance,
                account_no
            )
        )

        log_transaction(
            cursor,
            account_no,
            "DEPOSIT",
            amount,
            new_balance,
            "Cash deposit"
        )

    return (
        True,
        f"Deposited ₹{amount:,.2f}. "
        f"New balance: ₹{new_balance:,.2f}"
    )


# ============================================================
# WITHDRAW
# ============================================================

def withdraw(account_no, amount):

    amount = validate_amount(amount)

    if amount is None:
        return False, "Enter an amount greater than zero."

    with db_cursor() as cursor:

        balance = lock_balance(
            cursor,
            account_no
        )

        if balance is None:
            return False, "Account not found."

        if amount > balance:
            return False, "Insufficient balance."

        new_balance = balance - amount

        cursor.execute(
            """
            UPDATE accounts
            SET balance = %s
            WHERE account_no = %s
            """,
            (
                new_balance,
                account_no
            )
        )

        log_transaction(
            cursor,
            account_no,
            "WITHDRAW",
            amount,
            new_balance,
            "Cash withdrawal"
        )

    return (
        True,
        f"Withdrew ₹{amount:,.2f}. "
        f"New balance: ₹{new_balance:,.2f}"
    )


# ============================================================
# TRANSFER
# ============================================================

def transfer(from_account, to_account, amount):

    amount = validate_amount(amount)

    if amount is None:
        return False, "Enter an amount greater than zero."

    try:
        to_account = int(to_account)

    except (TypeError, ValueError):
        return False, "Enter a valid recipient account number."

    if to_account == from_account:
        return False, "You cannot transfer money to yourself."

    with db_cursor() as cursor:

        account_numbers = sorted(
            [from_account, to_account]
        )

        balances = {}

        for account_no in account_numbers:

            balances[account_no] = lock_balance(
                cursor,
                account_no
            )

        # Check recipient
        if balances[to_account] is None:
            return False, "Recipient account not found."

        # Check sender
        if balances[from_account] is None:
            return False, "Your account was not found."

        # Check balance
        if amount > balances[from_account]:
            return False, "Insufficient balance."

        sender_balance = (
            balances[from_account] - amount
        )

        receiver_balance = (
            balances[to_account] + amount
        )

        # Update sender
        cursor.execute(
            """
            UPDATE accounts
            SET balance = %s
            WHERE account_no = %s
            """,
            (
                sender_balance,
                from_account
            )
        )

        # Update receiver
        cursor.execute(
            """
            UPDATE accounts
            SET balance = %s
            WHERE account_no = %s
            """,
            (
                receiver_balance,
                to_account
            )
        )

        # Sender transaction
        log_transaction(
            cursor,
            from_account,
            "TRANSFER_OUT",
            amount,
            sender_balance,
            f"Transfer to {to_account}"
        )

        # Receiver transaction
        log_transaction(
            cursor,
            to_account,
            "TRANSFER_IN",
            amount,
            receiver_balance,
            f"Transfer from {from_account}"
        )

    return (
        True,
        f"Transferred ₹{amount:,.2f} "
        f"to account {to_account}. "
        f"New balance: ₹{sender_balance:,.2f}"
    )


# ============================================================
# TRANSACTION HISTORY
# ============================================================

def get_transactions(account_no, limit=200):

    with db_cursor() as cursor:

        cursor.execute(
            """
            SELECT
                id,
                created_at,
                type,
                amount,
                balance_after,
                description
            FROM transactions
            WHERE account_no = %s
            ORDER BY id DESC
            LIMIT %s
            """,
            (
                account_no,
                limit
            )
        )

        return cursor.fetchall()