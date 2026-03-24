import sqlite3
import os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'emotions.db')


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Initialize database and create tables if they don't exist."""
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            email TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS emotion_sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            emotion TEXT NOT NULL,
            confidence REAL DEFAULT 0.0,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS recommendations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id INTEGER NOT NULL,
            movie_title TEXT NOT NULL,
            genre TEXT,
            year INTEGER,
            rating REAL,
            FOREIGN KEY (session_id) REFERENCES emotion_sessions(id)
        )
    ''')

    conn.commit()
    conn.close()
    print("[DB] Database initialized successfully.")


# ──────────────────────────── User helpers ──────────────────────────────────

def create_user(username, password_hash, email=None):
    try:
        conn = get_db()
        conn.execute(
            "INSERT INTO users (username, password_hash, email) VALUES (?, ?, ?)",
            (username, password_hash, email)
        )
        conn.commit()
        conn.close()
        return True
    except sqlite3.IntegrityError:
        return False  # Username already exists


def get_user_by_username(username):
    conn = get_db()
    user = conn.execute(
        "SELECT * FROM users WHERE username = ?", (username,)
    ).fetchone()
    conn.close()
    return user


def get_user_by_id(user_id):
    conn = get_db()
    user = conn.execute(
        "SELECT * FROM users WHERE id = ?", (user_id,)
    ).fetchone()
    conn.close()
    return user


# ─────────────────────── Emotion session helpers ────────────────────────────

def save_emotion_session(user_id, emotion, confidence):
    """Save a detected emotion session and return its ID."""
    conn = get_db()
    cursor = conn.execute(
        "INSERT INTO emotion_sessions (user_id, emotion, confidence) VALUES (?, ?, ?)",
        (user_id, emotion, confidence)
    )
    session_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return session_id


def save_recommendations(session_id, movies):
    """Save recommended movies for a session."""
    conn = get_db()
    for movie in movies:
        conn.execute(
            "INSERT INTO recommendations (session_id, movie_title, genre, year, rating) VALUES (?, ?, ?, ?, ?)",
            (session_id, movie['title'], movie.get('genre', ''), movie.get('year', 0), movie.get('rating', 0.0))
        )
    conn.commit()
    conn.close()


def get_user_history(user_id, limit=20):
    """Get past emotion sessions with their recommendations."""
    conn = get_db()
    sessions = conn.execute(
        """SELECT es.id, es.emotion, es.confidence, es.timestamp,
                  GROUP_CONCAT(r.movie_title, '||') as movies,
                  GROUP_CONCAT(r.genre, '||') as genres
           FROM emotion_sessions es
           LEFT JOIN recommendations r ON r.session_id = es.id
           WHERE es.user_id = ?
           GROUP BY es.id
           ORDER BY es.timestamp DESC
           LIMIT ?""",
        (user_id, limit)
    ).fetchall()
    conn.close()
    return sessions


def get_emotion_stats(user_id):
    """Get emotion frequency stats for a user."""
    conn = get_db()
    stats = conn.execute(
        """SELECT emotion, COUNT(*) as count
           FROM emotion_sessions
           WHERE user_id = ?
           GROUP BY emotion
           ORDER BY count DESC""",
        (user_id,)
    ).fetchall()
    conn.close()
    return stats
