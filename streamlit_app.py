import streamlit as st
import sqlite3
import pandas as pd
from model import predict_expense
from werkzeug.security import generate_password_hash, check_password_hash

st.set_page_config(layout="wide")

# ---------- DB ----------
def get_db():
    return sqlite3.connect("database.db", check_same_thread=False)

conn = get_db()

# ---------- SESSION ----------
if "user" not in st.session_state:
    st.session_state.user = None

# ---------- AUTH ----------
def login():
    st.title("🔐 Login")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        user = conn.execute(
            "SELECT * FROM users WHERE username=?", (username,)
        ).fetchone()

        if user and check_password_hash(user[2], password):
            st.session_state.user = user
            st.success("Login successful")
            st.rerun()
        else:
            st.error("Invalid credentials")


def register():
    st.title("📝 Register")

    username = st.text_input("New Username")
    password = st.text_input("New Password", type="password")

    if st.button("Register"):
        existing = conn.execute(
            "SELECT * FROM users WHERE username=?", (username,)
        ).fetchone()

        if existing:
            st.error("Username exists")
        else:
            conn.execute(
                "INSERT INTO users (username, password) VALUES (?, ?)",
                (username, generate_password_hash(password))
            )
            conn.commit()
            st.success("Account created")


# ---------- NOT LOGGED ----------
if not st.session_state.user:
    choice = st.sidebar.selectbox("Menu", ["Login", "Register"])

    if choice == "Login":
        login()
    else:
        register()

    st.stop()

# ---------- USER ----------
user_id = st.session_state.user[0]
st.sidebar.title(f"👋 {st.session_state.user[1]}")

menu = st.sidebar.selectbox(
    "Navigation",
    ["Dashboard", "Add Expense", "Analytics", "Manage", "Logout"]
)

# ---------- DASHBOARD ----------
if menu == "Dashboard":
    st.title("🤖 Expense AI Dashboard")

    df = pd.read_sql(
        "SELECT * FROM expenses WHERE user_id=?",
        conn,
        params=(user_id,)
    )

    if not df.empty:
        total = df["amount"].sum()
        avg = df["amount"].mean()
        count = len(df)
        categories = df["category"].nunique()
        prediction = predict_expense(df.values.tolist())

        col1, col2, col3, col4 = st.columns(4)

        col1.metric("Total", f"₹{total}")
        col2.metric("Entries", count)
        col3.metric("Categories", categories)
        col4.metric("Average", f"₹{round(avg,2)}")

        if total > 5000:
            st.warning("⚠️ High spending detected!")

        st.subheader("🔍 Search")
        search = st.text_input("")

        if search:
            df = df[df["title"].str.contains(search, case=False)]

        st.dataframe(df[["title","amount","category"]])

        # AI CHAT
        st.subheader("🤖 Ask AI")
        q = st.text_input("Ask something (highest / total / category)")

        if q:
            q = q.lower()

            if "highest" in q:
                row = df.loc[df["amount"].idxmax()]
                st.info(f"Highest expense: ₹{row['amount']} on {row['title']}")

            elif "total" in q:
                st.info(f"Total spending: ₹{total}")

            elif "category" in q:
                top = df.groupby("category")["amount"].sum().idxmax()
                st.info(f"You spend most on {top}")

            else:
                st.info("Try: highest / total / category")

# ---------- ADD ----------
elif menu == "Add Expense":
    st.title("➕ Add Expense")

    title = st.text_input("Title")
    amount = st.number_input("Amount", min_value=0.0)
    category = st.selectbox(
        "Category",
        ["Food","Travel","Bills","Shopping","Entertainment","Other"]
    )

    if st.button("Save"):
        conn.execute(
            "INSERT INTO expenses (user_id,title,amount,category) VALUES (?,?,?,?)",
            (user_id,title,amount,category)
        )
        conn.commit()
        st.success("Added!")
        st.rerun()

# ---------- ANALYTICS ----------
elif menu == "Analytics":
    st.title("📊 Analytics")

    df = pd.read_sql(
        "SELECT * FROM expenses WHERE user_id=?",
        conn,
        params=(user_id,)
    )

    if not df.empty:
        total = df["amount"].sum()
        avg = df["amount"].mean()

        st.metric("Total", f"₹{total}")
        st.metric("Average", f"₹{round(avg,2)}")

        st.subheader("📊 Category Breakdown")
        st.bar_chart(df.groupby("category")["amount"].sum())

        top = df.groupby("category")["amount"].sum().idxmax()
        st.success(f"Top category: {top}")

# ---------- MANAGE ----------
elif menu == "Manage":
    st.title("🛠 Manage Expenses")

    df = pd.read_sql(
        "SELECT * FROM expenses WHERE user_id=?",
        conn,
        params=(user_id,)
    )

    for _, row in df.iterrows():
        col1, col2, col3, col4 = st.columns([3,2,2,1])

        col1.write(row["title"])
        col2.write(f"₹{row['amount']}")
        col3.write(row["category"])

        if col4.button("❌", key=row["id"]):
            conn.execute("DELETE FROM expenses WHERE id=?", (row["id"],))
            conn.commit()
            st.rerun()

# ---------- LOGOUT ----------
elif menu == "Logout":
    st.session_state.user = None
    st.rerun()