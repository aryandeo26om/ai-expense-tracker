from flask import Flask, render_template, request, redirect, session, Response
import sqlite3, json
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import timedelta
from model import predict_expense

app = Flask(__name__)
app.secret_key = "secret123"
app.permanent_session_lifetime = timedelta(days=7)

# ---------------- DB ----------------
def get_db():
    return sqlite3.connect("database.db")


# 🔐 REGISTER
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"].strip()
        password = request.form["password"]

        if not username or not password:
            return render_template("register.html", error="Username and password required")

        conn = get_db()
        existing = conn.execute("SELECT id FROM users WHERE username=?", (username,)).fetchone()

        if existing:
            conn.close()
            return render_template("register.html", error="Username already exists")

        conn.execute(
            "INSERT INTO users (username, password) VALUES (?, ?)",
            (username, generate_password_hash(password))
        )
        conn.commit()
        conn.close()

        return render_template("login.html", message="Account created successfully")

    return render_template("register.html")


# 🔐 LOGIN
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"].strip()
        password = request.form["password"]

        conn = get_db()
        user = conn.execute("SELECT * FROM users WHERE username=?", (username,)).fetchone()
        conn.close()

        if user and check_password_hash(user[2], password):
            session.permanent = True
            session["user_id"] = user[0]
            session["username"] = user[1]
            return redirect("/")
        else:
            return render_template("login.html", error="Invalid credentials")

    return render_template("login.html")


# 🔓 LOGOUT
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")


# 🏠 DASHBOARD
@app.route("/")
def dashboard():
    if "user_id" not in session:
        return redirect("/login")

    conn = get_db()
    data = conn.execute(
        "SELECT * FROM expenses WHERE user_id=?",
        (session["user_id"],)
    ).fetchall()
    conn.close()

    total = sum([row[3] for row in data])
    category_count = len(set([row[4] for row in data]))
    average = round(total / len(data), 2) if data else 0

    labels = [row[4] for row in data]
    amounts = [row[3] for row in data]

    prediction = predict_expense(data) if data else 0

    alert = "⚠️ High spending detected!" if total > 5000 else ""

    return render_template(
        "dashboard.html",
        data=data,
        total=total,
        alert=alert,
        labels=json.dumps(labels),
        amounts=json.dumps(amounts),
        category_count=category_count,
        average=average,
        prediction=round(prediction, 2),
        ai_response=None
    )


# 🤖 AI CHAT
@app.route("/ask-ai", methods=["POST"])
def ask_ai():
    if "user_id" not in session:
        return redirect("/login")

    question = request.form["question"].lower()

    conn = get_db()
    data = conn.execute(
        "SELECT * FROM expenses WHERE user_id=?",
        (session["user_id"],)
    ).fetchall()
    conn.close()

    if not data:
        return redirect("/")

    if "highest" in question:
        max_exp = max(data, key=lambda x: x[3])
        response = f"Your highest expense is ₹{max_exp[3]} on {max_exp[2]}"

    elif "total" in question:
        total = sum(row[3] for row in data)
        response = f"Your total spending is ₹{total}"

    elif "category" in question:
        categories = {}
        for row in data:
            categories[row[4]] = categories.get(row[4], 0) + row[3]
        top_cat = max(categories, key=categories.get)
        response = f"You spend most on {top_cat}"

    else:
        response = "Try asking: highest expense, total spending, or top category"

    total = sum([row[3] for row in data])
    category_count = len(set([row[4] for row in data]))
    average = round(total / len(data), 2)

    labels = [row[4] for row in data]
    amounts = [row[3] for row in data]

    prediction = predict_expense(data)

    return render_template(
        "dashboard.html",
        data=data,
        total=total,
        labels=json.dumps(labels),
        amounts=json.dumps(amounts),
        category_count=category_count,
        average=average,
        prediction=round(prediction, 2),
        ai_response=response
    )


