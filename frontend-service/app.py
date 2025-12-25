from flask import Flask, render_template, request, redirect, session, url_for
import requests, os

app = Flask(__name__)
app.secret_key = "supersecretkey"

AUTH = os.environ["AUTH_URL"]
API = os.environ["API_URL"]

# ---------------- LOGIN ----------------
@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        # 1️⃣ Try login
        r = requests.post(f"{AUTH}/login", json={
            "email": email,
            "password": password
        })

        # 2️⃣ If login fails, auto-signup (EXPECTED APP BEHAVIOR)
        if r.status_code != 200:
            requests.post(f"{AUTH}/signup", json={
                "email": email,
                "password": password
            })

            # Try login again
            r = requests.post(f"{AUTH}/login", json={
                "email": email,
                "password": password
            })

        # 3️⃣ Final login check
        if r.status_code == 200:
            session.clear()
            session["user_id"] = r.json()["user_id"]
            session["user_email"] = email
            return redirect(url_for("notes"))

        # Should almost never happen now
        return render_template(
            "login.html",
            error="Login failed. Please try again."
        )

    return render_template("login.html")


# ---------------- NOTES ----------------
@app.route("/notes", methods=["GET", "POST"])
def notes():
    user_id = session.get("user_id")
    user_email = session.get("user_email")

    if not user_id:
        return redirect(url_for("login"))

    if request.method == "POST":
        content = request.form.get("content", "").strip()
        if content:
            requests.post(
                f"{API}/notes",
                json={"content": content},
                headers={"X-USER-ID": str(user_id)}
            )
        return redirect(url_for("notes"))

    notes = requests.get(
        f"{API}/notes",
        headers={"X-USER-ID": str(user_id)}
    ).json()

    return render_template(
        "notes.html",
        notes=notes,
        user_email=user_email
    )


# ---------------- NOTE DETAIL ----------------
@app.route("/notes/<int:index>", methods=["GET", "POST"])
def note_detail(index):
    user_id = session.get("user_id")
    user_email = session.get("user_email")

    if not user_id:
        return redirect(url_for("login"))

    if request.method == "POST":
        requests.delete(
            f"{API}/notes/{index}",
            headers={"X-USER-ID": str(user_id)}
        )
        return redirect(url_for("notes"))

    note = requests.get(
        f"{API}/notes/{index}",
        headers={"X-USER-ID": str(user_id)}
    ).json()

    return render_template(
        "note_detail.html",
        note=note,
        user_email=user_email
    )


# ---------------- LOGOUT ----------------
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


app.run(host="0.0.0.0", port=5000)
