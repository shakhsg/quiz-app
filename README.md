# Quiz Application

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-3.0%2B-000000?logo=flask)](https://flask.palletsprojects.com)
[![License: MIT](https://img.shields.io/badge/License-MIT-green)](LICENSE)
[![CI](https://github.com/shakhsg/quiz-app/actions/workflows/ci.yml/badge.svg)](https://github.com/shakhsg/quiz-app/actions)

An interactive, timed quiz game with a Flask backend and a modern dark-themed UI.

---

## Features

| Feature | Description |
|---|---|
| 📋 Main Menu | Navigate between Start, Rules, and Logout |
| 🗂️ 3 Categories | General Knowledge, Science, Technology |
| ⏱️ Timed Questions | 15-second countdown per question |
| ✅ Score Tracking | Correct / wrong count with percentage and grade |
| 🔐 Secure Auth | Werkzeug password hashing, Flask-Login sessions, CSRF protection |
| 💾 Persistent Accounts | SQLite locally; PostgreSQL-ready for deployment |
| 🔁 Replay | Play again without logging out |

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python 3.x, Flask 3, Flask-SQLAlchemy, Flask-Login, Flask-WTF |
| Database | SQLite (local) / PostgreSQL (production) |
| Password hashing | Werkzeug `generate_password_hash` / `check_password_hash` |
| Frontend | Vanilla HTML + CSS + JavaScript (no framework) |
| Deployment | Gunicorn + Render |

---

## Running Locally

**1. Clone and create a virtual environment**
```bash
git clone https://github.com/your-username/quiz-app.git
cd quiz-app
python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
```

**2. Install dependencies**
```bash
pip install -r requirements.txt
```

**3. Set up environment variables**
```bash
cp .env.example .env
# Edit .env — at minimum set a strong SECRET_KEY
```

**4. Run the development server**
```bash
python app.py
```

Open [http://localhost:5000](http://localhost:5000) in your browser.  
The SQLite database (`instance/quiz.db`) is created automatically on first run.

---

## Deploying to Render

1. Push the repo to GitHub.
2. Create a new **Web Service** on [Render](https://render.com) pointing to the repo.
3. Set the following environment variables in the Render dashboard:

| Variable | Value |
|---|---|
| `APP_CONFIG` | `production` |
| `SECRET_KEY` | A long random string (use `python -c "import secrets; print(secrets.token_hex(32))"`) |
| `DATABASE_URL` | Set automatically when you attach a Render PostgreSQL database |

4. Render detects the `Procfile` and runs `gunicorn wsgi:app` automatically.

---

## Project Structure

```
quiz_app/
├── app.py              # Flask app factory + all routes
├── config.py           # Development / Production config classes
├── models.py           # SQLAlchemy User model
├── forms.py            # Flask-WTF register + login forms
├── wsgi.py             # Gunicorn entry point
├── Procfile            # Render deployment command
├── requirements.txt
├── .env.example        # Environment variable template
├── static/
│   ├── style.css       # All UI styles
│   └── quiz.js         # Quiz game logic (client-side only)
├── templates/
│   ├── layout.html     # Base template
│   ├── welcome.html    # Landing page
│   ├── register.html   # Registration form
│   ├── login.html      # Login form
│   └── quiz.html       # Protected quiz app
└── quiz_app.py         # Original terminal CLI version (standalone)
```

---

## Grading System

| Score | Grade |
|---|---|
| 100% | Perfect Score 🏆 |
| 80–99% | Excellent 🥇 |
| 60–79% | Good Job 🥈 |
| 40–59% | Needs Improvement 🥉 |
| Below 40% | Keep Practising 📖 |

---

## CLI Version

The original terminal quiz is still available and fully independent:

```bash
python quiz_app.py
```

---

## Future Improvements

- Real email OTP for two-factor authentication (Flask-Mail + SMTP)
- High-score leaderboard stored in the database
- Difficulty levels (Easy / Medium / Hard)
- Additional question categories

---

## License

MIT
