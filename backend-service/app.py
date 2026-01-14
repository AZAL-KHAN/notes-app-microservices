from flask import Flask, request, jsonify
import mysql.connector
import os
import time
from datetime import date, datetime

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
            print("⏳ Backend waiting for MySQL...", e)
            time.sleep(3)

# ---------------------------------------------------
# Fetch Notes (with date formatting)
# ---------------------------------------------------
def fetch_notes(user_id):
    conn, cur = get_connection(dict_cursor=True)

    cur.execute(
        "SELECT * FROM notes WHERE user_id=%s ORDER BY id",
        (user_id,)
    )
    notes = cur.fetchall()

    for i, note in enumerate(notes):
        note["display_no"] = i + 1
        if isinstance(note["created_at"], (date, datetime)):
            note["created_at"] = note["created_at"].strftime("%d/%m/%Y")

    cur.close()
    conn.close()
    return notes

# ---------------------------------------------------
# Notes List & Create
# ---------------------------------------------------
@app.route("/notes", methods=["GET", "POST"])
def notes():
    user_id = request.headers.get("X-USER-ID")

    if not user_id or not user_id.isdigit():
        return jsonify({"error": "Unauthorized"}), 401

    if request.method == "POST":
        conn, cur = get_connection()
        cur.execute(
            "INSERT INTO notes (user_id, content, created_at) VALUES (%s, %s, %s)",
            (user_id, request.json["content"], date.today())
        )
        cur.close()
        conn.close()

    return jsonify(fetch_notes(user_id))

# ---------------------------------------------------
# Note Detail & Delete
# ---------------------------------------------------
@app.route("/notes/<int:index>", methods=["GET", "DELETE"])
def note_detail(index):
    user_id = request.headers.get("X-USER-ID")

    if not user_id or not user_id.isdigit():
        return jsonify({"error": "Unauthorized"}), 401

    notes = fetch_notes(user_id)

    if index < 1 or index > len(notes):
        return jsonify({"error": "Not found"}), 404

    note = notes[index - 1]

    if request.method == "DELETE":
        conn, cur = get_connection()
        cur.execute("DELETE FROM notes WHERE id=%s", (note["id"],))
        cur.close()
        conn.close()
        return jsonify({"status": "deleted"})

    return jsonify(note)

# ---------------------------------------------------
# App Start
# ---------------------------------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
