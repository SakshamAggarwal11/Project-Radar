"""
Project Radar — Terminal Controller
Query stalkers.db and display caught visitors from the last 7 days.
Customize the caught page message.
Generate a public shareable link.

Usage:
    python3 radar.py logs
    python3 radar.py setmsg "BUSTED"
    python3 radar.py getmsg
    python3 radar.py link
"""

import sqlite3
import sys
import os
from datetime import datetime, timedelta, timezone

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "stalkers.db")

# ── ANSI Color Codes ──────────────────────────────────────────────
CYAN = "\033[96m"
MAGENTA = "\033[95m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
BOLD = "\033[1m"
DIM = "\033[2m"
RESET = "\033[0m"


def parse_device(user_agent: str) -> str:
    """Extract a human-readable device type from a raw User-Agent string."""
    ua = user_agent.lower()
    if "iphone" in ua:
        return "iPhone"
    elif "ipad" in ua:
        return "iPad"
    elif "android" in ua and "mobile" in ua:
        return "Android Phone"
    elif "android" in ua:
        return "Android Tablet"
    elif "macintosh" in ua or "mac os" in ua:
        return "Mac"
    elif "windows" in ua:
        return "Windows PC"
    elif "linux" in ua:
        return "Linux"
    elif "bot" in ua or "crawler" in ua or "spider" in ua:
        return "Bot/Crawler"
    else:
        return "Unknown"


def show_logs():
    """Query and display logs from the last 7 days."""
    if not os.path.exists(DB_PATH):
        print(f"\n  {RED}✖  Database not found.{RESET} Run the server first to create stalkers.db.\n")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    seven_days_ago = (datetime.now(timezone.utc) - timedelta(days=7)).strftime("%Y-%m-%d %H:%M:%S UTC")

    cursor.execute(
        "SELECT name, ip_address, user_agent, timestamp FROM visitors WHERE timestamp >= ? ORDER BY timestamp DESC",
        (seven_days_ago,),
    )
    rows = cursor.fetchall()
    conn.close()

    if not rows:
        print(f"\n  {DIM}No visitors caught in the last 7 days.{RESET}\n")
        return

    # ── Header ─────────────────────────────────────────────────────
    print()
    print(f"  {BOLD}{CYAN}╔══════════════════════════════════════════════════════════════════╗{RESET}")
    print(f"  {BOLD}{CYAN}║{RESET}        {BOLD}{MAGENTA}P R O J E C T   R A D A R  —  L O G S{RESET}              {BOLD}{CYAN}║{RESET}")
    print(f"  {BOLD}{CYAN}╚══════════════════════════════════════════════════════════════════╝{RESET}")
    print(f"  {DIM}  Showing entries from the last 7 days  •  {len(rows)} caught{RESET}")
    print(f"  {CYAN}{'─' * 66}{RESET}")

    # ── Rows ───────────────────────────────────────────────────────
    for name, ip, ua, ts in rows:
        device = parse_device(ua)
        print(
            f"  {DIM}[{RESET}{YELLOW}{ts}{RESET}{DIM}]{RESET}"
            f"  {CYAN}NAME:{RESET} {BOLD}{name}{RESET}"
            f"  {GREEN}IP:{RESET} {ip}"
            f"  {MAGENTA}DEVICE:{RESET} {device}"
        )

    print(f"  {CYAN}{'─' * 66}{RESET}")
    print()


def clear_logs():
    """Clear all visitor logs from the database without deleting settings."""
    if not os.path.exists(DB_PATH):
        print(f"\n  {RED}✖  Database not found.{RESET} Nothing to clear.\n")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM visitors")
        conn.commit()
        print(f"\n  {GREEN}✔  All trap logs have been cleared successfully.{RESET}\n")
    except sqlite3.OperationalError:
        print(f"\n  {YELLOW}⚠  Tables not created yet.{RESET} Nothing to clear.\n")
    finally:
        conn.close()


def set_message(msg: str):
    """Set the custom caught page message."""
    if not os.path.exists(DB_PATH):
        print(f"\n  {RED}✖  Database not found.{RESET} Run the server first to create stalkers.db.\n")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)",
        ("caught_message", msg),
    )
    conn.commit()
    conn.close()
    print(f"\n  {GREEN}✔  Caught message updated to:{RESET} {BOLD}{msg}{RESET}\n")


