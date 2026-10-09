# PRACTICE — small "Notes" feature for trying the 3-tier process end to end.
# Written normally (no planted bugs). Not research data: do not log it in log.csv.
import os
import sqlite3

from flask import Flask, g, jsonify, request

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", os.urandom(32).hex())
app.config["DB"] = os.environ.get("NOTES_DB", "notes.db")

MAX_TITLE = 100
MAX_BODY = 2000

# Test tokens only. A real app would get these from its sign-in service.
TOKENS = {"token-alice": 1, "token-bob": 2}


def db():
    if "db" not in g:
        g.db = sqlite3.connect(app.config["DB"])
        g.db.row_factory = sqlite3.Row
    return g.db


@app.teardown_appcontext
def close_db(_exc):
    conn = g.pop("db", None)
    if conn is not None:
        conn.close()


def init_db():
    with app.app_context():
        db().execute(
            """CREATE TABLE IF NOT EXISTS notes(
                   id INTEGER PRIMARY KEY, user_id INT NOT NULL,
                   title TEXT NOT NULL, body TEXT NOT NULL DEFAULT '')"""
        )
        db().commit()


def current_user():
    header = request.headers.get("Authorization", "")
    if not header.startswith("Bearer "):
        return None
    return TOKENS.get(header.removeprefix("Bearer "))


@app.before_request
def require_login():
    g.uid = current_user()
    if g.uid is None:
        return jsonify({"error": "Please sign in again."}), 401


def error(message, status):
    return jsonify({"error": message}), status


@app.get("/notes")
def list_notes():
    rows = db().execute(
        "SELECT id, title, body FROM notes WHERE user_id=? ORDER BY id DESC", (g.uid,)
    ).fetchall()
    return jsonify([dict(r) for r in rows])


@app.get("/notes/<int:note_id>")
def get_note(note_id):
    row = db().execute(
        "SELECT id, title, body FROM notes WHERE id=? AND user_id=?", (note_id, g.uid)
    ).fetchone()
    if row is None:
        return error("Note not found.", 404)
    return jsonify(dict(row))


@app.post("/notes")
def create_note():
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return error("Request body must be a JSON object.", 400)
    title = data.get("title")
    body = data.get("body", "")
    if not isinstance(title, str) or not title.strip():
        return error("Title is required.", 400)
    if not isinstance(body, str):
        return error("Body must be text.", 400)
    if len(title) > MAX_TITLE or len(body) > MAX_BODY:
        return error(f"Title max {MAX_TITLE} characters, body max {MAX_BODY}.", 400)
    cur = db().execute(
        "INSERT INTO notes(user_id, title, body) VALUES (?,?,?)", (g.uid, title.strip(), body)
    )
    db().commit()
    return jsonify({"id": cur.lastrowid}), 201


@app.delete("/notes/<int:note_id>")
def delete_note(note_id):
    cur = db().execute("DELETE FROM notes WHERE id=? AND user_id=?", (note_id, g.uid))
    db().commit()
    if cur.rowcount == 0:
        return error("Note not found.", 404)
    return "", 204


@app.errorhandler(500)
def server_error(_e):
    return error("Something went wrong. Please try again.", 500)


init_db()

if __name__ == "__main__":
    app.run(port=5000)
