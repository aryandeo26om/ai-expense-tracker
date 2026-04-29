import streamlit as st
import sqlite3
import pandas as pd
from model import predict_expense
from werkzeug.security import generate_password_hash, check_password_hash

st.set_page_config(page_title="FinTrack Pro", layout="wide")

# ---------------- DB ----------------
def get_db():
    return sqlite3.connect("database.db", check_same_thread=False)

conn = get_db()

# ---------------- SESSION ----------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = ""
if "user_id" not in st.session_state:
    st.session_state.user_id = None

# ---------------- AUTH ----------------
def login():
    st.title("🔐 Login")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        if not username or not password:
            st.error("Enter all fields")
            return

        user = conn.execute(
            "SELECT * FROM users WHERE username=?",
            (username,)
        ).fetchone()

        if user and check_password_hash(user[2], password):
            st.session_state.logged_in = True
            st.session_state.user_id = user[0]
            st.session_state.username = user[1]
            st.success("Login successful")
            st.rerun()
        else:
            st.error("Invalid credentials")


def register():
    st.title("📝 Register")

    username = st.text_input("New Username")
    password = st.text_input("New Password", type="password")

    if st.button("Register"):
        if not username or not password:
            st.error("Enter valid details")
            return

        existing = conn.execute(
            "SELECT * FROM users WHERE username=?",
            (username,)
        ).fetchone()

        if existing:
            st.error("Username already exists")
            return

        conn.execute(
            "INSERT INTO users (username, password) VALUES (?, ?)",
            (username, generate_password_hash(password))
        )
        conn.commit()

        st.success("Account created! Now login.")

# ---------------- LOGIN FLOW ----------------
if not st.session_state.logged_in:
    menu = st.sidebar.selectbox("Menu", ["Login", "Register"])

    if menu == "Login":
        login()
    else:
        register()

    st.stop()

# ---------------- SIDEBAR ----------------
st.sidebar.title(f"👋 {st.session_state.username}")

menu = st.sidebar.selectbox(
    "Navigation",
    ["Dashboard", "Add Expense", "Analytics", "Manage Data", "Logout"]
)

# ---------------- DASHBOARD ----------------
if menu == "Dashboard":
    st.title("📊 Dashboard")

    data = conn.execute(
        "SELECT * FROM expenses WHERE user_id=?",
        (st.session_state.user_id,)
    ).fetchall()

    if data:
        df = pd.DataFrame(data, columns=["ID", "User", "Title", "Amount", "Category"])

        col1, col2, col3 = st.columns(3)
        col1.metric("Total", f"₹{df['Amount'].sum()}")
        col2.metric("Average", f"₹{round(df['Amount'].mean(),2)}")
        col3.metric("Entries", len(df))

        st.divider()

        category_filter = st.selectbox(
            "Filter by Category",
            ["All"] + list(df["Category"].unique())
        )

        if category_filter != "All":
            df = df[df["Category"] == category_filter]

        st.dataframe(df[["Title", "Amount", "Category"]])

        st.subheader("📊 Category Distribution")
        st.bar_chart(df.groupby("Category")["Amount"].sum())

    else:
        st.warning("No expenses yet")

# ---------------- ADD ----------------
elif menu == "Add Expense":
    st.title("➕ Add Expense")

    title = st.text_input("Title")
    amount = st.number_input("Amount", min_value=0.0)
    category = st.selectbox(
        "Category",
        ["Food", "Travel", "Bills", "Shopping", "Entertainment", "Other"]
    )

    if st.button("Save Expense"):
        if title and amount > 0:
            conn.execute(
                "INSERT INTO expenses (user_id, title, amount, category) VALUES (?, ?, ?, ?)",
                (st.session_state.user_id, title, amount, category)
            )
            conn.commit()
            st.success("✅ Expense added")
            st.balloons()
            st.rerun()
        else:
            st.error("Enter valid data")

# ---------------- ANALYTICS ----------------
elif menu == "Analytics":
    st.title("📈 Smart Analytics")

    data = conn.execute(
        "SELECT * FROM expenses WHERE user_id=?",
        (st.session_state.user_id,)
    ).fetchall()

    if data:
        df = pd.DataFrame(data, columns=["ID", "User", "Title", "Amount", "Category"])

        st.subheader("🤖 AI Prediction")
        pred = predict_expense(data)
        st.success(f"Next predicted expense: ₹{round(pred,2)}")

        st.subheader("📊 Category Breakdown")
        st.bar_chart(df.groupby("Category")["Amount"].sum())

        st.subheader("🥧 Category Share")
        st.write(df.groupby("Category")["Amount"].sum())

    else:
        st.warning("Not enough data")

# ---------------- MANAGE ----------------
elif menu == "Manage Data":
    st.title("🛠 Manage Expenses")

    data = conn.execute(
        "SELECT * FROM expenses WHERE user_id=?",
        (st.session_state.user_id,)
    ).fetchall()

    if data:
        df = pd.DataFrame(data, columns=["ID", "User", "Title", "Amount", "Category"])

        for _, row in df.iterrows():
            col1, col2, col3, col4 = st.columns([3,2,2,1])

            col1.write(row["Title"])
            col2.write(f"₹{row['Amount']}")
            col3.write(row["Category"])

            if col4.button("❌", key=row["ID"]):
                conn.execute("DELETE FROM expenses WHERE id=?", (row["ID"],))
                conn.commit()
                st.rerun()

    else:
        st.warning("No data")

# ---------------- LOGOUT ----------------
elif menu == "Logout":
    st.session_state.logged_in = False
    st.session_state.username = ""
    st.session_state.user_id = None
    st.rerun()