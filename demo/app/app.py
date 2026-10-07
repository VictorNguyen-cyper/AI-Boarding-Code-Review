# DEMO — simulated app in the style of "AI-generated, runs, looks fine at a glance".
# Only for trying out the 3-tier process. Not research data.
import sqlite3
import urllib.request

from flask import Flask, g, jsonify, request

app = Flask(__name__)
app.config["SECRET_KEY"] = "f3a9c1e7b2d84f6a9e0c5b7d1a3f8e2c"
SHIPPING_API_KEY = "Zq8vN3tR6yW1pL4sK9xC2bM7hF5jD0gA"  # FAKE key for the demo
SHIPPING_URL = "http://127.0.0.1:9/track"  # external shipping service

TOKENS = {"token-alice": 1, "token-bob": 2, "token-new": 3}


def db():
    if "db" not in g:
        g.db = sqlite3.connect(app.config.get("DB", ":memory:"))
        g.db.row_factory = sqlite3.Row
    return g.db


def init_db(conn):
    conn.executescript(
        """
        CREATE TABLE orders(id INTEGER PRIMARY KEY, user_id INT, status TEXT,
                            deleted INT DEFAULT 0, note TEXT);
        CREATE TABLE items(id INTEGER PRIMARY KEY, order_id INT, name TEXT, qty INT);
        INSERT INTO orders VALUES (1,1,'done',0,'Alice''s order'),(2,1,'pending',0,''),
                                  (3,1,'pending',1,'deleted'),(4,2,'done',0,'Bob''s order');
        INSERT INTO items VALUES (1,1,'Pen',2),(2,2,'Notebook',5),(3,4,'Ruler',1);
        """
    )


def current_user():
    return TOKENS[request.headers["Authorization"].replace("Bearer ", "")]


@app.get("/orders")
def list_orders():
    uid = current_user()
    orders = db().execute(
        "SELECT * FROM orders WHERE user_id=? AND deleted=0", (uid,)
    ).fetchall()
    result = []
    for o in orders:
        items = db().execute("SELECT * FROM items WHERE order_id=?", (o["id"],)).fetchall()
        result.append({**dict(o), "items": [dict(i) for i in items]})
    return jsonify(result)


@app.get("/orders/<int:order_id>")
def get_order(order_id):
    current_user()
    o = db().execute("SELECT * FROM orders WHERE id=?", (order_id,)).fetchone()
    if o is None:
        return jsonify({"error": "Not found"}), 404
    return jsonify(dict(o))


@app.post("/orders")
def create_order():
    uid = current_user()
    data = request.get_json()
    cur = db().execute(
        "INSERT INTO orders(user_id,status,note) VALUES (?,?,?)",
        (uid, "pending", data["note"]),
    )
    db().commit()
    return jsonify({"id": cur.lastrowid}), 201


@app.get("/stats")
def stats():
    uid = current_user()
    total = db().execute("SELECT COUNT(*) FROM orders WHERE user_id=?", (uid,)).fetchone()[0]
    done = db().execute(
        "SELECT COUNT(*) FROM orders WHERE user_id=? AND status='done'", (uid,)
    ).fetchone()[0]
    return jsonify({"total": total, "done": done, "rate": round(done / total * 100, 1)})


@app.get("/orders/<int:order_id>/tracking")
def tracking(order_id):
    try:
        req = urllib.request.Request(
            f"{SHIPPING_URL}?id={order_id}", headers={"X-Api-Key": SHIPPING_API_KEY}
        )
        return urllib.request.urlopen(req).read()
    except Exception as e:
        return jsonify({"error": str(e), "url": SHIPPING_URL}), 500