# ➕ ADD
@app.route("/add", methods=["GET", "POST"])
def add():
    if "user_id" not in session:
        return redirect("/login")

    if request.method == "POST":
        title = request.form["title"]
        category = request.form["category"]
        amount = float(request.form["amount"])

        conn = get_db()
        conn.execute(
            "INSERT INTO expenses (user_id, title, amount, category) VALUES (?, ?, ?, ?)",
            (session["user_id"], title, amount, category)
        )
        conn.commit()
        conn.close()

        return redirect("/")

    return render_template("add.html")


# ✏️ EDIT
@app.route("/edit/<int:id>", methods=["GET", "POST"])
def edit(id):
    if "user_id" not in session:
        return redirect("/login")

    conn = get_db()
    expense = conn.execute(
        "SELECT * FROM expenses WHERE id=? AND user_id=?",
        (id, session["user_id"])
    ).fetchone()

    if request.method == "POST":
        title = request.form["title"]
        category = request.form["category"]
        amount = float(request.form["amount"])

        conn.execute(
            "UPDATE expenses SET title=?, amount=?, category=? WHERE id=?",
            (title, amount, category, id)
        )
        conn.commit()
        conn.close()

        return redirect("/")

    conn.close()
    return render_template("edit.html", expense=expense)


# ❌ DELETE
@app.route("/delete/<int:id>")
def delete(id):
    if "user_id" not in session:
        return redirect("/login")

    conn = get_db()
    conn.execute("DELETE FROM expenses WHERE id=? AND user_id=?", (id, session["user_id"]))
    conn.commit()
    conn.close()

    return redirect("/")


# 🔍 SEARCH
@app.route("/search", methods=["POST"])
def search():
    if "user_id" not in session:
        return redirect("/login")

    query = request.form["query"]

    conn = get_db()
    data = conn.execute(
        "SELECT * FROM expenses WHERE title LIKE ? AND user_id=?",
        ('%' + query + '%', session["user_id"])
    ).fetchall()
    conn.close()

    total = sum([row[3] for row in data])
    category_count = len(set([row[4] for row in data]))
    average = round(total / len(data), 2) if data else 0

    labels = [row[4] for row in data]
    amounts = [row[3] for row in data]

    prediction = predict_expense(data) if data else 0

    return render_template(
        "dashboard.html",
        data=data,
        total=total,
        labels=json.dumps(labels),
        amounts=json.dumps(amounts),
        category_count=category_count,
        average=average,
        prediction=round(prediction, 2),
        ai_response=None
    )

# ANALYTICS
@app.route("/report")
def report():
    if "user_id" not in session:
        return redirect("/login")

    conn = get_db()
    data = conn.execute(
        "SELECT * FROM expenses WHERE user_id=?",
        (session["user_id"],)
    ).fetchall()
    conn.close()

    total = sum([row[3] for row in data])
    average = round(total / len(data), 2) if data else 0
    category_count = len(set([row[4] for row in data]))

    labels = [row[4] for row in data]
    amounts = [row[3] for row in data]

    prediction = predict_expense(data) if data else 0

    # TOP CATEGORY
    category_totals = {}
    for row in data:
        category_totals[row[4]] = category_totals.get(row[4], 0) + row[3]

    top_category = max(category_totals, key=category_totals.get) if category_totals else "None"

    return render_template(
        "report.html",
        data=data,
        total=total,
        average=average,
        category_count=category_count,
        labels=json.dumps(labels),
        amounts=json.dumps(amounts),
        prediction=round(prediction, 2),
        top_category=top_category
    )

# 📁 EXPORT CSV
@app.route("/export")
def export():
    if "user_id" not in session:
        return redirect("/login")

    conn = get_db()
    data = conn.execute(
        "SELECT title, amount, category FROM expenses WHERE user_id=?",
        (session["user_id"],)
    ).fetchall()
    conn.close()

    def generate():
        yield "Title,Amount,Category\n"
        for row in data:
            yield f"{row[0]},{row[1]},{row[2]}\n"

    return Response(
        generate(),
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment;filename=expenses.csv"}
    )


# ▶ RUN
if __name__ == "__main__":
    app.run(debug=True)

# from flask import Flask, render_template, request, redirect, session, Response
# import sqlite3, json, os
# from werkzeug.security import generate_password_hash, check_password_hash
# from datetime import timedelta
# from model import predict_expense
# from openai import OpenAI

