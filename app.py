"""Bank Management System — Streamlit UI."""

import pandas as pd
import streamlit as st

import database as db


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Bank Management System",
    page_icon="🏦",
    layout="wide"
)



# ============================================================
# DATABASE SETUP
# ============================================================

@st.cache_resource
def setup_database():
    db.init_db()
    return True


try:
    setup_database()

except Exception as error:

    st.error(
        f"Could not connect to MySQL: {error}"
    )

    st.info(
        "Make sure MySQL is running and your "
        "database credentials are correct."
    )

    st.stop()


# ============================================================
# SESSION STATE
# ============================================================

if "account_no" not in st.session_state:
    st.session_state.account_no = None


# ============================================================
# HELPER
# ============================================================

def show_result(result):

    success, message = result

    if success:
        st.success(message)
    else:
        st.error(message)

    return success


# ============================================================
# LOGIN / CREATE ACCOUNT
# ============================================================

def auth_page():

    # Header
    st.markdown(
        "<div style='text-align:center;'>"
        "<div style='font-size:48px;'>🏦</div>"
        "<h1>Bank Management System</h1>"
        "<p style='color:#9ca3af;'>"
        "Secure and simple banking management"
        "</p>"
        "</div>",
        unsafe_allow_html=True
    )

    st.write("")

    # Login / Signup tabs
    login_tab, signup_tab = st.tabs(
        ["🔐 Login", "📝 Create Account"]
    )

    # ========================================================
    # LOGIN
    # ========================================================

    with login_tab:

        st.subheader("Welcome Back 👋")

        with st.form("login_form"):

            account_no = st.text_input(
                "Account Number",
                placeholder="Enter your account number",
                max_chars=10
            )

            pin = st.text_input(
                "4-Digit PIN",
                placeholder="Enter your PIN",
                type="password",
                max_chars=4
            )

            login = st.form_submit_button(
                "🔐 Login",
                type="primary",
                use_container_width=True
            )

            if login:

                if not account_no or not pin:

                    st.warning(
                        "Please enter your account number and PIN."
                    )

                else:

                    logged_in_account = db.authenticate(
                        account_no,
                        pin
                    )

                    if logged_in_account:

                        st.session_state.account_no = (
                            logged_in_account
                        )

                        st.rerun()

                    else:

                        st.error(
                            "Invalid account number or PIN."
                        )

    # ========================================================
    # CREATE ACCOUNT
    # ========================================================

    with signup_tab:

        st.subheader("Open a New Account")

        with st.form("signup_form"):

            name = st.text_input(
                "Full Name",
                placeholder="Enter your full name"
            )

            phone = st.text_input(
                "Phone Number",
                placeholder="10-digit phone number",
                max_chars=10
            )

            pin = st.text_input(
                "Create 4-Digit PIN",
                placeholder="Enter a 4-digit PIN",
                type="password",
                max_chars=4
            )

            initial_deposit = st.number_input(
                "Initial Deposit (₹)",
                min_value=0.0,
                step=100.0
            )

            create = st.form_submit_button(
                "📝 Create Account",
                type="primary",
                use_container_width=True
            )

            if create:

                success, message, account_no = (
                    db.create_account(
                        name,
                        phone,
                        pin,
                        initial_deposit
                    )
                )

                if success:

                    st.success(message)

                    st.info(
                        f"Your Account Number is **{account_no}**. "
                        "Please save it for login."
                    )

                else:

                    st.error(message)
# ============================================================
# DASHBOARD
# ============================================================

def dashboard(account):

    st.header(
        f"Welcome, {account['name']} 👋"
    )

    col1, col2, col3 = st.columns(3)

    col1.metric(
        "💰 Available Balance",
        f"₹{account['balance']:,.2f}"
    )

    col2.metric(
        "🏦 Account Number",
        account["account_no"]
    )

    col3.metric(
        "📅 Member Since",
        account["created_at"].strftime("%d %b %Y")
    )

    st.divider()

    st.subheader("📜 Recent Transactions")

    transactions = db.get_transactions(
        account["account_no"],
        limit=5
    )

    if transactions:

        dataframe = pd.DataFrame(
            transactions
        ).drop(
            columns=["id"]
        )

        st.dataframe(
            dataframe,
            use_container_width=True,
            hide_index=True
        )

    else:

        st.info(
            "No transactions yet."
        )


