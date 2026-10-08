import json
import os
from functools import wraps

from authlib.integrations.flask_client import OAuth
from dotenv import load_dotenv
from flask import Flask, redirect, render_template, request, session, url_for, flash
from werkzeug.security import generate_password_hash, check_password_hash

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "change-this-secret-key")
USERS_FILE = "users.json"

oauth = OAuth(app)
google = oauth.register(
    name="google",
    client_id=os.getenv("GOOGLE_CLIENT_ID"),
    client_secret=os.getenv("GOOGLE_CLIENT_SECRET"),
    server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
    client_kwargs={"scope": "openid email profile"},
)


def load_users():
    if not os.path.exists(USERS_FILE):
        return []
    try:
        with open(USERS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return []


def save_users(users):
    with open(USERS_FILE, "w", encoding="utf-8") as f:
        json.dump(users, f, ensure_ascii=False, indent=4)


def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if "user_email" not in session:
            return redirect(url_for("login"))
        return view(*args, **kwargs)
    return wrapped


@app.route("/")
def index():
    if "user_email" in session:
        return redirect(url_for("profile"))
    return render_template("index.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        if not email or not password:
            flash("Заполни все поля.", "error")
            return redirect(url_for("register"))

        if len(password) < 6:
            flash("Пароль должен быть не короче 6 символов.", "error")
            return redirect(url_for("register"))

        users = load_users()
        if any(user["email"] == email for user in users):
            flash("Пользователь с таким email уже существует.", "error")
            return redirect(url_for("register"))

        users.append({
            "email": email,
            "password": generate_password_hash(password),
            "name": email.split("@")[0],
            "provider": "local"
        })
        save_users(users)

        session["user_email"] = email
        return redirect(url_for("profile"))

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        user = next((u for u in load_users() if u["email"] == email), None)

        if not user or not user.get("password") or not check_password_hash(user["password"], password):
            flash("Неверный email или пароль.", "error")
            return redirect(url_for("login"))

        session["user_email"] = email
        return redirect(url_for("profile"))

    return render_template("login.html")


@app.route("/login/google")
def google_login():
    redirect_uri = url_for("google_callback", _external=True)
    return google.authorize_redirect(redirect_uri)


@app.route("/auth/google/callback")
def google_callback():
    token = google.authorize_access_token()
    user_info = token.get("userinfo")

    if not user_info or not user_info.get("email"):
        flash("Google не вернул данные пользователя.", "error")
        return redirect(url_for("login"))

    email = user_info["email"].lower()
    name = user_info.get("name") or email.split("@")[0]

    users = load_users()
    user = next((u for u in users if u["email"] == email), None)

    if not user:
        users.append({
            "email": email,
            "password": None,
            "name": name,
            "provider": "google"
        })
        save_users(users)
    else:
        user["name"] = name
        if user.get("provider") != "google":
            user["provider"] = "google"
        save_users(users)

    session["user_email"] = email
    return redirect(url_for("profile"))


@app.route("/profile")
@login_required
def profile():
    user = next(u for u in load_users() if u["email"] == session["user_email"])
    return render_template("profile.html", user=user)


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(debug=True)
