import json, os, time
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs
import psycopg2, psycopg2.extras

def get_db():
    database_url = os.getenv("DATABASE_URL")
    if database_url:
        url = database_url.replace("postgres://", "postgresql://", 1)
        return psycopg2.connect(url, cursor_factory=psycopg2.extras.RealDictCursor)
    return psycopg2.connect(
        host=os.getenv("DB_HOST", "db"), port=os.getenv("DB_PORT", "5432"),
        user=os.getenv("DB_USER", "postgres"), password=os.getenv("DB_PASSWORD", "postgres"),
        dbname=os.getenv("DB_NAME", "lycheedb"), cursor_factory=psycopg2.extras.RealDictCursor,
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
        print("🌱 Seeding 50 products...")
        products = [
            # 🌿 TƯƠI
            ("Fresh Lychee Premium","Vải Tươi Cao Cấp","Vải thiều Lục Ngạn loại 1. Hái buổi sáng, giao trong ngày. Vỏ đỏ tươi, hạt nhỏ, thịt dày, ngọt thanh.",85000,"kg",200,"fresh","🍈",True),
            ("Fresh Lychee Standard","Vải Tươi Thường","Vải thiều Bắc Giang loại 2. Chất lượng tốt, giá hợp lý. Phù hợp mua số lượng lớn.",65000,"kg",350,"fresh","🍈",False),
            ("Fresh Lychee Early Season","Vải Tươi Đầu Mùa","Vải đầu mùa tháng 5, hàng hiếm. Vị ngọt dịu, thơm đặc trưng. Số lượng có hạn mỗi ngày.",120000,"kg",80,"fresh","🍈",True),
            ("Fresh Lychee Late Season","Vải Tươi Cuối Mùa","Vải cuối mùa tháng 7, đường tập trung cao nhất. Ngọt đậm, thơm lâu.",95000,"kg",120,"fresh","🍈",False),
            ("Lychee Bunch on Branch","Vải Cành Nguyên Cành","Vải còn nguyên cành lá xanh. Trưng bày đẹp mắt, độ tươi kéo dài 2-3 ngày. Lý tưởng làm quà.",150000,"kg",60,"fresh","🌿",True),
            ("Seedless Lychee","Vải Không Hạt","Giống vải đặc biệt không hạt, thịt dày. Cực kỳ hiếm, chỉ có tại vườn nhà. Trải nghiệm ăn vải khác biệt.",200000,"kg",40,"fresh","🍈",True),
            ("Mini Lychee","Vải Bi Nhỏ","Giống vải bi hạt nhỏ tí, thịt dày hơn vải thường. Ngọt sắc, ăn không ngán. Được trẻ em yêu thích.",90000,"kg",100,"fresh","🍈",False),
            ("Organic Lychee","Vải Hữu Cơ","Vải canh tác hữu cơ 100%, không thuốc trừ sâu, không phân hóa học. Có chứng nhận VietGAP.",160000,"kg",75,"fresh","🌱",True),
            ("Fresh Lychee 5kg Pack","Vải Tươi Túi 5kg","Túi vải tươi 5kg giá ưu đãi. Tiết kiệm 15% so với mua lẻ. Giao nguyên túi, đóng gói kỹ càng.",380000,"túi",50,"fresh","🍈",False),
            ("Fresh Lychee 10kg Pack","Vải Tươi Thùng 10kg","Thùng 10kg cho gia đình đông người hoặc buôn bán nhỏ. Giá tốt nhất, giao nhanh.",700000,"thùng",30,"fresh","📦",False),
            # 🎁 QUÀ TẶNG
            ("Gift Box 500g Premium","Hộp Quà Vải 500g Cao Cấp","Hộp quà 500g thiết kế sang trọng. In tên theo yêu cầu. Kèm thiệp chúc mừng viết tay.",85000,"hộp",80,"gift","🎁",False),
            ("Gift Box 1kg Classic","Hộp Quà Vải 1kg","Hộp quà 1kg vải thiều cao cấp, đóng gói đẹp. Kèm túi đá lạnh giữ tươi. Phù hợp biếu tặng.",120000,"hộp",100,"gift","🎁",True),
            ("Gift Box 2kg Deluxe","Hộp Quà Vải 2kg Deluxe","Hộp quà 2kg cao cấp, hộp gỗ tự nhiên. Bên trong lót vải nhung đỏ. Sang trọng, phù hợp biếu sếp.",250000,"hộp",60,"gift","🎁",True),
            ("Gift Box 3kg Premium","Hộp Quà Vải 3kg Cao Cấp","Hộp quà 3kg sang trọng, thiết kế lụa đỏ. Vải hạng A tuyển chọn kỹ. Kèm thư pháp lời chúc.",320000,"hộp",45,"gift","🎁",True),
            ("Gift Basket 2kg","Giỏ Quà Vải 2kg","Giỏ tre thủ công đan tay, chứa 2kg vải thiều. Kết hợp cùng mật ong vải và mứt vải. Quà tết ý nghĩa.",380000,"giỏ",35,"gift","🧺",True),
            ("Corporate Gift 5kg","Quà Doanh Nghiệp 5kg","Bộ quà tặng doanh nghiệp 5kg vải cao cấp. In logo công ty, kèm brochure. Giảm 10% cho đơn 20 hộp.",550000,"hộp",25,"gift","🏢",False),
            ("Gift Set Lychee Trio","Bộ Quà 3 Trong 1","Combo: 500g vải tươi + mứt vải 200g + mật ong vải 150g. Hộp quà thiết kế đẹp, tặng Tết/sinh nhật.",280000,"set",40,"gift","🎀",False),
            ("Wedding Favor Box","Hộp Quà Cưới Vải Thiều","Hộp quà mini 200g cho tiệc cưới, in tên cô dâu chú rể. Đặt từ 50 hộp. Giao trước ngày cưới 3 ngày.",45000,"hộp",200,"gift","💍",False),
            ("Tet Premium Box","Hộp Quà Tết Vải Cao Cấp","Hộp quà Tết: 1kg vải sấy + rượu vải mini + mật ong vải. Hộp thiết kế phong thủy đỏ vàng.",450000,"hộp",30,"gift","🧧",False),
            ("Teacher Day Gift","Quà Tặng Thầy Cô","Bộ quà Ngày Nhà Giáo: hộp vải 1kg + túi trà vải + thiệp in sẵn. Giao tận trường.",180000,"set",50,"gift","📚",False),
            # 🍂 SẤY KHÔ
            ("Dried Lychee Classic","Vải Sấy Khô Truyền Thống","Vải sấy khô bằng phương pháp truyền thống, không chất bảo quản. Dai ngọt tự nhiên. Để được 6 tháng.",95000,"200g",300,"dried","🍂",False),
            ("Dried Lychee Crispy","Vải Sấy Giòn","Vải sấy giòn bằng công nghệ sấy lạnh. Giòn tan, ngọt nhẹ, không mất chất dinh dưỡng. Ăn vặt sức khỏe.",110000,"150g",200,"dried","🍂",True),
            ("Dried Lychee 500g","Vải Sấy Túi 500g","Túi lớn 500g vải sấy khô, tiết kiệm. Đóng gói zip-lock giữ độ giòn. Phù hợp gia đình và văn phòng.",200000,"500g",150,"dried","🍂",False),
            ("Lychee Trail Mix","Hỗn Hợp Trái Cây Vải","Hỗn hợp vải sấy + hạt điều + hạnh nhân + nho khô. Snack dinh dưỡng cho dân văn phòng.",135000,"200g",120,"dried","🥗",False),
            ("Dried Lychee Sugar Coated","Vải Sấy Phủ Đường","Vải sấy phủ lớp đường mỏng, đóng thành viên tròn đẹp. Ăn vặt dịp lễ tết, làm quà nhỏ xinh.",85000,"150g",180,"dried","🍬",False),
            ("Lychee Chips","Chip Vải","Vải sấy lát mỏng kiểu chip, giòn rụm. Vị ngọt chua nhẹ tự nhiên. Không chiên, không dầu mỡ.",90000,"100g",160,"dried","🍟",False),
            ("Dried Lychee Gift Tin","Hộp Thiếc Vải Sấy","Vải sấy đóng hộp thiếc sang trọng, 300g. Hộp có thể tái sử dụng. Quà tặng ý nghĩa.",180000,"hộp",90,"dried","🥫",False),
            ("Organic Dried Lychee","Vải Sấy Hữu Cơ","Vải hữu cơ VietGAP sấy khô. Không đường, không chất bảo quản. Phù hợp người ăn kiêng, tiểu đường.",150000,"150g",80,"dried","🌿",False),
            # 🍯 CHẾ BIẾN
            ("Lychee Jam 250g","Mứt Vải 250g","Mứt vải nấu thủ công từ vải tươi Bắc Giang. Không chất bảo quản, ngọt tự nhiên. Ăn kèm bánh mì, bánh quy.",75000,"hũ",120,"processed","🍯",False),
            ("Lychee Jam 500g","Mứt Vải 500g","Mứt vải hũ lớn 500g cho gia đình. Công thức ít đường, hương vị đậm đà. Bảo quản tủ lạnh sau khi mở.",130000,"hũ",80,"processed","🍯",False),
            ("Lychee Honey 250g","Mật Ong Hoa Vải 250g","Mật ong hoa vải thiều nguyên chất, thu hoạch tháng 4-5. Màu vàng nhạt, thơm hoa vải. Không pha trộn.",145000,"hũ",100,"processed","🍯",True),
            ("Lychee Honey 500g","Mật Ong Hoa Vải 500g","Hũ lớn 500g mật ong hoa vải. Giảm 10% so với 2 hũ nhỏ. Bao bì hộp gỗ sang trọng.",260000,"hũ",60,"processed","🍯",False),
            ("Lychee Vinegar","Giấm Vải","Giấm lên men từ vải thiều tươi, ủ 12 tháng. Vị chua dịu, thơm, dùng pha salad hoặc uống sức khỏe.",85000,"300ml",70,"processed","🍶",False),
            ("Lychee Syrup","Siro Vải","Siro vải đặc nguyên chất, pha 1:10 với nước. Dùng làm đồ uống, pha chế cocktail, làm bánh.",95000,"500ml",90,"processed","🧴",False),
            ("Lychee Paste","Bột Nhuyễn Vải","Bột nhuyễn vải đông lạnh IQF, tiện lợi làm bánh, kem, smoothie. Túi 1kg.",120000,"túi",60,"processed","🥣",False),
            ("Lychee Candy","Kẹo Vải","Kẹo mềm vị vải thiều, không phẩm màu nhân tạo. Làm từ vải thiều cô đặc tự nhiên. Hộp 200g.",65000,"hộp",150,"processed","🍬",False),
            ("Lychee Tea","Trà Vải Thiều","Trà hoa vải sấy khô, pha trà thơm thanh mát. Túi 50g pha được 20 ấm trà. Tốt cho tiêu hóa.",70000,"50g",110,"processed","🍵",False),
            ("Lychee Chocolate","Socola Nhân Vải","Socola đen 70% cacao nhân mứt vải. Kết hợp đắng-ngọt độc đáo. Hộp 12 viên làm thủ công.",120000,"hộp",65,"processed","🍫",False),
            # 🍷 ĐỒ UỐNG
            ("Lychee Wine 500ml","Rượu Vải 500ml","Rượu vải ủ truyền thống, 12% ABV. Hương vải thơm nồng, vị ngọt dịu. Thích hợp uống lạnh mùa hè.",180000,"chai",55,"beverage","🍷",True),
            ("Lychee Wine 750ml","Rượu Vải 750ml","Chai rượu vải 750ml sang trọng, dán nhãn đẹp. Ủ 18 tháng, hương vị phức hợp. Quà biếu lịch sự.",250000,"chai",40,"beverage","🍷",False),
            ("Lychee Sparkling Water","Nước Có Gas Vải","Nước khoáng có gas hương vải tự nhiên. Không đường, không calo. Lon 330ml.",18000,"lon",300,"beverage","🥤",False),
            ("Lychee Juice 1L","Nước Ép Vải 1L","Nước ép vải nguyên chất, không đường thêm, không chất bảo quản. Hộp 1 lít, bảo quản lạnh.",85000,"hộp",80,"beverage","🧃",False),
            ("Lychee Smoothie Pack","Gói Sinh Tố Vải","Hỗn hợp vải + dừa + gừng đông lạnh sẵn. Cho vào máy xay là xong. Gói 4 phần dùng.",95000,"gói",60,"beverage","🥤",False),
            ("Lychee Kombucha","Kombucha Vải","Trà lên men kombucha vị vải thiều. Tốt cho đường ruột, giàu probiotic. Chai 350ml.",55000,"chai",90,"beverage","🫧",False),
            ("Lychee Liqueur","Rượu Mùi Vải","Rượu mùi vải 25% ABV, màu hồng đẹp. Uống thẳng, pha cocktail hoặc làm bánh. Chai 350ml.",220000,"chai",35,"beverage","🍸",False),
            # ❄️ ĐÔNG LẠNH
            ("Frozen Lychee 500g","Vải Đông Lạnh 500g","Vải đã bóc vỏ, bỏ hạt, đông lạnh IQF. Giữ nguyên hương vị tươi. Dùng làm kem, sinh tố, bánh.",70000,"túi",180,"frozen","❄️",False),
            ("Frozen Lychee 1kg","Vải Đông Lạnh 1kg","Túi lớn 1kg vải đông lạnh IQF tiện lợi. Hạn dùng 12 tháng. Tiết kiệm hơn túi nhỏ.",125000,"túi",120,"frozen","❄️",False),
            ("Frozen Lychee Sorbet","Kem Sorbet Vải","Kem sorbet vải thiều làm từ 100% vải tươi. Không chất béo, không sữa. Hộp 500ml 4 phần dùng.",85000,"hộp",70,"frozen","🍧",True),
            ("Frozen Lychee Pulp","Thịt Vải Đông Lạnh","Thịt vải xay nhuyễn đông lạnh, túi 500g. Tiện dụng cho quán cafe, tiệm bánh làm nguyên liệu.",90000,"túi",95,"frozen","❄️",False),
            ("Lychee Ice Cream Bar","Kem Que Vải Thiều","Kem que vải thiều handmade, hộp 6 cây. Nhân thịt vải thật. Không phẩm màu, hương liệu nhân tạo.",95000,"hộp",55,"frozen","🍦",False),
        ]
        for p in products:
            cur.execute("INSERT INTO products (name,name_vn,description,price,unit,stock,category,image_emoji,featured) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)", p)
        print(f"✅ Seeded {len(products)} products")
        # Sample reviews
        cur.execute("SELECT id FROM products ORDER BY id LIMIT 10")
        pids = [r["id"] for r in cur.fetchall()]
        reviews = [
            (pids[0],"Nguyễn Thị Lan",5,"Vải ngon tuyệt vời! Tươi, ngọt, hạt nhỏ. Giao hàng siêu nhanh, đóng gói cẩn thận."),
            (pids[0],"Trần Văn Minh",5,"Đặt lần thứ 3 rồi. Chất lượng ổn định, không bao giờ thất vọng."),
            (pids[0],"Lê Thị Hoa",4,"Vải ngon, giao nhanh. Trừ 1 sao vì có vài quả nhỏ nhưng vị vẫn ngon."),
            (pids[2],"Phạm Quang Huy",5,"Vải đầu mùa hiếm lắm! Ngon hơn hẳn vải thường. Sẽ đặt sớm năm sau."),
            (pids[5],"Hoàng Thị Mai",5,"Vải không hạt lần đầu ăn, ngạc nhiên ghê! Thịt dày, ngọt đậm."),
            (pids[1],"Vũ Thị Thanh",5,"Mua hộp quà biếu sếp, sếp khen quà sang. Đóng gói đẹp, thiệp viết tay rất tình cảm."),
            (pids[3],"Đặng Văn Long",5,"Hộp gỗ đẹp lắm, giữ làm đựng đồ được. Vải bên trong tươi ngon."),
            (pids[7],"Cao Minh Tuấn",5,"Rượu vải thơm lắm! Uống lạnh mùa hè tuyệt."),
            (pids[8],"Ngô Thị Hương",5,"Mứt vải ngon, ngọt thanh không bị ngọt gắt. Ăn với bánh mì bơ tuyệt vời."),
            (pids[9],"Phan Văn Đức",4,"Mật ong hoa vải thơm lắm, khác hẳn mật ong thường. Chắc chắn mua lại."),
        ]
        for rev in reviews:
            cur.execute("INSERT INTO reviews (product_id,author,rating,comment) VALUES (%s,%s,%s,%s)", rev)
        print(f"✅ Seeded {len(reviews)} reviews")
    conn.commit(); conn.close()
    print("✅ Database ready")
def wait_for_db():
    for i in range(15):
        try:
            c = get_db(); c.close()
            print("Connected to database"); return
        except Exception as e:
            print(f"Waiting ({i+1}/15): {e}"); time.sleep(5)
    raise RuntimeError("Cannot connect to database")

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
    def log_message(self, fmt, *a): print(f"  {self.command} {self.path} -> {a[1]}")

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
        send_json(self, 201, {"order":order,"message":"Order placed successfully!"})

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