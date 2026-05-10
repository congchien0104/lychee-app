import json, os, time
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs
import psycopg2, psycopg2.extras

# ── DB connection ──────────────────────────────────────────────────────────────
def get_db():
    database_url = os.getenv("DATABASE_URL")
    if database_url:
        url = database_url.replace("postgres://", "postgresql://", 1)
        return psycopg2.connect(url, cursor_factory=psycopg2.extras.RealDictCursor)
    return psycopg2.connect(
        host=os.getenv("DB_HOST", "db"),
        port=os.getenv("DB_PORT", "5432"),
        user=os.getenv("DB_USER", "postgres"),
        password=os.getenv("DB_PASSWORD", "postgres"),
        dbname=os.getenv("DB_NAME", "lycheedb"),
        cursor_factory=psycopg2.extras.RealDictCursor,
    )

def init_db():
    conn = get_db(); cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id SERIAL PRIMARY KEY, name VARCHAR(255) NOT NULL,
            name_vn VARCHAR(255), description TEXT,
            price DECIMAL(10,2) NOT NULL, unit VARCHAR(50) DEFAULT 'kg',
            stock INTEGER DEFAULT 0, category VARCHAR(100),
            image_emoji VARCHAR(10) DEFAULT '🍈',
            featured BOOLEAN DEFAULT FALSE, created_at TIMESTAMPTZ DEFAULT NOW()
        );
        CREATE TABLE IF NOT EXISTS orders (
            id SERIAL PRIMARY KEY, name VARCHAR(255) NOT NULL,
            email VARCHAR(255) NOT NULL, phone VARCHAR(50),
            address TEXT, total DECIMAL(10,2) NOT NULL,
            status VARCHAR(50) DEFAULT 'pending', created_at TIMESTAMPTZ DEFAULT NOW()
        );
        CREATE TABLE IF NOT EXISTS order_items (
            id SERIAL PRIMARY KEY,
            order_id INTEGER REFERENCES orders(id) ON DELETE CASCADE,
            product_id INTEGER REFERENCES products(id),
            name VARCHAR(255), quantity INTEGER NOT NULL, price DECIMAL(10,2) NOT NULL
        );
        CREATE TABLE IF NOT EXISTS reviews (
            id SERIAL PRIMARY KEY,
            product_id INTEGER REFERENCES products(id) ON DELETE CASCADE,
            author VARCHAR(255) NOT NULL,
            rating INTEGER CHECK (rating BETWEEN 1 AND 5),
            comment TEXT, created_at TIMESTAMPTZ DEFAULT NOW()
        );
    """)
    cur.execute("SELECT COUNT(*) as n FROM products")
    if cur.fetchone()["n"] == 0:
        print("🌱 Seeding database...")
        products = [
            ("Fresh Lychee","Vải tươi","Premium fresh lychee from Bac Giang. Sweet, juicy with thin skin and small seed.",85000,"kg",150,"fresh","🍈",True),
            ("Lychee Gift Box 1kg","Hộp quà vải 1kg","Beautiful gift box with 1kg premium lychee. Perfect for gifting.",120000,"box",50,"gift","🎁",True),
            ("Dried Lychee","Vải sấy khô","Sun-dried lychee with no preservatives. Chewy, naturally sweet.",95000,"200g",200,"dried","🍂",False),
            ("Lychee Gift Box 3kg","Hộp quà vải 3kg","Premium 3kg gift box. Beautiful packaging, ideal for holidays.",320000,"box",30,"gift","🎁",True),
            ("Lychee Jam","Mứt vải","Homemade lychee jam with natural sweetness. No artificial flavors.",75000,"jar",80,"processed","🍯",False),
            ("Lychee Wine","Rượu vải","Traditional lychee wine, 12% ABV. Smooth and fragrant.",180000,"500ml",40,"beverage","🍷",True),
            ("Lychee Honey","Mật ong vải","Pure monofloral lychee blossom honey. Raw and unfiltered.",145000,"250g",60,"processed","🍯",False),
            ("Frozen Lychee","Vải đông lạnh","IQF frozen lychee, peeled and seeded. Ready for smoothies.",70000,"500g",120,"frozen","❄️",False),
        ]
        for p in products:
            cur.execute("INSERT INTO products (name,name_vn,description,price,unit,stock,category,image_emoji,featured) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)", p)
        cur.execute("SELECT id FROM products LIMIT 2")
        pids = [r["id"] for r in cur.fetchall()]
        for pid, author, rating, comment in [
            (pids[0],"Nguyễn Thị Lan",5,"Vải rất ngon, tươi và ngọt. Giao hàng nhanh!"),
            (pids[0],"Trần Văn Minh",5,"Đặt lần 2 rồi, chất lượng ổn định."),
            (pids[1],"Phạm Thu Hà",5,"Mua làm quà biếu, đóng gói đẹp lắm!"),
        ]:
            cur.execute("INSERT INTO reviews (product_id,author,rating,comment) VALUES (%s,%s,%s,%s)", (pid,author,rating,comment))
    conn.commit(); conn.close()
    print("✅ Database ready")

def wait_for_db():
    for i in range(15):
        try:
            c = get_db(); c.close()
            print("✅ Connected to database"); return
        except Exception as e:
            print(f"⏳ Waiting ({i+1}/15): {e}"); time.sleep(5)
    raise RuntimeError("❌ Cannot connect to database")

ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "*")

def send_json(h, status, data):
    body = json.dumps(data, default=str).encode()
    origin = h.headers.get("Origin", "*")
    cors_origin = "*" if ALLOWED_ORIGINS == "*" else origin
    h.send_response(status)
    h.send_header("Content-Type", "application/json")
    h.send_header("Access-Control-Allow-Origin", cors_origin)
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

class Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *a): print(f"  {self.command} {self.path} → {a[1]}")

    def do_OPTIONS(self):
        origin = self.headers.get("Origin", "*")
        cors_origin = "*" if ALLOWED_ORIGINS == "*" else origin
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", cors_origin)
        self.send_header("Access-Control-Allow-Methods", "GET,POST,PUT,DELETE,OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_GET(self):
        p = urlparse(self.path); path, qs = p.path, parse_qs(p.query)
        if path == "/api/health": send_json(self, 200, {"status":"ok"})
        elif path in ("/api/products","/api/products/"): self.list_products(qs)
        elif path.startswith("/api/products/") and path.endswith("/reviews"):
            self.get_reviews(int(path.split("/")[-2]))
        elif path.startswith("/api/products/") and parse_id(path): self.get_product(parse_id(path))
        elif path == "/api/featured": self.featured_products()
        elif path == "/api/stats": self.get_stats()
        elif path in ("/api/orders","/api/orders/"): self.list_orders()
        else: send_json(self, 404, {"error":"not found"})

    def do_POST(self):
        p = self.path.rstrip("/")
        if p == "/api/orders": self.create_order()
        elif p.endswith("/reviews"): self.create_review(int(p.split("/")[-2]))
        else: send_json(self, 404, {"error":"not found"})

    def list_products(self, qs):
        conn = get_db(); cur = conn.cursor()
        cat = qs.get("category",[None])[0]
        if cat: cur.execute("SELECT * FROM products WHERE category=%s ORDER BY featured DESC,id",(cat,))
        else: cur.execute("SELECT * FROM products ORDER BY featured DESC,id")
        rows = [dict(r) for r in cur.fetchall()]; conn.close()
        send_json(self, 200, rows)

    def get_product(self, pid):
        conn = get_db(); cur = conn.cursor()
        cur.execute("SELECT * FROM products WHERE id=%s",(pid,))
        row = cur.fetchone(); conn.close()
        if not row: send_json(self,404,{"error":"not found"}); return
        send_json(self, 200, dict(row))

    def featured_products(self):
        conn = get_db(); cur = conn.cursor()
        cur.execute("SELECT * FROM products WHERE featured=TRUE ORDER BY id LIMIT 4")
        rows = [dict(r) for r in cur.fetchall()]; conn.close()
        send_json(self, 200, rows)

    def get_reviews(self, pid):
        conn = get_db(); cur = conn.cursor()
        cur.execute("SELECT * FROM reviews WHERE product_id=%s ORDER BY created_at DESC",(pid,))
        rows = [dict(r) for r in cur.fetchall()]; conn.close()
        send_json(self, 200, rows)

    def create_review(self, pid):
        body = read_body(self)
        if not body.get("author") or not body.get("rating"):
            send_json(self,400,{"error":"author and rating required"}); return
        conn = get_db(); cur = conn.cursor()
        cur.execute("INSERT INTO reviews (product_id,author,rating,comment) VALUES (%s,%s,%s,%s) RETURNING *",
            (pid,body["author"],int(body["rating"]),body.get("comment","")))
        row = dict(cur.fetchone()); conn.commit(); conn.close()
        send_json(self, 201, row)

    def list_orders(self):
        conn = get_db(); cur = conn.cursor()
        cur.execute("SELECT * FROM orders ORDER BY created_at DESC LIMIT 50")
        rows = [dict(r) for r in cur.fetchall()]; conn.close()
        send_json(self, 200, rows)

    def create_order(self):
        body = read_body(self)
        if not body.get("name") or not body.get("email") or not body.get("items"):
            send_json(self,400,{"error":"name, email, items required"}); return
        items = body["items"]
        total = sum(i["price"]*i["quantity"] for i in items)
        conn = get_db(); cur = conn.cursor()
        cur.execute("INSERT INTO orders (name,email,phone,address,total) VALUES (%s,%s,%s,%s,%s) RETURNING id,total,status,created_at",
            (body["name"],body["email"],body.get("phone",""),body.get("address",""),total))
        order = dict(cur.fetchone())
        for item in items:
            cur.execute("INSERT INTO order_items (order_id,product_id,name,quantity,price) VALUES (%s,%s,%s,%s,%s)",
                (order["id"],item.get("product_id"),item.get("name"),item["quantity"],item["price"]))
        conn.commit(); conn.close()
        send_json(self, 201, {"order":order,"message":"Order placed successfully! 🎉"})

    def get_stats(self):
        conn = get_db(); cur = conn.cursor()
        cur.execute("SELECT COUNT(*) as n FROM products"); p=cur.fetchone()
        cur.execute("SELECT COUNT(*) as n FROM orders"); o=cur.fetchone()
        cur.execute("SELECT COUNT(*) as n FROM reviews"); r=cur.fetchone()
        cur.execute("SELECT AVG(rating) as a FROM reviews"); avg=cur.fetchone()
        conn.close()
        send_json(self,200,{"products":p["n"],"orders":o["n"],"reviews":r["n"],
                             "avg_rating":round(float(avg["a"] or 0),1)})

if __name__ == "__main__":
    port = int(os.getenv("PORT", 10000))
    print(f"Starting Lychee backend on port {port}...")

    import threading
    server = HTTPServer(("0.0.0.0", port), Handler)
    print(f"HTTP server listening on 0.0.0.0:{port}")

    def setup_db():
        try:
            wait_for_db()
            init_db()
            print("Database setup complete")
        except Exception as e:
            print(f"DB setup failed: {e}")

    threading.Thread(target=setup_db, daemon=True).start()
    server.serve_forever()