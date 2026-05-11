"""
Project Radar — Flask Web Server
Captures visitor data (Name, IP, Location, User-Agent, Timestamp) and stores it in stalkers.db.
"""

import sqlite3
import os
import requests
import bleach
from datetime import datetime, timezone
from flask import Flask, render_template, request, redirect, url_for, session
from dotenv import load_dotenv
from werkzeug.middleware.proxy_fix import ProxyFix

load_dotenv()

app = Flask(__name__)
# Add a secret key for session management (needed for admin login)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "fallback_secret_key_if_env_missing")
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "stalkers.db")

# Apply ProxyFix to correctly handle IPs behind reverse proxies (like ngrok or pythonanywhere)
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1)

def init_db():
    """Initialize the SQLite database and create the table if it doesn't exist."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    # Adding location column to existing database might require migration, but for simplicity we recreate if needed or add column
    try:
        cursor.execute("SELECT location FROM visitors LIMIT 1")
    except sqlite3.OperationalError:
        try:
            cursor.execute("ALTER TABLE visitors ADD COLUMN location TEXT DEFAULT 'Unknown'")
        except sqlite3.OperationalError:
            pass # Table might not exist yet
            
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS visitors (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            ip_address TEXT NOT NULL,
            location TEXT DEFAULT 'Unknown',
            user_agent TEXT NOT NULL,
            timestamp TEXT NOT NULL
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS settings (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL
        )
    """)
    # Insert default caught message if not set
    cursor.execute(
        "INSERT OR IGNORE INTO settings (key, value) VALUES (?, ?)",
        ("caught_message", "YOU ARE\nCAUGHT"),
    )
    conn.commit()
    conn.close()


def get_setting(key, default=""):
    """Read a setting from the database."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT value FROM settings WHERE key = ?", (key,))
    row = cursor.fetchone()
    conn.close()
    return row[0] if row else default

def get_geolocation(ip_address):
    """Fetch geolocation data for an IP address using ip-api.com."""
    if ip_address == "127.0.0.1" or ip_address.startswith("192.168."):
        return "Localhost"
    try:
        response = requests.get(f"http://ip-api.com/json/{ip_address}?fields=country,city,isp", timeout=3)
        if response.status_code == 200:
            data = response.json()
            if data.get("status") != "fail":
                city = data.get("city", "Unknown City")
                country = data.get("country", "Unknown Country")
                isp = data.get("isp", "Unknown ISP")
                return f"{city}, {country} ({isp})"
    except Exception:
        pass
    return "Unknown Location"

@app.before_request
def ensure_db():
    """Ensure the database and tables exist before handling any request."""
    init_db()

@app.route("/")
def index():
    """Serve the landing page."""
    return render_template("index.html")


@app.route("/submit", methods=["POST"])
def submit():
    """Capture visitor data and redirect to the caught page."""
    raw_name = request.form.get("name", "Unknown")
    # Sanitize the input to prevent XSS
    name = bleach.clean(raw_name)
    
    ip_address = request.remote_addr
    location = get_geolocation(ip_address)
    user_agent = request.headers.get("User-Agent", "Unknown")
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO visitors (name, ip_address, location, user_agent, timestamp) VALUES (?, ?, ?, ?, ?)",
        (name, ip_address, location, user_agent, timestamp),
    )
    conn.commit()
    conn.close()

    return redirect(url_for("caught"))


@app.route("/caught")
def caught():
    """Serve the caught page with a customizable message."""
    message = get_setting("caught_message", "YOU ARE\nCAUGHT")
    # Convert newlines to <br> for HTML display
    from markupsafe import Markup
    message_html = Markup(bleach.clean(message).replace("\n", "<br>"))
    return render_template("caught.html", message=message_html)


@app.route("/radar-admin", methods=["GET", "POST"])
def admin():
    """Secret Admin Dashboard to manage logs and messages from the Cloud."""
    ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "radar_secret_pass")
    
    if request.method == "POST":
        # Check login
        if "password" in request.form:
            if request.form["password"] == ADMIN_PASSWORD:
                session["admin"] = True
            return redirect(url_for("admin"))
            
        # Handle clear logs & update message if logged in
        if session.get("admin"):
            if "clear" in request.form:
                conn = sqlite3.connect(DB_PATH)
                conn.cursor().execute("DELETE FROM visitors")
                conn.commit()
                conn.close()
            elif "new_message" in request.form:
                new_msg = request.form["new_message"]
                conn = sqlite3.connect(DB_PATH)
                conn.cursor().execute("INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)", ("caught_message", new_msg))
                conn.commit()
                conn.close()
            return redirect(url_for("admin"))

    if not session.get("admin"):
        return render_template("admin_login.html")

    # Fetch data for dashboard
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT name, ip_address, location, user_agent, timestamp FROM visitors ORDER BY timestamp DESC")
    except sqlite3.OperationalError:
        # Fallback if location column doesn't exist yet for some reason
        cursor.execute("SELECT name, ip_address, 'Unknown', user_agent, timestamp FROM visitors ORDER BY timestamp DESC")
    logs = cursor.fetchall()
    conn.close()

    current_msg = get_setting("caught_message", "YOU ARE\nCAUGHT")

    return render_template("admin_dashboard.html", current_msg=current_msg, logs=logs)


if __name__ == "__main__":
    init_db()
    app.run(debug=True, host="0.0.0.0", port=5001)