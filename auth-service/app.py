from flask import Flask, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
import mysql.connector
import os
import time

app = Flask(__name__)

# ---------------------------------------------------
# MySQL Connection (AUTO-RECONNECT, K8s SAFE)
# ---------------------------------------------------
def get_connection(dict_cursor=False):
    while True:
        try:
            conn = mysql.connector.connect(
                host=os.environ["DB_HOST"],
                user=os.environ["DB_USER"],
                password=os.environ["DB_PASSWORD"],
                database=os.environ["DB_NAME"],
                autocommit=True
            )
            cursor = conn.cursor(dictionary=dict_cursor)
            return conn, cursor
        except mysql.connector.Error as e:
            print("⏳ Auth service waiting for MySQL...", e)
            time.sleep(3)

# ---------------------------------------------------
# SIGNUP (IDEMPOTENT)
# ---------------------------------------------------
@app.route("/signup", methods=["POST"])
def signup():
    data = request.json
    email = data["email"]
    password = data["password"]

    conn, cur = get_connection(dict_cursor=True)

    # 🔍 Check if user already exists
    cur.execute("SELECT id FROM users WHERE email=%s", (email,))
    user = cur.fetchone()

    if user:
        cur.close()
        conn.close()
        return jsonify({"user_id": user["id"]}), 200

    # ✅ Create new user
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO users (email, password) VALUES (%s, %s)",
        (email, generate_password_hash(password))
    )

    user_id = cur.lastrowid
    cur.close()
    conn.close()

    return jsonify({"user_id": user_id}), 201

# ---------------------------------------------------
# LOGIN
# ---------------------------------------------------
@app.route("/login", methods=["POST"])
def login():
    data = request.json
    email = data["email"]
    password = data["password"]

    conn, cur = get_connection(dict_cursor=True)

    cur.execute("SELECT id, password FROM users WHERE email=%s", (email,))
    user = cur.fetchone()

    cur.close()
    conn.close()

    if user and check_password_hash(user["password"], password):
        return jsonify({"user_id": user["id"]}), 200

    return jsonify({"error": "Invalid credentials"}), 401

# ---------------------------------------------------
# APP START
# ---------------------------------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
