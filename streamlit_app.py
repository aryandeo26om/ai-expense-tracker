# import streamlit as st
# import sqlite3
# import pandas as pd
# from model import predict_expense
# from werkzeug.security import generate_password_hash, check_password_hash

# st.set_page_config(layout="wide")

# # ---------- DB ----------
# def get_db():
#     return sqlite3.connect("database.db", check_same_thread=False)

# conn = get_db()

# # ---------- SESSION ----------
# if "user" not in st.session_state:
#     st.session_state.user = None

# # ---------- AUTH ----------
# def login():
#     st.title("🔐 Login")

#     username = st.text_input("Username")
#     password = st.text_input("Password", type="password")

#     if st.button("Login"):
#         user = conn.execute(
#             "SELECT * FROM users WHERE username=?", (username,)
#         ).fetchone()

#         if user and check_password_hash(user[2], password):
#             st.session_state.user = user
#             st.success("Login successful")
#             st.rerun()
#         else:
#             st.error("Invalid credentials")


# def register():
#     st.title("📝 Register")

#     username = st.text_input("New Username")
#     password = st.text_input("New Password", type="password")

#     if st.button("Register"):
#         existing = conn.execute(
#             "SELECT * FROM users WHERE username=?", (username,)
#         ).fetchone()

#         if existing:
#             st.error("Username exists")
#         else:
#             conn.execute(
#                 "INSERT INTO users (username, password) VALUES (?, ?)",
#                 (username, generate_password_hash(password))
#             )
#             conn.commit()
#             st.success("Account created")


# # ---------- NOT LOGGED ----------
# if not st.session_state.user:
#     choice = st.sidebar.selectbox("Menu", ["Login", "Register"])

#     if choice == "Login":
#         login()
#     else:
#         register()

#     st.stop()

# # ---------- USER ----------
# user_id = st.session_state.user[0]
# st.sidebar.title(f"👋 {st.session_state.user[1]}")

# menu = st.sidebar.selectbox(
#     "Navigation",
#     ["Dashboard", "Add Expense", "Analytics", "Manage", "Logout"]
# )

# # ---------- DASHBOARD ----------
# if menu == "Dashboard":
#     st.title("🤖 Expense AI Dashboard")

#     df = pd.read_sql(
#         "SELECT * FROM expenses WHERE user_id=?",
#         conn,
#         params=(user_id,)
#     )

#     if not df.empty:
#         total = df["amount"].sum()
#         avg = df["amount"].mean()
#         count = len(df)
#         categories = df["category"].nunique()
#         prediction = predict_expense(df.values.tolist())

#         col1, col2, col3, col4 = st.columns(4)

#         col1.metric("Total", f"₹{total}")
#         col2.metric("Entries", count)
#         col3.metric("Categories", categories)
#         col4.metric("Average", f"₹{round(avg,2)}")

#         if total > 5000:
#             st.warning("⚠️ High spending detected!")

#         st.subheader("🔍 Search")
#         search = st.text_input("")

#         if search:
#             df = df[df["title"].str.contains(search, case=False)]

#         st.dataframe(df[["title","amount","category"]])

#         # AI CHAT
#         st.subheader("🤖 Ask AI")
#         q = st.text_input("Ask something (highest / total / category)")

#         if q:
#             q = q.lower()

#             if "highest" in q:
#                 row = df.loc[df["amount"].idxmax()]
#                 st.info(f"Highest expense: ₹{row['amount']} on {row['title']}")

#             elif "total" in q:
#                 st.info(f"Total spending: ₹{total}")

#             elif "category" in q:
#                 top = df.groupby("category")["amount"].sum().idxmax()
#                 st.info(f"You spend most on {top}")

#             else:
#                 st.info("Try: highest / total / category")

# # ---------- ADD ----------
# elif menu == "Add Expense":
#     st.title("➕ Add Expense")

#     title = st.text_input("Title")
#     amount = st.number_input("Amount", min_value=0.0)
#     category = st.selectbox(
#         "Category",
#         ["Food","Travel","Bills","Shopping","Entertainment","Other"]
#     )

#     if st.button("Save"):
#         conn.execute(
#             "INSERT INTO expenses (user_id,title,amount,category) VALUES (?,?,?,?)",
#             (user_id,title,amount,category)
#         )
#         conn.commit()
#         st.success("Added!")
#         st.rerun()

# # ---------- ANALYTICS ----------
# elif menu == "Analytics":
#     st.title("📊 Analytics")

#     df = pd.read_sql(
#         "SELECT * FROM expenses WHERE user_id=?",
#         conn,
#         params=(user_id,)
#     )

#     if not df.empty:
#         total = df["amount"].sum()
#         avg = df["amount"].mean()

#         st.metric("Total", f"₹{total}")
#         st.metric("Average", f"₹{round(avg,2)}")

