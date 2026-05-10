-- Products table
CREATE TABLE IF NOT EXISTS products (
    id          SERIAL PRIMARY KEY,
    name        VARCHAR(255) NOT NULL,
    name_vn     VARCHAR(255),
    description TEXT,
    price       DECIMAL(10,2) NOT NULL,
    unit        VARCHAR(50) DEFAULT 'kg',
    stock       INTEGER DEFAULT 0,
    category    VARCHAR(100),
    image_emoji VARCHAR(10) DEFAULT '🍈',
    featured    BOOLEAN DEFAULT FALSE,
    created_at  TIMESTAMPTZ DEFAULT NOW()
);

-- Orders table
CREATE TABLE IF NOT EXISTS orders (
    id         SERIAL PRIMARY KEY,
    name       VARCHAR(255) NOT NULL,
    email      VARCHAR(255) NOT NULL,
    phone      VARCHAR(50),
    address    TEXT,
    total      DECIMAL(10,2) NOT NULL,
    status     VARCHAR(50) DEFAULT 'pending',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Order items
CREATE TABLE IF NOT EXISTS order_items (
    id         SERIAL PRIMARY KEY,
    order_id   INTEGER REFERENCES orders(id) ON DELETE CASCADE,
    product_id INTEGER REFERENCES products(id),
    name       VARCHAR(255),
    quantity   INTEGER NOT NULL,
    price      DECIMAL(10,2) NOT NULL
);

-- Reviews
CREATE TABLE IF NOT EXISTS reviews (
    id         SERIAL PRIMARY KEY,
    product_id INTEGER REFERENCES products(id) ON DELETE CASCADE,
    author     VARCHAR(255) NOT NULL,
    rating     INTEGER CHECK (rating BETWEEN 1 AND 5),
    comment    TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ── Seed products ────────────────────────────────────────────────────────────
INSERT INTO products (name, name_vn, description, price, unit, stock, category, image_emoji, featured) VALUES
('Fresh Lychee', 'Vải tươi', 'Premium fresh lychee from Bac Giang. Sweet, juicy with thin skin and small seed. Harvested daily.', 85000, 'kg', 150, 'fresh', '🍈', TRUE),
('Lychee Gift Box 1kg', 'Hộp quà vải 1kg', 'Beautiful gift box with 1kg premium lychee. Perfect for gifting. Includes ice pack for freshness.', 120000, 'box', 50, 'gift', '🎁', TRUE),
('Dried Lychee', 'Vải sấy khô', 'Sun-dried lychee with no preservatives. Chewy, naturally sweet. Great for snacking.', 95000, '200g', 200, 'dried', '🍂', FALSE),
('Lychee Gift Box 3kg', 'Hộp quà vải 3kg', 'Premium 3kg gift box with hand-selected lychees. Beautiful packaging, ideal for holidays.', 320000, 'box', 30, 'gift', '🎁', TRUE),
('Lychee Jam', 'Mứt vải', 'Homemade lychee jam with natural sweetness. No artificial flavors. 250g jar.', 75000, 'jar', 80, 'processed', '🍯', FALSE),
('Lychee Wine', 'Rượu vải', 'Traditional lychee wine, 12% ABV. Smooth and fragrant. Handcrafted in small batches.', 180000, '500ml', 40, 'beverage', '🍷', TRUE),
('Lychee Honey', 'Mật ong vải', 'Pure monofloral lychee blossom honey. Light golden color, floral aroma. Raw and unfiltered.', 145000, '250g', 60, 'processed', '🍯', FALSE),
('Frozen Lychee', 'Vải đông lạnh', 'IQF frozen lychee, peeled and seeded. Ready to use in smoothies and desserts.', 70000, '500g', 120, 'frozen', '❄️', FALSE);

-- Seed reviews
INSERT INTO reviews (product_id, author, rating, comment) VALUES
(1, 'Nguyễn Thị Lan', 5, 'Vải rất ngon, tươi và ngọt. Giao hàng nhanh!'),
(1, 'Trần Văn Minh', 5, 'Đặt lần 2 rồi, chất lượng ổn định. Sẽ tiếp tục ủng hộ.'),
(1, 'Lê Hoàng Nam', 4, 'Vải ngon, hạt nhỏ, thịt dày. Giá hợp lý.'),
(2, 'Phạm Thu Hà', 5, 'Mua làm quà biếu, đóng gói đẹp lắm. Mọi người khen nhiều.'),
(6, 'Đỗ Quang Vinh', 4, 'Rượu vải thơm, uống vào mùa hè rất mát. Độ cồn vừa phải.');
