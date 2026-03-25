"""
app.py  –  Emotion-Aware Movie Recommendation Website
Flask backend entry point.

Routes:
  GET  /                         → Home / webcam detection page
  POST /detect                   → Detect emotion from base64 frame
  GET  /recommend/<emotion>      → Movie recommendations page
  GET  /api/movies/<emotion>     → JSON API for movies
  GET  /history                  → User's past sessions
  GET/POST /register             → User registration
  GET/POST /login                → User login
  GET  /logout                   → Logout
"""

import os
import json
from datetime import datetime

from flask import (
    Flask, render_template, request, redirect,
    url_for, session, jsonify, flash
)
from werkzeug.security import generate_password_hash, check_password_hash

from database import init_db, create_user, get_user_by_username, get_user_by_id
from database import save_emotion_session, save_recommendations, get_user_history, get_emotion_stats
from emotion_detector import detect_emotion
from movies_db import get_movies_for_emotion, get_all_emotions, EMOTION_META

# ────────────────────────────────────────────────────────────────────────────
# App setup
# ────────────────────────────────────────────────────────────────────────────

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "emotion-movie-secret-2025-sgbau")

# Initialise the database on startup
with app.app_context():
    init_db()


# ────────────────────────────────────────────────────────────────────────────
# Helpers
# ────────────────────────────────────────────────────────────────────────────

def current_user():
    """Return current logged-in user dict or None."""
    uid = session.get("user_id")
    if uid:
        user = get_user_by_id(uid)
        if user:
            return dict(user)
    return None


def login_required(f):
    """Decorator: redirect to login if not authenticated."""
    from functools import wraps
    @wraps(f)
    def wrapper(*args, **kwargs):
        if not current_user():
            flash("Please log in to continue.", "warning")
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return wrapper


# ────────────────────────────────────────────────────────────────────────────
# Context processor – inject user into all templates
# ────────────────────────────────────────────────────────────────────────────

@app.context_processor
def inject_user():
    return {"user": current_user(), "emotion_meta": EMOTION_META}


# ────────────────────────────────────────────────────────────────────────────
# Main routes
# ────────────────────────────────────────────────────────────────────────────

@app.route("/")
def index():
    emotions = get_all_emotions()
    return render_template("index.html", emotions=emotions, emotion_meta=EMOTION_META)


@app.route("/detect", methods=["POST"])
def detect():
    """
    Receive a base64-encoded image frame from JavaScript,
    run emotion detection, save to DB, return JSON.
    """
    data = request.get_json(silent=True) or {}
    b64_image = data.get("image", "")

    if not b64_image:
        return jsonify({"error": "No image data received."}), 400

    result = detect_emotion(b64_image)
    emotion = result["emotion"]
    confidence = result["confidence"]

    # Save session to DB if user is logged in
    uid = session.get("user_id")
    session_id = None
    if uid:
        try:
            session_id = save_emotion_session(uid, emotion, confidence)
            movies = get_movies_for_emotion(emotion, count=12)
            save_recommendations(session_id, movies)
        except Exception as e:
            print(f"[app] DB save error: {e}")

    meta = EMOTION_META.get(emotion, EMOTION_META["neutral"])
    return jsonify({
        "emotion": emotion,
        "confidence": confidence,
        "all_scores": result.get("all_scores", {}),
        "face_detected": result.get("face_detected", False),
        "method": result.get("method", "unknown"),
        "icon": meta["icon"],
        "color": meta["color"],
        "label": meta["label"],
        "tip": meta["tip"],
        "session_id": session_id,
        "redirect_url": url_for("recommend", emotion=emotion)
    })


@app.route("/recommend/<emotion>")
def recommend(emotion):
    """Show movie recommendations for a given emotion."""
    valid = get_all_emotions()
    if emotion not in valid:
        emotion = "neutral"

    movies = get_movies_for_emotion(emotion, count=12)
    meta = EMOTION_META.get(emotion, EMOTION_META["neutral"])
    return render_template(
        "recommend.html",
        emotion=emotion,
        movies=movies,
        meta=meta,
        other_emotions=valid
    )


