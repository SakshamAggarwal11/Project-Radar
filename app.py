"""
Project Radar — Flask Web Server
Captures visitor data (Name, IP, User-Agent, Timestamp) and stores it in stalkers.db.
"""

import sqlite3
import os
from datetime import datetime, timezone
from flask import Flask, render_template, request, redirect, url_for, session, render_template_string

app = Flask(__name__)
# Add a secret key for session management (needed for admin login)
# IMPORTANT: Change this value to something random before hosting!
app.secret_key = "CHANGE_ME_TO_A_RANDOM_SECRET_KEY"
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "stalkers.db")


def init_db():
    """Initialize the SQLite database and create the table if it doesn't exist."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS visitors (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            ip_address TEXT NOT NULL,
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
    name = request.form.get("name", "Unknown")
    ip_address = request.remote_addr
    user_agent = request.headers.get("User-Agent", "Unknown")
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO visitors (name, ip_address, user_agent, timestamp) VALUES (?, ?, ?, ?)",
        (name, ip_address, user_agent, timestamp),
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
    message_html = Markup(message.replace("\n", "<br>"))
    return render_template("caught.html", message=message_html)


@app.route("/radar-admin", methods=["GET", "POST"])
def admin():
    """Secret Admin Dashboard to manage logs and messages from the Cloud."""
    # IMPORTANT: Change this password before public hosting!
    ADMIN_PASSWORD = "**********"  # Password to access the dashboard
    
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
        # Login page
        return render_template_string('''
            <html><body style="background:#050505; color:cyan; font-family:monospace; text-align:center; padding-top:100px;">
            <h2>🚨 Restricted Radar Access</h2>
            <form method="POST">
                <input type="password" name="password" placeholder="Passcode" style="padding:10px; background:#111; color:cyan; border:1px solid cyan; text-align:center;">
                <br><br>
                <button type="submit" style="padding:10px 20px; background:cyan; color:#000; border:none; cursor:pointer;">Enter</button>
            </form>
            </body></html>
        ''')

    # Fetch data for dashboard
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT name, ip_address, user_agent, timestamp FROM visitors ORDER BY timestamp DESC")
    logs = cursor.fetchall()
    conn.close()

    current_msg = get_setting("caught_message", "YOU ARE\nCAUGHT")

    # Admin Dashboard page
    return render_template_string('''
        <html><body style="background:#050505; color:#fff; font-family:monospace; padding:30px; max-width:800px; margin:0 auto;">
        
        <h1 style="color:cyan;">🎯 Project Radar | Admin Dashboard</h1>
        
        <div style="background:#111; padding:20px; border:1px solid #333; margin-bottom:20px;">
            <h3 style="color:magenta; margin-top:0;">✏️ 1. Set Caught Message</h3>
            <form method="POST" style="margin:0;">
                <textarea name="new_message" rows="3" style="width:100%; background:#050505; color:cyan; border:1px solid #333; padding:10px; font-family:monospace;">{{ current_msg }}</textarea><br>
                <button type="submit" style="margin-top:10px; padding:8px 15px; background:cyan; color:#000; border:none; font-weight:bold; cursor:pointer;">Update Message</button>
            </form>
        </div>
        
        <div style="background:#111; padding:20px; border:1px solid #333;">
            <h3 style="color:magenta; margin-top:0;">📋 2. Trap Logs <span style="color:#666; font-size:14px;">({{ logs|length }} caught)</span></h3>
            
            <form method="POST" onsubmit="return confirm('WARNING: Are you sure you want to delete all logs forever?');">
                <input type="hidden" name="clear" value="1">
                <button type="submit" style="padding:6px 12px; background:red; color:#fff; border:none; font-weight:bold; cursor:pointer; margin-bottom:15px;">🗑 Clear All Logs</button>
            </form>
            
            <table style="width:100%; border-collapse:collapse; text-align:left;">
                <tr style="border-bottom:1px solid #333; color:cyan;">
                    <th style="padding:8px;">Timestamp (UTC)</th>
                    <th style="padding:8px;">Name</th>
                    <th style="padding:8px;">IP Address</th>
                    <th style="padding:8px;">Device/Browser</th>
                </tr>
                {% for name, ip, ua, ts in logs %}
                <tr style="border-bottom:1px solid #222;">
                    <td style="padding:8px; color:yellow; font-size:12px;">{{ ts }}</td>
                    <td style="padding:8px; font-weight:bold;">{{ name }}</td>
                    <td style="padding:8px; color:#0f0; font-size:12px;">{{ ip }}</td>
                    <td style="padding:8px; color:#aaa; font-size:12px;">{{ ua }}</td>
                </tr>
                {% else %}
                <tr><td colspan="4" style="padding:20px; text-align:center; color:#555;">No stalkers caught yet. Send out your link!</td></tr>
                {% endfor %}
            </table>
        </div>
        </body></html>
    ''', current_msg=current_msg, logs=logs)


if __name__ == "__main__":
    init_db()
    app.run(debug=True, host="0.0.0.0", port=5001)