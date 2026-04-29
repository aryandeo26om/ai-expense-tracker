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



# import streamlit as st
# import sqlite3
# import pandas as pd
# from model import predict_expense
# from werkzeug.security import generate_password_hash, check_password_hash

# st.set_page_config(layout="wide")

# # ---------- DB ----------
# conn = sqlite3.connect("database.db", check_same_thread=False)

# # ---------- SESSION ----------
# if "user" not in st.session_state:
#     st.session_state.user = None
# if "page" not in st.session_state:
#     st.session_state.page = "Dashboard"

# # ---------- CSS ----------
# st.markdown("""
# <style>
# .main {
#     background: linear-gradient(180deg,#020617,#0b0f1a);
# }
# .logo {
#     font-size: 22px;
#     font-weight: 700;
#     color: #a78bfa;
# }
# .title {
#     font-size: 36px;
#     color: #a78bfa;
# }
# .card {
#     padding: 20px;
#     border-radius: 15px;
#     text-align: center;
#     color: white;
# }
# .blue { background: linear-gradient(135deg,#6366f1,#8b5cf6); }
# .green { background: linear-gradient(135deg,#22c55e,#4ade80); }
# .yellow { background: linear-gradient(135deg,#f59e0b,#fbbf24); }
# .purple { background: linear-gradient(135deg,#a855f7,#c084fc); }
# button {
#     background: linear-gradient(135deg,#6366f1,#8b5cf6) !important;
#     color: white !important;
# }
# </style>
# """, unsafe_allow_html=True)

# # ================= AUTH SCREENS =================

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
#             st.error("Username already exists")
#         else:
#             conn.execute(
#                 "INSERT INTO users (username, password) VALUES (?, ?)",
#                 (username, generate_password_hash(password))
#             )
#             conn.commit()
#             st.success("Account created! Now login.")

# # ---------- NOT LOGGED IN ----------
# if not st.session_state.user:
#     choice = st.sidebar.selectbox("Menu", ["Login", "Register"])
#     if choice == "Login":
#         login()
#     else:
#         register()
#     st.stop()

# # ================= NAVBAR =================

# col1, col2 = st.columns([3, 5])

# with col1:
#     st.markdown('<div class="logo">💡 FinTrack</div>', unsafe_allow_html=True)

# with col2:
#     nav1, nav2, nav3, nav4, nav5 = st.columns(5)

#     if nav1.button("Dashboard"):
#         st.session_state.page = "Dashboard"

#     if nav2.button("Add Expense"):
#         st.session_state.page = "Add"

#     if nav3.button("Analytics"):
#         st.session_state.page = "Analytics"

#     if nav4.button("Manage"):
#         st.session_state.page = "Manage"

#     if nav5.button("Logout"):
#         st.session_state.user = None
#         st.rerun()

# st.markdown("---")

# # ---------- USER ----------
# user_id = st.session_state.user[0]

# df = pd.read_sql(
#     "SELECT * FROM expenses WHERE user_id=?",
#     conn,
#     params=(user_id,)
# )

# # ================= DASHBOARD =================
# if st.session_state.page == "Dashboard":

#     st.markdown('<div class="title">🤖 Expense AI Dashboard</div>', unsafe_allow_html=True)

#     if not df.empty:
#         total = df["amount"].sum()
#         avg = df["amount"].mean()
#         count = len(df)
#         categories = df["category"].nunique()

#         c1, c2, c3, c4 = st.columns(4)

#         c1.markdown(f'<div class="card blue">Total<br><h2>₹{total}</h2></div>', unsafe_allow_html=True)
#         c2.markdown(f'<div class="card green">Entries<br><h2>{count}</h2></div>', unsafe_allow_html=True)
#         c3.markdown(f'<div class="card yellow">Categories<br><h2>{categories}</h2></div>', unsafe_allow_html=True)
#         c4.markdown(f'<div class="card purple">Average<br><h2>₹{round(avg,2)}</h2></div>', unsafe_allow_html=True)

#         if total > 5000:
#             st.warning("⚠️ High spending detected!")

#     st.subheader("🔍 Search")
#     search = st.text_input("")

#     if search:
#         df = df[df["title"].str.contains(search, case=False)]

#     st.dataframe(df[["title","amount","category"]])

# # ================= ADD =================
# elif st.session_state.page == "Add":

#     st.title("➕ Add Expense")

#     title = st.text_input("Title")
#     amount = st.number_input("Amount", min_value=0.0)
#     category = st.selectbox(
#         "Category",
#         ["Food","Travel","Bills","Shopping","Entertainment","Other"]
#     )

#     if st.button("Save Expense"):
#         conn.execute(
#             "INSERT INTO expenses (user_id,title,amount,category) VALUES (?,?,?,?)",
#             (user_id,title,amount,category)
#         )
#         conn.commit()
#         st.success("Added!")
#         st.rerun()

# # ================= ANALYTICS =================
# elif st.session_state.page == "Analytics":

#     st.title("📊 Analytics")

#     if not df.empty:
#         st.subheader("Category Breakdown")
#         st.bar_chart(df.groupby("category")["amount"].sum())

#         prediction = predict_expense(df.values.tolist())
#         st.success(f"AI Prediction: ₹{round(prediction,2)}")

# # ================= MANAGE =================
# elif st.session_state.page == "Manage":

#     st.title("🛠 Manage Expenses")

#     for _, row in df.iterrows():
#         c1, c2, c3, c4 = st.columns([3,2,2,1])

#         c1.write(row["title"])
#         c2.write(f"₹{row['amount']}")
#         c3.write(row["category"])

#         if c4.button("❌", key=row["id"]):
#             conn.execute("DELETE FROM expenses WHERE id=?", (row["id"],))
#             conn.commit()
#             st.rerun()