def get_message():
    """Display the current caught page message."""
    if not os.path.exists(DB_PATH):
        print(f"\n  {RED}✖  Database not found.{RESET} Run the server first to create stalkers.db.\n")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT value FROM settings WHERE key = ?", ("caught_message",))
    row = cursor.fetchone()
    conn.close()

    if row:
        print(f"\n  {CYAN}Current caught message:{RESET} {BOLD}{row[0]}{RESET}\n")
    else:
        print(f"\n  {DIM}No custom message set. Default: YOU ARE CAUGHT{RESET}\n")


def generate_link(port=5001):
    """Generate a public ngrok tunnel URL."""
    try:
        from pyngrok import ngrok
    except ImportError:
        print(f"\n  {RED}✖  pyngrok not installed.{RESET} Run: pip install pyngrok\n")
        return

    print(f"\n  {DIM}Starting ngrok tunnel on port {port}...{RESET}")

    try:
        tunnel = ngrok.connect(port)
        public_url = tunnel.public_url

        print(f"  {BOLD}{CYAN}╔══════════════════════════════════════════════════════════════════╗{RESET}")
        print(f"  {BOLD}{CYAN}║{RESET}       {BOLD}{MAGENTA}P R O J E C T   R A D A R  —  L I N K{RESET}               {BOLD}{CYAN}║{RESET}")
        print(f"  {BOLD}{CYAN}╚══════════════════════════════════════════════════════════════════╝{RESET}")
        print(f"  {CYAN}{'─' * 66}{RESET}")
        print(f"  {GREEN}✔  Public URL:{RESET}  {BOLD}{public_url}{RESET}")
        print(f"  {CYAN}{'─' * 66}{RESET}")
        print(f"  {DIM}Share this link with your target. Press Ctrl+C to stop.{RESET}")
        print()

        # Keep alive until user presses Ctrl+C
        input(f"  {DIM}Press Enter to disconnect the tunnel...{RESET}")
    except KeyboardInterrupt:
        pass
    finally:
        ngrok.kill()
        print(f"\n  {YELLOW}⏹  Tunnel disconnected.{RESET}\n")


def show_help():
    """Display usage information."""
    print(f"""
  {BOLD}{CYAN}Project Radar — Terminal Controller{RESET}

  {BOLD}Usage:{RESET}
    python3 radar.py {GREEN}logs{RESET}               Show caught visitors (last 7 days)
    python3 radar.py {GREEN}clear{RESET}              Clear all caught visitors logs
    python3 radar.py {GREEN}setmsg{RESET} {YELLOW}"MESSAGE"{RESET}    Set custom caught page message
    python3 radar.py {GREEN}getmsg{RESET}              Show current caught message
    python3 radar.py {GREEN}link{RESET}               Generate a public shareable link
    python3 radar.py {GREEN}help{RESET}               Show this message

  {DIM}Tip: Use \\n in your message for line breaks (e.g. "YOU ARE\\nBUSTED"){RESET}
""")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        show_help()
        sys.exit(0)

    command = sys.argv[1].lower()

    if command == "logs":
        show_logs()
    elif command == "clear":
        clear_logs()
    elif command == "setmsg":
        if len(sys.argv) < 3:
            print(f"\n  {RED}✖  Missing message.{RESET} Usage: python3 radar.py setmsg \"YOUR MESSAGE\"\n")
            sys.exit(1)
        # Join all remaining args to support unquoted multi-word messages
        msg = " ".join(sys.argv[2:])
        # Support literal \n for line breaks
        msg = msg.replace("\\n", "\n")
        set_message(msg)
    elif command == "getmsg":
        get_message()
    elif command == "link":
        port = int(sys.argv[2]) if len(sys.argv) > 2 else 5001
        generate_link(port)
    elif command == "help":
        show_help()
    else:
        print(f"\n  {RED}✖  Unknown command: '{command}'{RESET}")
        show_help()
        sys.exit(1)