# ============================================================
# DEPOSIT / WITHDRAW
# ============================================================

def money_page(title, label, operation):

    st.header(title)

    with st.form(title):

        amount = st.number_input(
            label,
            min_value=0.0,
            step=100.0
        )

        submit = st.form_submit_button(
            "Submit",
            type="primary"
        )

        if submit:

            result = operation(
                st.session_state.account_no,
                amount
            )

            show_result(result)
# ============================================================
# TRANSFER
# ============================================================

def transfer_page():

    st.header("🔄 Transfer Money")

    with st.form("transfer_form"):

        recipient = st.text_input(
            "Recipient Account Number",
            placeholder="Enter recipient account number"
        )

        amount = st.number_input(
            "Amount (₹)",
            min_value=0.0,
            step=100.0
        )

        submit = st.form_submit_button(
            "💸 Transfer",
            type="primary"
        )

        if submit:

            result = db.transfer(
                st.session_state.account_no,
                recipient,
                amount
            )

            show_result(result)

# ============================================================
# TRANSACTION HISTORY
# ============================================================

def history_page(account):

    st.header("📜 Transaction History")

    transactions = db.get_transactions(
        account["account_no"]
    )

    if not transactions:

        st.info(
            "No transactions yet."
        )

        return

    dataframe = pd.DataFrame(
        transactions
    ).drop(
        columns=["id"]
    )

    transaction_types = dataframe["type"].unique()

    selected_types = st.multiselect(
        "Filter by Transaction Type",
        transaction_types,
        default=list(transaction_types)
    )

    filtered = dataframe[
        dataframe["type"].isin(selected_types)
    ]

    st.dataframe(
        filtered,
        use_container_width=True,
        hide_index=True
    )


# ============================================================
# ACCOUNT DETAILS
# ============================================================

def details_page(account):

    st.header("👤 Account Details")

    col1, col2 = st.columns(2)

    with col1:

        st.write(
            f"**Name:** {account['name']}"
        )

        st.write(
            f"**Phone:** {account['phone']}"
        )

        st.write(
            f"**Account Number:** "
            f"{account['account_no']}"
        )

    with col2:

        st.write(
            f"**Balance:** "
            f"₹{account['balance']:,.2f}"
        )

        st.write(
            f"**Opened On:** "
            f"{account['created_at']:%d %b %Y, %I:%M %p}"
        )


# ============================================================
# MAIN APPLICATION
# ============================================================

if st.session_state.account_no is None:

    auth_page()

else:

    account = db.get_account(
        st.session_state.account_no
    )

    if account is None:

        st.session_state.account_no = None
        st.rerun()

    # --------------------------------------------------------
    # SIDEBAR
    # --------------------------------------------------------

    with st.sidebar:

        st.title("🏦 My Bank")

        st.write(
            f"**{account['name']}**"
        )

        st.caption(
            f"A/C {account['account_no']}"
        )

        st.divider()

        page = st.radio(
            "Menu",
            [
                "Dashboard",
                "Deposit",
                "Withdraw",
                "Transfer",
                "Transaction History",
                "Account Details"
            ]
        )

        st.divider()

        if st.button(
            "🚪 Logout",
            use_container_width=True
        ):

            st.session_state.account_no = None
            st.rerun()

    # --------------------------------------------------------
    # PAGES
    # --------------------------------------------------------

    if page == "Dashboard":

        dashboard(account)

    elif page == "Deposit":

        money_page(
            "➕ Deposit Money",
            "Amount to deposit (₹)",
            db.deposit
        )

    elif page == "Withdraw":

        money_page(
            "➖ Withdraw Money",
            "Amount to withdraw (₹)",
            db.withdraw
        )

    elif page == "Transfer":

        transfer_page()

    elif page == "Transaction History":

        history_page(account)

    elif page == "Account Details":

        details_page(account)