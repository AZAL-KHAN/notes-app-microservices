from flask import Flask, request, jsonify
import mysql.connector, os, time
from datetime import date, datetime

app = Flask(__name__)

# ---------------- DB CONNECTION WITH RETRY ----------------
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
            print("⏳ backend-service waiting for MySQL...")
            time.sleep(3)

db = get_db()

# ---------------- FETCH NOTES (WITH DATE FORMAT FIX) ----------------
def fetch_notes(user_id):
    cur = db.cursor(dictionary=True)
    cur.execute(
        "SELECT * FROM notes WHERE user_id=%s ORDER BY id",
        (user_id,)
    )
    notes = cur.fetchall()

    for i, n in enumerate(notes):
        # Display number
        n["display_no"] = i + 1

        # ✅ FORMAT DATE AS DD/MM/YYYY
        if isinstance(n["created_at"], (date, datetime)):
            n["created_at"] = n["created_at"].strftime("%d/%m/%Y")

    return notes


# ---------------- NOTES LIST & CREATE ----------------
@app.route("/notes", methods=["GET", "POST"])
def notes():
    user_id = request.headers.get("X-USER-ID")

    if not user_id or not user_id.isdigit():
        return jsonify({"error": "Unauthorized"}), 401

    if request.method == "POST":
        cur = db.cursor()
        cur.execute(
            "INSERT INTO notes (user_id, content, created_at) VALUES (%s, %s, %s)",
            (user_id, request.json["content"], date.today())
        )
        db.commit()

    return jsonify(fetch_notes(user_id))


# ---------------- NOTE DETAIL & DELETE ----------------
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
        cur = db.cursor()
        cur.execute("DELETE FROM notes WHERE id=%s", (note["id"],))
        db.commit()
        return jsonify({"status": "deleted"})

    return jsonify(note)


app.run(host="0.0.0.0", port=5000)