@app.route("/api/movies/<emotion>")
def api_movies(emotion):
    """JSON API endpoint for movie recommendations."""
    movies = get_movies_for_emotion(emotion, count=12)
    meta = EMOTION_META.get(emotion, EMOTION_META.get("neutral"))
    return jsonify({"emotion": emotion, "meta": meta, "movies": movies})


@app.route("/history")
@login_required
def history():
    uid = session["user_id"]
    sessions = get_user_history(uid)
    stats = get_emotion_stats(uid)
    history_data = []
    for s in sessions:
        movies = []
        if s["movies"]:
            titles = s["movies"].split("||")
            genres = (s["genres"] or "").split("||")
            for i, title in enumerate(titles):
                if title:
                    movies.append({
                        "title": title,
                        "genre": genres[i] if i < len(genres) else ""
                    })
        meta = EMOTION_META.get(s["emotion"], EMOTION_META["neutral"])
        history_data.append({
            "id": s["id"],
            "emotion": s["emotion"],
            "confidence": s["confidence"],
            "timestamp": s["timestamp"],
            "movies": movies[:4],
            "icon": meta["icon"],
            "color": meta["color"],
            "label": meta["label"],
        })
    return render_template("history.html", history=history_data, stats=list(stats), emotion_meta=EMOTION_META)


@app.route("/clear_history")
@login_required
def clear_history():
    uid = session["user_id"]
    conn = get_db()
    conn.execute("DELETE FROM recommendations WHERE session_id IN (SELECT id FROM emotion_sessions WHERE user_id = ?)", (uid,))
    conn.execute("DELETE FROM emotion_sessions WHERE user_id = ?", (uid,))
    conn.commit()
    conn.close()
    flash("Your emotion history has been cleared.", "info")
    return redirect(url_for("history"))


# ────────────────────────────────────────────────────────────────────────────
# Auth routes
# ────────────────────────────────────────────────────────────────────────────

@app.route("/register", methods=["GET", "POST"])
def register():
    if current_user():
        return redirect(url_for("index"))

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        confirm  = request.form.get("confirm", "")
        email    = request.form.get("email", "").strip()

        error = None
        if not username or len(username) < 3:
            error = "Username must be at least 3 characters."
        elif not password or len(password) < 6:
            error = "Password must be at least 6 characters."
        elif password != confirm:
            error = "Passwords do not match."

        if error:
            flash(error, "error")
            return render_template("register.html")

        pw_hash = generate_password_hash(password)
        success = create_user(username, pw_hash, email or None)

        if success:
            user = get_user_by_username(username)
            session["user_id"] = user["id"]
            flash(f"Welcome, {username}! Your account has been created.", "success")
            return redirect(url_for("index"))
        else:
            flash("Username already taken. Please choose another.", "error")

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user():
        return redirect(url_for("index"))

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        user = get_user_by_username(username)
        if user and check_password_hash(user["password_hash"], password):
            session["user_id"] = user["id"]
            flash(f"Welcome back, {username}!", "success")
            return redirect(url_for("index"))
        else:
            flash("Invalid username or password.", "error")

    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for("index"))


# ────────────────────────────────────────────────────────────────────────────
# Error handlers
# ────────────────────────────────────────────────────────────────────────────

@app.errorhandler(404)
def not_found(e):
    return render_template("index.html"), 404


# ────────────────────────────────────────────────────────────────────────────
# Run
# ────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("\n" + "="*55)
    print("  [MoodFlick] Emotion-Aware Movie Recommendation")
    print("  Running on: http://127.0.0.1:5000")
    print("  Emotion Detection: FER (ML) + OpenCV fallback")
    print("  Database: SQLite (emotions.db)")
    print("="*55 + "\n")
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=False, host="0.0.0.0", port=port)
