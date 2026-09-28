# 🏦 Bank Management System

A simple **Bank Management System** built using **Python, Streamlit, and MySQL**.

This project allows users to create a bank account, securely log in using a PIN, manage their balance, transfer money, and view their transaction history.

It was built as a simple full-stack Python project to understand how a frontend application can interact with a MySQL database.

---

## ✨ Features

* 📝 Create a new bank account
* 🔐 Secure login using Account Number and 4-digit PIN
* 💰 Check account balance
* ➕ Deposit money
* ➖ Withdraw money
* 🔄 Transfer money between accounts
* 📜 View transaction history
* 👤 View account details
* 🚪 Logout
* 🔒 PINs are stored as hashed values
* 💾 MySQL database for persistent data storage
* ⚡ Streamlit frontend

---

## 🛠️ Technologies Used

| Technology             | Purpose                         |
| ---------------------- | ------------------------------- |
| Python                 | Backend logic                   |
| Streamlit              | Frontend / User Interface       |
| MySQL                  | Database                        |
| mysql-connector-python | Python–MySQL connection         |
| Pandas                 | Transaction data display        |
| python-dotenv          | Environment variable management |

---

## 📂 Project Structure

```text
bank-management-system/
│
├── app.py              # Streamlit frontend
├── database.py         # MySQL database operations
├── requirements.txt    # Python dependencies
├── .env                # Database credentials (not uploaded)
├── .gitignore          # Files ignored by Git
└── README.md           # Project documentation
```

---

## ⚙️ How It Works

The application follows this basic flow:

```text
User
 │
 ▼
Streamlit Frontend
 │
 ▼
Python Application
 │
 ▼
database.py
 │
 ▼
MySQL Database
```

The Streamlit interface handles user interaction, while `database.py` handles database operations such as creating accounts, depositing money, withdrawing money, and transferring funds.

---

## 🚀 Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/YOUR-USERNAME/bank-management-system.git
```

Move into the project directory:

```bash
cd bank-management-system
```

---

### 2. Create a virtual environment

```bash
python -m venv venv
```

Activate it on Windows:

```bash
venv\Scripts\activate
```

---

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

---

### 4. Configure MySQL

Make sure MySQL is installed and running on your computer.

The application uses:

```text
Host: localhost
Port: 3306
User: root
```

The database will be created automatically when the application starts.

---

### 5. Create the `.env` file

Create a file named:

```text
.env
```

Add your MySQL configuration:

```text
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=YOUR_MYSQL_PASSWORD
```

Replace `YOUR_MYSQL_PASSWORD` with your own MySQL password.

**Never upload your `.env` file to GitHub.**

---

### 6. Run the application

Start Streamlit:

```bash
streamlit run app.py
```

The application will open in your browser.

---

## 🧪 How to Use

### 1. Create an Account

Open the **Create Account** tab and enter:

* Full name
* Phone number
* 4-digit PIN
* Initial deposit

The system generates a unique account number.

---

### 2. Login

Use:

```text
Account Number
+
4-digit PIN
```

to access your account.

---

### 3. Deposit Money

Select **Deposit** from the sidebar.

Enter the amount and submit.

The balance and transaction history are updated in MySQL.

---

### 4. Withdraw Money

Select **Withdraw**.

Enter the amount you want to withdraw.

The system checks whether your account has sufficient balance before completing the withdrawal.

---

### 5. Transfer Money

Select **Transfer**.

Enter:

```text
Recipient Account Number
Amount
```

The system updates both accounts and creates transaction records for the sender and receiver.

---

### 6. Transaction History

The **Transaction History** section displays previous:

* Deposits
* Withdrawals
* Transfers

You can also filter transactions by type.

---

## 🔐 Security

The project includes basic security practices:

* PINs are not stored as plain text.
* PINs are hashed using PBKDF2-HMAC with SHA-256.
* Database credentials are stored in environment variables.
* `.env` is excluded from Git using `.gitignore`.
* Database transactions use commit/rollback handling.
* Account balances are locked during money operations to help prevent conflicting updates.

> This project is intended for educational purposes and is not suitable for handling real banking data.

---

## 🗄️ Database

The application automatically creates:

```text
bank_db
```

with two main tables:

### `accounts`

Stores:

* Account number
* Name
* Phone number
* Hashed PIN
* Balance
* Account creation date

### `transactions`

Stores:

* Transaction ID
* Account number
* Transaction type
* Amount
* Balance after transaction
* Description
* Transaction date

---

## 📸 Application

### Login / Create Account

*Add a screenshot of your login page here.*

### Dashboard

*Add a screenshot of your dashboard here.*

### Transaction History

*Add a screenshot of your transaction history here.*

---

## 🎯 Learning Objectives

This project was created to practice:

* Python programming
* MySQL database management
* CRUD operations
* Database connectivity
* Streamlit UI development
* Authentication
* Password/PIN hashing
* Transactions and rollback
* Git and GitHub

---

## 🔮 Future Improvements

Possible future improvements include:

* 📧 Email notifications
* 📱 OTP verification
* 🧾 Downloadable bank statements
* 📊 Spending analytics
* 👨‍💼 Admin dashboard
* 🔎 Advanced transaction search
* 🎨 Improved banking UI
* ☁️ Cloud deployment

---

## 👨‍💻 Author

**Mohammed Iyaz**

B.Tech Artificial Intelligence & Data Science

---

## 📄 License

This project is created for educational purposes.
