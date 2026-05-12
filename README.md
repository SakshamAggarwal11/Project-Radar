# 🎯 Project Radar

A dark-themed honeypot web app that captures visitor data behind a sleek "Restricted Content" page — paired with a terminal controller for viewing logs and customizing the experience.

![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=flat-square&logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-3.x-000000?style=flat-square&logo=flask&logoColor=white)
![SQLite](https://img.shields.io/badge/SQLite-3-003B57?style=flat-square&logo=sqlite&logoColor=white)

---

## ✨ Features

- **Dark Developer Aesthetic** — `#050505` background, glassmorphic containers, animated grid, floating orbs, scanline overlays, neon cyan/purple accents
- **Data Capture** — Logs visitor Name, IP Address, User-Agent (device), and Timestamp to SQLite
- **Customizable Caught Page** — Giant neon pink message
- **Two Controller Modes** — Professional ANSI-colored Terminal CLI `radar.py` AND a built-in Secret Web Dashboard.

---

## 📁 Project Structure

```
stalker/
├── app.py                  # Flask web server
├── radar.py                # Terminal CLI controller
├── requirements.txt        # Python dependencies
├── stalkers.db             # SQLite database (auto-created)
└── templates/
    ├── index.html          # Landing page
    └── caught.html         # Caught redirect page
```

---

## 🚀 The Absolute Beginner's Guide

You have two choices: run it on your own computer (easier but turns off when you close your laptop), or host it on the Cloud for free (runs 24/7 forever)

---
### METHOD A: Run on your Computer (Temporary)

Follow these exact steps to run it locally with ngrok.

#### Step 0: Before you begin
1. You must have **Python** installed. If you don't, download it from [python.org](https://www.python.org/downloads/) and install it. *(If you are on Windows, make sure to check the box that says "Add Python to PATH" during installation!)*
2. You must have a free **ngrok** account to create public links. Go to [ngrok.com](https://ngrok.com) and create an account. Find your "Authtoken" on their dashboard.

---

### 🍎 IF YOU ARE ON A MAC / LINUX:

#### Phase 1: Start the Server
1. Open the **Terminal** app (Press `Cmd + Space`, type "Terminal", hit Enter).
2. Type `cd ` followed by the path to where you saved this project folder and hit enter. For example:
   ```bash
   cd ~/Documents/stalker
   ```
3. Copy and paste these exact commands one by one, hitting Enter after each:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   python3 app.py
   ```
4. **DO NOT CLOSE THIS TERMINAL.** Leave it running in the background. The server is now on.

#### Phase 2: Use the Radar Tool (Trap & Logs)
1. Leave the first Terminal running. **Open a brand new Terminal window** (Press `Cmd + N`).
2. Go into your project folder again and turn on the virtual environment:
   ```bash
   cd ~/Documents/stalker
   source venv/bin/activate
   ```
3. Type this command to **set the message** the victim will see:
   ```bash
   python3 radar.py setmsg "You just got caught!"
   ```
4. Type this command to **get the trick link**:
   ```bash
   python3 radar.py link
   ```
   *(It will spit out a link like `https://xxxx-xx-xx.ngrok-free.app`. **Send this link to your target!**)*
5. Once your target clicks the link and types their name, type this command to **see their details** (Name, IP, Device):
   ```bash
   python3 radar.py logs
   ```
6. **Clear the Logs (Optional):** Want to clear old tests and start with an empty log?
   ```bash
   python3 radar.py clear
   ```

---

### 🪟 IF YOU ARE ON WINDOWS:

#### Phase 1: Start the Server
1. Open **Command Prompt** (Press the `Windows` key, type "cmd", hit Enter).
2. Type `cd ` followed by the path to where you saved this project folder and hit enter. For example:
   ```cmd
   cd Documents\stalker
   ```
3. Copy and paste these exact commands one by one, hitting Enter after each (wait for installations to finish):
   ```cmd
   python -m venv venv
   venv\Scripts\activate
   pip install -r requirements.txt
   python app.py
   ```
4. **DO NOT CLOSE THIS WINDOW.** Leave it running in the background. The server is now on.

#### Phase 2: Use the Radar Tool (Trap & Logs)
1. Leave the first Command Prompt running. **Open a brand new Command Prompt window**.
2. Go into your project folder again and turn on the virtual environment:
   ```cmd
   cd Documents\stalker
   venv\Scripts\activate
   ```
3. Type this command to **set the message** the victim will see:
   ```cmd
   python radar.py setmsg "You just got caught!"
   ```
4. Type this command to **get the trick link**:
   ```cmd
   python radar.py link
   ```
   *(It will spit out a link like `https://xxxx-xx-xx.ngrok-free.app`. **Send this link to your target!**)*
5. Once your target clicks the link and types their name, type this command to **see their details** (Name, IP, Device):
   ```cmd
   python radar.py logs
   ```
6. **Clear the Logs (Optional):** Want to clear old tests and start with an empty log?
   ```cmd
   python radar.py clear
   ```

---

**Example Logs Output:**
```
  ╔══════════════════════════════════════════════════════════════════╗
  ║        P R O J E C T   R A D A R  —  L O G S              ║
  ╚══════════════════════════════════════════════════════════════════╝
    Showing entries from the last 7 days  •  3 caught
  ──────────────────────────────────────────────────────────────────
  [2026-05-11 13:30:01 UTC]  NAME: target_name  IP: 127.0.0.1  DEVICE: Mac
  ──────────────────────────────────────────────────────────────────
```

---

### METHOD B: Host on the Cloud (Runs 24/7 Forever)

Want your trap to work from anywhere, forever, without needing to keep your terminal open or use ngrok? Follow these 5-minute steps to host it on PythonAnywhere.

#### 1. Create a Cloud Account
* Go to **[PythonAnywhere.com](https://www.pythonanywhere.com/)** and sign up for a free Beginner account.
* Note: Your username will become your public web link (e.g., if you choose `cooltrap`, your link will be `cooltrap.pythonanywhere.com`).

#### 2. Make the Cloud App
* Log in, click the **"Web"** tab at the top.
* Click the blue button: **"Add a new web app"**.
* Click "Next" -> click **"Flask"** -> click **"Python 3.10"** -> click "Next" again.

#### 3. Upload Your Files
* Go to the **"Files"** tab at the top.
* Click the folder called **`mysite`**. Delete the `flask_app.py` file inside it.
* Click the yellow **"Upload a file"** button and upload your `app.py`.
* Upload your `requirements.txt`.
* In the "Enter new directory name" box, type `templates` and click **"New directory"**.
* Inside the new `templates` folder, click "Upload a file" and upload both `index.html` and `caught.html`.

#### 4. Install Packages
* Go to the **"Consoles"** tab at the top.
* Under "Start a new", click **"Bash"**.
* In the black screen, copy/paste this exact command and hit Enter:
  ```bash
  pip3 install --user -r mysite/requirements.txt
  ```
* Wait for the installations to finish.

#### 5. Turn it On
* Go back to the **"Web"** tab. Scroll down to the **"Code"** section.
* Click the link next to **"WSGI configuration file:"**.
* An editor will open. Around **Line 16**, change the line to look exactly like this:
  ```python
  from app import app as application
  ```
* Click the green **"Save"** button at the top right.
* Click the **"Web"** tab again, and hit the big green **"Reload your_username.pythonanywhere.com"** button at the very top.

#### 6. Access your Secret Admin Dashboard
Your trap is now live on the internet! You never need to touch the terminal again.

* **Trap Link for targets:** `http://<your_username>.pythonanywhere.com`
* **Secret Dashboard link:** `http://<your_username>.pythonanywhere.com/radar-admin`
* **Admin Password:** `<YOUR_SECRET_PASSWORD>` *(You MUST change this inside `app.py` before hosting!)*

From your phone or browser, log into the dashboard to check logs, clear logs, and change your neon caught message!

---

### 📖 Full Command Reference (For Method A)

| Command | Description |
|---------|-------------|
| `radar.py link` | Generate a public shareable URL (ngrok tunnel) |
| `radar.py setmsg "MSG"` | Set a custom caught page message |
| `radar.py getmsg` | View the current caught page message |
| `radar.py logs` | Show caught visitors from the last 7 days |
| `radar.py clear` | Clear all trap logs without deleting settings |
| `radar.py help` | Show all available commands |

---

## 🎨 Design

The UI follows a **"Dark Developer"** aesthetic:

- Background: `#050505` with animated CSS grid overlay
- Glassmorphic containers with `backdrop-filter: blur(24px)`
- Floating gradient orbs (cyan, purple, indigo)
- CRT-style scanline overlay
- Neon pink (`#ff0066`) glow on the caught page
- Typography: **Outfit** + **JetBrains Mono**

---

## 📊 Data Captured

| Field | Source |
|-------|--------|
| Name | Form input |
| IP Address | `request.remote_addr` |
| User-Agent | `User-Agent` header (parsed to device type in CLI) |
| Timestamp | UTC timestamp at submission |

---

## ⚠️ Disclaimer

This project is built only for **educational and personal use only**. Always respect privacy laws and obtain consent before collecting any personal data.

---

## 📄 License

MIT
