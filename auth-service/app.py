from flask import Flask, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
import mysql.connector, os, time

app = Flask(__name__)

def get_db():
    while True:
        try:
            return mysql.connector.connect(
                host=os.environ["DB_HOST"],
                user=os.environ["DB_USER"],
                password=os.environ["DB_PASSWORD"],
                database=os.environ["DB_NAME"]
            )
        except mysql.connector.Error:
            time.sleep(2)

db = get_db()

# ---------------- SIGNUP (IDEMPOTENT) ----------------
@app.route("/signup", methods=["POST"])
def signup():
    data = request.json
    email = data["email"]
    password = data["password"]

    cur = db.cursor(dictionary=True)

    # 🔍 Check if user already exists
    cur.execute("SELECT id FROM users WHERE email=%s", (email,))
    user = cur.fetchone()

    if user:
        # ✅ User already exists → return same ID
        return jsonify({"user_id": user["id"]}), 200

    # ✅ Create new user
    cur.execute(
        "INSERT INTO users (email, password) VALUES (%s, %s)",
        (email, generate_password_hash(password))
    )
    db.commit()

    return jsonify({"user_id": cur.lastrowid}), 201


# ---------------- LOGIN ----------------
@app.route("/login", methods=["POST"])
def login():
    data = request.json
    email = data["email"]
    password = data["password"]

    cur = db.cursor(dictionary=True)
    cur.execute("SELECT * FROM users WHERE email=%s", (email,))
    user = cur.fetchone()

    if user and check_password_hash(user["password"], password):
        return jsonify({"user_id": user["id"]}), 200

    return jsonify({"error": "Invalid credentials"}), 401


app.run(host="0.0.0.0", port=5000)