import streamlit as st
import sqlite3
import pandas as pd
from model import predict_expense
from werkzeug.security import generate_password_hash, check_password_hash

st.set_page_config(layout="wide")

# ---------- DB ----------
conn = sqlite3.connect("database.db", check_same_thread=False)

# ---------- SESSION ----------
if "user" not in st.session_state:
    st.session_state.user = None
if "page" not in st.session_state:
    st.session_state.page = "Dashboard"

# ---------- CSS ----------
st.markdown("""
<style>
.main {
    background: linear-gradient(180deg,#020617,#0b0f1a);
}
.logo {
    font-size: 22px;
    font-weight: 700;
    color: #a78bfa;
}
.title {
    font-size: 36px;
    color: #a78bfa;
}
.card {
    padding: 20px;
    border-radius: 15px;
    text-align: center;
    color: white;
}
.blue { background: linear-gradient(135deg,#6366f1,#8b5cf6); }
.green { background: linear-gradient(135deg,#22c55e,#4ade80); }
.yellow { background: linear-gradient(135deg,#f59e0b,#fbbf24); }
.purple { background: linear-gradient(135deg,#a855f7,#c084fc); }
button {
    background: linear-gradient(135deg,#6366f1,#8b5cf6) !important;
    color: white !important;
}
</style>
""", unsafe_allow_html=True)

# ================= AUTH =================

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
            st.error("Username already exists")
        else:
            conn.execute(
                "INSERT INTO users (username, password) VALUES (?, ?)",
                (username, generate_password_hash(password))
            )
            conn.commit()
            st.success("Account created! Now login.")

# ---------- NOT LOGGED ----------
if not st.session_state.user:
    choice = st.sidebar.selectbox("Menu", ["Login", "Register"])
    if choice == "Login":
        login()
    else:
        register()
    st.stop()

# ================= NAVBAR =================

col1, col2 = st.columns([3, 6])

with col1:
    st.markdown('<div class="logo">💡 FinTrack</div>', unsafe_allow_html=True)

with col2:
    nav1, nav2, nav3, nav4, nav5, nav6 = st.columns(6)

    if nav1.button("Dashboard"):
        st.session_state.page = "Dashboard"

    if nav2.button("Add"):
        st.session_state.page = "Add"

    if nav3.button("Analytics"):
        st.session_state.page = "Analytics"

    if nav4.button("Manage"):
        st.session_state.page = "Manage"

    if nav5.button("Export"):
        st.session_state.page = "Export"

    if nav6.button("Logout"):
        st.session_state.user = None
        st.rerun()

st.markdown("---")

# ---------- USER ----------
user_id = st.session_state.user[0]

df = pd.read_sql(
    "SELECT * FROM expenses WHERE user_id=?",
    conn,
    params=(user_id,)
)

# ================= DASHBOARD =================
if st.session_state.page == "Dashboard":

    st.markdown('<div class="title">🤖 Expense AI Dashboard</div>', unsafe_allow_html=True)

    if not df.empty:
        total = df["amount"].sum()
        avg = df["amount"].mean()
        count = len(df)
        categories = df["category"].nunique()

        c1, c2, c3, c4 = st.columns(4)

        c1.markdown(f'<div class="card blue">Total<br><h2>₹{total}</h2></div>', unsafe_allow_html=True)
        c2.markdown(f'<div class="card green">Entries<br><h2>{count}</h2></div>', unsafe_allow_html=True)
        c3.markdown(f'<div class="card yellow">Categories<br><h2>{categories}</h2></div>', unsafe_allow_html=True)
        c4.markdown(f'<div class="card purple">Average<br><h2>₹{round(avg,2)}</h2></div>', unsafe_allow_html=True)

        if total > 5000:
            st.warning("⚠️ High spending detected!")

    st.subheader("🔍 Search")
    search = st.text_input("")

    if search:
        df = df[df["title"].str.contains(search, case=False)]

    st.dataframe(df[["title","amount","category"]])

    # ---------- AI ----------
    st.markdown("### 🤖 Ask AI")

    q = st.text_input("Ask (highest / total / category)")

    if q:
        q = q.lower()

        if "highest" in q:
            row = df.loc[df["amount"].idxmax()]
            st.success(f"Highest expense: ₹{row['amount']} on {row['title']}")

        elif "total" in q:
            st.success(f"Total spending: ₹{df['amount'].sum()}")

        elif "category" in q:
            top = df.groupby("category")["amount"].sum().idxmax()
            st.success(f"You spend most on {top}")

        else:
            st.warning("Try: highest / total / category")

# ================= ADD =================
elif st.session_state.page == "Add":

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

# ================= ANALYTICS =================
elif st.session_state.page == "Analytics":

    st.title("📊 Analytics")

    if not df.empty:
        st.bar_chart(df.groupby("category")["amount"].sum())

        prediction = predict_expense(df.values.tolist())
        st.success(f"Prediction: ₹{round(prediction,2)}")

# ================= MANAGE =================
elif st.session_state.page == "Manage":

    st.title("🛠 Manage Expenses")

    for _, row in df.iterrows():
        c1, c2, c3, c4 = st.columns([3,2,2,1])

        c1.write(row["title"])
        c2.write(f"₹{row['amount']}")
        c3.write(row["category"])

        if c4.button("❌", key=row["id"]):
            conn.execute("DELETE FROM expenses WHERE id=?", (row["id"],))
            conn.commit()
            st.rerun()

# ================= EXPORT =================
elif st.session_state.page == "Export":

    st.title("📥 Export CSV")

    if not df.empty:
        csv = df.to_csv(index=False).encode("utf-8")

        st.download_button(
            label="Download CSV",
            data=csv,
            file_name="expenses.csv",
            mime="text/csv"
        )
    else:
        st.warning("No data to export")