# app = Flask(__name__)
# app.secret_key = "secret123"
# app.permanent_session_lifetime = timedelta(days=7)

# # 🤖 OpenAI
# client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# # ---------------- DB ----------------
# def get_db():
#     return sqlite3.connect("database.db")

# # ---------------- REGISTER ----------------
# @app.route("/register", methods=["GET", "POST"])
# def register():
#     if request.method == "POST":
#         username = request.form["username"].strip()
#         password = request.form["password"]

#         conn = get_db()
#         existing = conn.execute("SELECT id FROM users WHERE username=?", (username,)).fetchone()

#         if existing:
#             conn.close()
#             return render_template("register.html", error="Username exists")

#         conn.execute(
#             "INSERT INTO users (username, password) VALUES (?, ?)",
#             (username, generate_password_hash(password))
#         )
#         conn.commit()
#         conn.close()

#         return render_template("login.html", message="Account created")

#     return render_template("register.html")

# # ---------------- LOGIN ----------------
# @app.route("/login", methods=["GET", "POST"])
# def login():
#     if request.method == "POST":
#         username = request.form["username"]
#         password = request.form["password"]

#         conn = get_db()
#         user = conn.execute("SELECT * FROM users WHERE username=?", (username,)).fetchone()
#         conn.close()

#         if user and check_password_hash(user[2], password):
#             session["user_id"] = user[0]
#             session["username"] = user[1]
#             return redirect("/")
#         else:
#             return render_template("login.html", error="Invalid login")

#     return render_template("login.html")

# # ---------------- LOGOUT ----------------
# @app.route("/logout")
# def logout():
#     session.clear()
#     return redirect("/login")

# # ---------------- DASHBOARD ----------------
# @app.route("/")
# def dashboard():
#     if "user_id" not in session:
#         return redirect("/login")

#     conn = get_db()
#     data = conn.execute(
#         "SELECT * FROM expenses WHERE user_id=?",
#         (session["user_id"],)
#     ).fetchall()
#     conn.close()

#     total = sum(row[3] for row in data)
#     category_count = len(set(row[4] for row in data))
#     average = round(total / len(data), 2) if data else 0

#     labels = [row[4] for row in data]
#     amounts = [row[3] for row in data]

#     prediction = predict_expense(data) if data else 0

#     return render_template(
#         "dashboard.html",
#         data=data,
#         total=total,
#         category_count=category_count,
#         average=average,
#         labels=json.dumps(labels),
#         amounts=json.dumps(amounts),
#         prediction=round(prediction, 2),
#         ai_response=None
#     )

# # ---------------- ANALYTICS ----------------
# @app.route("/report")
# def report():
#     if "user_id" not in session:
#         return redirect("/login")

#     conn = get_db()
#     data = conn.execute(
#         "SELECT * FROM expenses WHERE user_id=?",
#         (session["user_id"],)
#     ).fetchall()
#     conn.close()

#     if not data:
#         return render_template("report.html", data=[])

#     total = sum(row[3] for row in data)
#     average = round(total / len(data), 2)
#     category_count = len(set(row[4] for row in data))

#     # CATEGORY TOTALS
#     category_totals = {}
#     for row in data:
#         category_totals[row[4]] = category_totals.get(row[4], 0) + row[3]

#     labels = list(category_totals.keys())
#     amounts = list(category_totals.values())

#     # MONTHLY TREND
#     monthly = {}
#     for i, row in enumerate(data):
#         month = f"Month {i+1}"
#         monthly[month] = monthly.get(month, 0) + row[3]

#     top_category = max(category_totals, key=category_totals.get)
#     prediction = predict_expense(data)

#     return render_template(
#         "report.html",
#         data=data,
#         total=total,
#         average=average,
#         category_count=category_count,
#         labels=json.dumps(labels),
#         amounts=json.dumps(amounts),
#         month_labels=json.dumps(list(monthly.keys())),
#         month_amounts=json.dumps(list(monthly.values())),
#         prediction=round(prediction, 2),
#         top_category=top_category,
#         ai_response=None
#     )