#         st.subheader("📊 Category Breakdown")
#         st.bar_chart(df.groupby("category")["amount"].sum())

#         top = df.groupby("category")["amount"].sum().idxmax()
#         st.success(f"Top category: {top}")

# # ---------- MANAGE ----------
# elif menu == "Manage":
#     st.title("🛠 Manage Expenses")

#     df = pd.read_sql(
#         "SELECT * FROM expenses WHERE user_id=?",
#         conn,
#         params=(user_id,)
#     )

#     for _, row in df.iterrows():
#         col1, col2, col3, col4 = st.columns([3,2,2,1])

#         col1.write(row["title"])
#         col2.write(f"₹{row['amount']}")
#         col3.write(row["category"])

#         if col4.button("❌", key=row["id"]):
#             conn.execute("DELETE FROM expenses WHERE id=?", (row["id"],))
#             conn.commit()
#             st.rerun()

# # ---------- LOGOUT ----------
# elif menu == "Logout":
#     st.session_state.user = None
#     st.rerun()

import streamlit as st
import sqlite3
import pandas as pd
from model import predict_expense

st.set_page_config(layout="wide")

# ---------- CUSTOM CSS ----------
st.markdown("""
<style>

/* PAGE BACKGROUND */
.main {
    background: linear-gradient(180deg,#020617,#0b0f1a);
}

/* SIDEBAR */
section[data-testid="stSidebar"] {
    background-color: #020617;
}

/* TITLE */
.title {
    font-size: 42px;
    font-weight: 700;
    color: #a78bfa;
    margin-bottom: 20px;
}

/* CARDS */
.card {
    padding: 20px;
    border-radius: 16px;
    color: white;
    text-align: center;
    font-weight: 500;
}

.blue { background: linear-gradient(135deg,#6366f1,#8b5cf6); }
.green { background: linear-gradient(135deg,#22c55e,#4ade80); }
.yellow { background: linear-gradient(135deg,#f59e0b,#fbbf24); }
.purple { background: linear-gradient(135deg,#a855f7,#c084fc); }

/* BUTTON */
button {
    border-radius: 10px !important;
    background: linear-gradient(135deg,#6366f1,#8b5cf6) !important;
    color: white !important;
}

/* INPUT */
input {
    border-radius: 10px !important;
}

/* TABLE */
[data-testid="stDataFrame"] {
    background-color: #111827;
}

</style>
""", unsafe_allow_html=True)

# ---------- DB ----------
conn = sqlite3.connect("database.db", check_same_thread=False)

df = pd.read_sql("SELECT * FROM expenses", conn)

# ---------- TITLE ----------
st.markdown('<div class="title">🤖 Expense AI Dashboard</div>', unsafe_allow_html=True)

# ---------- STATS ----------
if not df.empty:
    total = df["amount"].sum()
    avg = df["amount"].mean()
    count = len(df)
    categories = df["category"].nunique()
    prediction = predict_expense(df.values.tolist())

    col1, col2, col3, col4 = st.columns(4)

    col1.markdown(f'<div class="card blue">Total spent<br><h2>₹{total}</h2></div>', unsafe_allow_html=True)
    col2.markdown(f'<div class="card green">Entries<br><h2>{count}</h2></div>', unsafe_allow_html=True)
    col3.markdown(f'<div class="card yellow">Categories<br><h2>{categories}</h2></div>', unsafe_allow_html=True)
    col4.markdown(f'<div class="card purple">Average<br><h2>₹{round(avg,2)}</h2></div>', unsafe_allow_html=True)

    if total > 5000:
        st.warning("⚠️ High spending detected!")

# ---------- SEARCH ----------
st.markdown("### 🔍 Search")
search = st.text_input("")

if search:
    df = df[df["title"].str.contains(search, case=False)]

# ---------- TABLE ----------
st.markdown("### 📊 Expenses")
st.dataframe(df[["title","amount","category"]])

# ---------- ADD ----------
st.markdown("### ➕ Add Expense")

title = st.text_input("Title")
amount = st.number_input("Amount", min_value=0.0)
category = st.selectbox("Category", ["Food","Travel","Bills","Shopping","Entertainment","Other"])

if st.button("Add Expense"):
    if title and amount:
        conn.execute(
            "INSERT INTO expenses (user_id,title,amount,category) VALUES (1,?,?,?)",
            (title,amount,category)
        )
        conn.commit()
        st.success("Added Successfully 🚀")
        st.rerun()

# ---------- ANALYTICS ----------
st.markdown("### 📈 AI Prediction")

if not df.empty:
    st.markdown(f"### 💰 Next predicted expense: ₹{round(prediction,2)}")

    st.markdown("### 📊 Category Breakdown")
    st.bar_chart(df.groupby("category")["amount"].sum())