import json, os, time
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs
import psycopg2, psycopg2.extras

# ── DB ─────────────────────────────────────────────────────────────────────────
def get_db():
    return psycopg2.connect(
        host=os.getenv("DB_HOST", "db"),
        port=os.getenv("DB_PORT", "5432"),
        user=os.getenv("DB_USER", "postgres"),
        password=os.getenv("DB_PASSWORD", "postgres"),
        dbname=os.getenv("DB_NAME", "lycheedb"),
        cursor_factory=psycopg2.extras.RealDictCursor,
    )

def wait_for_db():
    for i in range(15):
        try:
            c = get_db(); c.close()
            print("✅ Connected to PostgreSQL"); return
        except Exception as e:
            print(f"⏳ Waiting for db ({i+1}/15)..."); time.sleep(2)
    raise RuntimeError("❌ Cannot connect to database")

# ── Helpers ────────────────────────────────────────────────────────────────────
def send_json(h, status, data):
    body = json.dumps(data, default=str).encode()
    h.send_response(status)
    h.send_header("Content-Type", "application/json")
    h.send_header("Access-Control-Allow-Origin", "*")
    h.send_header("Access-Control-Allow-Methods", "GET,POST,PUT,DELETE,OPTIONS")
    h.send_header("Access-Control-Allow-Headers", "Content-Type")
    h.send_header("Content-Length", len(body))
    h.end_headers(); h.wfile.write(body)

def read_body(h):
    n = int(h.headers.get("Content-Length", 0))
    return json.loads(h.rfile.read(n)) if n else {}

def parse_id(path):
    parts = path.rstrip("/").split("/")
    try: return int(parts[-1])
    except: return None

# ── Handler ────────────────────────────────────────────────────────────────────
class Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *a): print(f"  {self.command} {self.path} → {a[1]}")

    def do_OPTIONS(self):
        self.send_response(204)
        for k,v in [("Access-Control-Allow-Origin","*"),
                    ("Access-Control-Allow-Methods","GET,POST,PUT,DELETE,OPTIONS"),
                    ("Access-Control-Allow-Headers","Content-Type")]:
            self.send_header(k,v)
        self.end_headers()

    def do_GET(self):
        p = urlparse(self.path)
        path, qs = p.path, parse_qs(p.query)

        if path == "/api/health":
            send_json(self, 200, {"status": "ok", "service": "lychee-backend"})

        elif path in ("/api/products", "/api/products/"):
            self.list_products(qs)

        elif path.startswith("/api/products/") and parse_id(path):
            self.get_product(parse_id(path))

        elif path.startswith("/api/products/") and path.endswith("/reviews"):
            pid = int(path.split("/")[-2])
            self.get_reviews(pid)

        elif path in ("/api/featured",):
            self.featured_products()

        elif path in ("/api/stats",):
            self.get_stats()

        elif path in ("/api/orders", "/api/orders/"):
            self.list_orders()

        else:
            send_json(self, 404, {"error": "not found"})

    def do_POST(self):
        p = self.path.rstrip("/")
        if p == "/api/orders":
            self.create_order()
        elif p.endswith("/reviews"):
            pid = int(p.split("/")[-2])
            self.create_review(pid)
        else:
            send_json(self, 404, {"error": "not found"})

    # ── Products ──────────────────────────────────────────────────────────────
    def list_products(self, qs):
        conn = get_db(); cur = conn.cursor()
        cat = qs.get("category", [None])[0]
        if cat:
            cur.execute("SELECT * FROM products WHERE category=%s ORDER BY featured DESC, id", (cat,))
        else:
            cur.execute("SELECT * FROM products ORDER BY featured DESC, id")
        rows = [dict(r) for r in cur.fetchall()]; conn.close()
        send_json(self, 200, rows)

    def get_product(self, pid):
        conn = get_db(); cur = conn.cursor()
        cur.execute("SELECT * FROM products WHERE id=%s", (pid,))
        row = cur.fetchone(); conn.close()
        if not row: send_json(self, 404, {"error": "not found"}); return
        send_json(self, 200, dict(row))

    def featured_products(self):
        conn = get_db(); cur = conn.cursor()
        cur.execute("SELECT * FROM products WHERE featured=TRUE ORDER BY id LIMIT 4")
        rows = [dict(r) for r in cur.fetchall()]; conn.close()
        send_json(self, 200, rows)

    # ── Reviews ───────────────────────────────────────────────────────────────
    def get_reviews(self, pid):
        conn = get_db(); cur = conn.cursor()
        cur.execute("SELECT * FROM reviews WHERE product_id=%s ORDER BY created_at DESC", (pid,))
        rows = [dict(r) for r in cur.fetchall()]; conn.close()
        send_json(self, 200, rows)

    def create_review(self, pid):
        body = read_body(self)
        if not body.get("author") or not body.get("rating"):
            send_json(self, 400, {"error": "author and rating required"}); return
        conn = get_db(); cur = conn.cursor()
        cur.execute(
            "INSERT INTO reviews (product_id,author,rating,comment) VALUES (%s,%s,%s,%s) RETURNING *",
            (pid, body["author"], int(body["rating"]), body.get("comment",""))
        )
        row = dict(cur.fetchone()); conn.commit(); conn.close()
        send_json(self, 201, row)

    # ── Orders ────────────────────────────────────────────────────────────────
    def list_orders(self):
        conn = get_db(); cur = conn.cursor()
        cur.execute("SELECT * FROM orders ORDER BY created_at DESC LIMIT 50")
        rows = [dict(r) for r in cur.fetchall()]; conn.close()
        send_json(self, 200, rows)

    def create_order(self):
        body = read_body(self)
        if not body.get("name") or not body.get("email") or not body.get("items"):
            send_json(self, 400, {"error": "name, email, items required"}); return
        items = body["items"]
        total = sum(i["price"] * i["quantity"] for i in items)
        conn = get_db(); cur = conn.cursor()
        cur.execute(
            "INSERT INTO orders (name,email,phone,address,total) VALUES (%s,%s,%s,%s,%s) RETURNING id,total,status,created_at",
            (body["name"], body["email"], body.get("phone",""), body.get("address",""), total)
        )
        order = dict(cur.fetchone())
        for item in items:
            cur.execute(
                "INSERT INTO order_items (order_id,product_id,name,quantity,price) VALUES (%s,%s,%s,%s,%s)",
                (order["id"], item.get("product_id"), item.get("name"), item["quantity"], item["price"])
            )
        conn.commit(); conn.close()
        send_json(self, 201, {"order": order, "message": "Order placed successfully! 🎉"})

    # ── Stats ─────────────────────────────────────────────────────────────────
    def get_stats(self):
        conn = get_db(); cur = conn.cursor()
        cur.execute("SELECT COUNT(*) as products FROM products")
        p = cur.fetchone()
        cur.execute("SELECT COUNT(*) as orders FROM orders")
        o = cur.fetchone()
        cur.execute("SELECT COUNT(*) as reviews FROM reviews")
        r = cur.fetchone()
        cur.execute("SELECT AVG(rating) as avg_rating FROM reviews")
        avg = cur.fetchone()
        conn.close()
        send_json(self, 200, {
            "products": p["products"],
            "orders": o["orders"],
            "reviews": r["reviews"],
            "avg_rating": round(float(avg["avg_rating"] or 0), 1)
        })

# ── Main ───────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    wait_for_db()
    port = int(os.getenv("PORT", 8080))
    print(f"🚀 Lychee backend on :{port}")
    HTTPServer(("0.0.0.0", port), Handler).serve_forever()