# # ---------------- AI CHAT ----------------
# @app.route("/ask-ai", methods=["POST"])
# def ask_ai():
#     if "user_id" not in session:
#         return redirect("/login")

#     question = request.form["question"]

#     conn = get_db()
#     data = conn.execute(
#         "SELECT title, amount, category FROM expenses WHERE user_id=?",
#         (session["user_id"],)
#     ).fetchall()
#     conn.close()

#     context = "\n".join([f"{d[0]} - ₹{d[1]} ({d[2]})" for d in data])

#     try:
#         response = client.chat.completions.create(
#             model="gpt-4o-mini",
#             messages=[
#                 {"role": "system", "content": "You are a financial assistant."},
#                 {"role": "user", "content": f"My expenses:\n{context}\n\nQuestion: {question}"}
#             ]
#         )
#         answer = response.choices[0].message.content
#     except:
#         answer = "AI service unavailable. Check API key."

#     return report_with_ai(answer)

# def report_with_ai(ai_response):
#     conn = get_db()
#     data = conn.execute(
#         "SELECT * FROM expenses WHERE user_id=?",
#         (session["user_id"],)
#     ).fetchall()
#     conn.close()

#     total = sum(row[3] for row in data)
#     average = round(total / len(data), 2)
#     category_count = len(set(row[4] for row in data))

#     category_totals = {}
#     for row in data:
#         category_totals[row[4]] = category_totals.get(row[4], 0) + row[3]

#     monthly = {}
#     for i, row in enumerate(data):
#         month = f"Month {i+1}"
#         monthly[month] = monthly.get(month, 0) + row[3]

#     return render_template(
#         "report.html",
#         data=data,
#         total=total,
#         average=average,
#         category_count=category_count,
#         labels=json.dumps(list(category_totals.keys())),
#         amounts=json.dumps(list(category_totals.values())),
#         month_labels=json.dumps(list(monthly.keys())),
#         month_amounts=json.dumps(list(monthly.values())),
#         prediction=round(predict_expense(data), 2),
#         top_category=max(category_totals, key=category_totals.get),
#         ai_response=ai_response
#     )

# # ---------------- ADD ----------------
# @app.route("/add", methods=["GET", "POST"])
# def add():
#     if "user_id" not in session:
#         return redirect("/login")

#     if request.method == "POST":
#         title = request.form["title"]
#         amount = float(request.form["amount"])
#         category = request.form["category"]

#         conn = get_db()
#         conn.execute(
#             "INSERT INTO expenses (user_id, title, amount, category) VALUES (?, ?, ?, ?)",
#             (session["user_id"], title, amount, category)
#         )
#         conn.commit()
#         conn.close()

#         return redirect("/")

#     return render_template("add.html")

# # ---------------- DELETE ----------------
# @app.route("/delete/<int:id>")
# def delete(id):
#     if "user_id" not in session:
#         return redirect("/login")

#     conn = get_db()
#     conn.execute("DELETE FROM expenses WHERE id=? AND user_id=?", (id, session["user_id"]))
#     conn.commit()
#     conn.close()

#     return redirect("/")

# # ---------------- SEARCH ----------------
# @app.route("/search", methods=["POST"])
# def search():
#     query = request.form["query"]

#     conn = get_db()
#     data = conn.execute(
#         "SELECT * FROM expenses WHERE title LIKE ? AND user_id=?",
#         ('%' + query + '%', session["user_id"])
#     ).fetchall()
#     conn.close()

#     return render_template("dashboard.html", data=data)

# # ---------------- EXPORT ----------------
# @app.route("/export")
# def export():
#     conn = get_db()
#     data = conn.execute(
#         "SELECT title, amount, category FROM expenses WHERE user_id=?",
#         (session["user_id"],)
#     ).fetchall()
#     conn.close()

#     def generate():
#         yield "Title,Amount,Category\n"
#         for row in data:
#             yield f"{row[0]},{row[1]},{row[2]}\n"

#     return Response(
#         generate(),
#         mimetype="text/csv",
#         headers={"Content-Disposition": "attachment;filename=expenses.csv"}
#     )

# # ---------------- RUN ----------------
# if __name__ == "__main__":
#     app.run(debug=True)