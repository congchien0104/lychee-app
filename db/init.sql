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

CREATE TABLE IF NOT EXISTS order_items (
    id         SERIAL PRIMARY KEY,
    order_id   INTEGER REFERENCES orders(id) ON DELETE CASCADE,
    product_id INTEGER REFERENCES products(id),
    name       VARCHAR(255),
    quantity   INTEGER NOT NULL,
    price      DECIMAL(10,2) NOT NULL
);

CREATE TABLE IF NOT EXISTS reviews (
    id         SERIAL PRIMARY KEY,
    product_id INTEGER REFERENCES products(id) ON DELETE CASCADE,
    author     VARCHAR(255) NOT NULL,
    rating     INTEGER CHECK (rating BETWEEN 1 AND 5),
    comment    TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ── 50 sản phẩm vải thiều ────────────────────────────────────────────────────
INSERT INTO products (name, name_vn, description, price, unit, stock, category, image_emoji, featured) VALUES

-- FRESH ───────────────────────────────────────────────────────────────────────
('Fresh Lychee Premium',      'Vải tươi cao cấp',          'Vải thiều Lục Ngạn loại đặc biệt, hái sáng giao chiều. Thịt dày, hạt nhỏ, ngọt thanh tự nhiên.',                     85000,  'kg',   150, 'fresh',     '🍈', TRUE),
('Fresh Lychee Grade A',      'Vải tươi hạng A',           'Vải hạng A chọn lọc kỹ, kích cỡ đều, màu đỏ đẹp. Phù hợp biếu tặng hoặc ăn gia đình.',                              75000,  'kg',   200, 'fresh',     '🍈', FALSE),
('Fresh Lychee Early Season', 'Vải tươi đầu mùa',          'Vải đầu mùa xuất hiện giữa tháng 5, hương thơm nồng nàn, vị ngọt dịu. Số lượng rất có hạn.',                         95000,  'kg',    60, 'fresh',     '🍈', TRUE),
('Fresh Lychee Late Season',  'Vải tươi cuối mùa',         'Vải cuối vụ thịt mọng nước hơn, độ ngọt cao nhất. Đây là thời điểm vải ngon nhất trong năm.',                        80000,  'kg',    80, 'fresh',     '🍈', FALSE),
('Fresh Lychee Whole Branch', 'Vải tươi cả cành',          'Vải để nguyên cành lá xanh, tươi như vừa hái. Thích hợp trưng bày và làm quà độc đáo.',                              110000, 'kg',    40, 'fresh',     '🍈', FALSE),
('Lychee Seedless',           'Vải không hạt đặc sản',     'Giống vải đặc biệt không hạt, ăn cả miếng không cần nhả hạt. Hiếm và quý, sản lượng rất thấp.',                     150000, 'kg',    25, 'fresh',     '🍈', TRUE),
('Baby Lychee',               'Vải bi nhỏ đặc sản',        'Giống vải bi đặc sản, trái nhỏ nhưng cực ngọt và thơm. Vị đậm đà hơn vải thường.',                                  90000,  'kg',    70, 'fresh',     '🍈', FALSE),
('Organic Lychee VietGAP',    'Vải hữu cơ VietGAP',        'Canh tác hoàn toàn hữu cơ, không phân hóa học, không thuốc trừ sâu. Chứng nhận VietGAP.',                           130000, 'kg',    50, 'fresh',     '🍈', TRUE),

-- GIFT ────────────────────────────────────────────────────────────────────────
('Gift Box 500g',             'Hộp quà vải 500g',          'Hộp quà nhỏ xinh 500g vải tươi. Thiết kế sang trọng, kèm túi đá giữ lạnh. Lý tưởng cho quà nhỏ.',                   85000,  'hộp',   80, 'gift',      '🎁', FALSE),
('Gift Box 1kg Classic',      'Hộp quà vải 1kg Classic',   'Hộp 1kg vải cao cấp thiết kế cổ điển. Kèm thiệp cảm ơn viết tay và túi đá giữ lạnh.',                               120000, 'hộp',   60, 'gift',      '🎁', TRUE),
('Gift Box 2kg Luxury',       'Hộp quà vải 2kg cao cấp',   'Hộp 2kg vải thiều loại đặc biệt. Hộp gỗ cao cấp, in laser, phù hợp biếu đối tác doanh nghiệp.',                     250000, 'hộp',   35, 'gift',      '🎁', TRUE),
('Gift Box 3kg Premium',      'Hộp quà vải 3kg Premium',   'Hộp gỗ 3kg thiết kế sang trọng, kèm dao nhỏ bạc và khăn lau tay. Quà Tết, quà sếp lý tưởng.',                       320000, 'hộp',   30, 'gift',      '🎁', TRUE),
('Gift Box 5kg VIP',          'Hộp quà vải 5kg VIP',       'Bộ quà VIP 5kg vải đặc biệt trong hộp gỗ khắc tên theo yêu cầu. Giao hàng tận nơi toàn quốc.',                       520000, 'hộp',   15, 'gift',      '🎁', TRUE),
('Gift Set Duo',              'Bộ đôi quà tặng',           'Bộ 2 hộp nhỏ 500g vải tươi + 1 hũ mật ong vải 200g. Đóng gói nơ ruy băng, thích hợp biếu tặng.',                    195000, 'bộ',    25, 'gift',      '🎁', FALSE),
('Gift Set Family',           'Bộ quà gia đình',           '2kg vải tươi + mứt vải 200g + nước ép vải 500ml. Bộ quà đầy đủ cho cả gia đình thưởng thức.',                        350000, 'bộ',    20, 'gift',      '🎁', FALSE),
('Corporate Gift Box',        'Hộp quà doanh nghiệp',      '3kg vải cao cấp trong hộp in logo công ty theo yêu cầu. Đặt số lượng lớn có giá ưu đãi.',                            450000, 'hộp',   10, 'gift',      '🎁', FALSE),

-- DRIED ───────────────────────────────────────────────────────────────────────
('Dried Lychee Original',     'Vải sấy truyền thống',      'Vải sấy theo công thức truyền thống, không chất bảo quản. Dẻo ngọt tự nhiên, ăn vặt tuyệt vời.',                     95000,  '200g', 200, 'dried',     '🍂', FALSE),
('Dried Lychee Sugar-Free',   'Vải sấy không đường',       'Vải sấy hoàn toàn không thêm đường. Ngọt tự nhiên từ trái vải. Phù hợp người ăn kiêng và tiểu đường.',               110000, '200g', 150, 'dried',     '🍂', FALSE),
('Dried Lychee Crispy',       'Vải sấy giòn chân không',   'Vải sấy giòn tan bằng công nghệ sấy chân không. Giữ nguyên hương vị và màu sắc tươi sáng.',                          120000, '150g', 180, 'dried',     '🍂', TRUE),
('Dried Lychee Traditional',  'Vải sấy có hạt',            'Vải sấy nguyên hạt theo phong cách truyền thống. Hương thơm đặc trưng quyến rũ.',                                    85000,  '250g', 120, 'dried',     '🍂', FALSE),
('Dried Lychee Bulk 1kg',     'Túi vải sấy 1kg',           'Túi lớn 1kg vải sấy tiết kiệm, phù hợp gia đình đông người hoặc làm quà số lượng nhiều.',                            380000, '1kg',   60, 'dried',     '🍂', FALSE),
('Lychee Chips Snack',        'Chips vải ăn vặt',          'Vải thiều thái lát mỏng sấy giòn, đóng gói túi snack tiện lợi. Ăn vặt lành mạnh cho cả nhà.',                        65000,  '80g',  250, 'dried',     '🍂', FALSE),

-- PROCESSED ───────────────────────────────────────────────────────────────────
('Lychee Jam Classic',        'Mứt vải truyền thống',      'Mứt vải nấu thủ công từ vải tươi và đường mía. Không phẩm màu, không chất bảo quản. Hũ 250g.',                        75000,  'hũ',    80, 'processed', '🍯', FALSE),
('Lychee Jam Low Sugar',      'Mứt vải ít đường',          'Mứt vải giảm 50% đường so với truyền thống. Vị chua ngọt cân bằng, tốt cho sức khỏe.',                               85000,  'hũ',    60, 'processed', '🍯', FALSE),
('Lychee Jam Rose',           'Mứt vải hoa hồng',          'Mứt vải pha hương hoa hồng tự nhiên. Màu hồng tươi, mùi thơm dịu. Phết bánh mì tuyệt hảo.',                         90000,  'hũ',    45, 'processed', '🍯', FALSE),
('Lychee Honey Raw',          'Mật ong vải thô',           'Mật ong hoa vải nguyên chất, chưa qua tiệt trùng. Màu vàng nhạt, hương thơm hoa vải đặc trưng.',                     145000, '250g',  60, 'processed', '🍯', TRUE),
('Lychee Honey Premium',      'Mật ong vải cao cấp',       'Mật ong hoa vải chuẩn VietGAP. Lọ thủy tinh sang trọng, nắp gỗ. Quà tặng sức khỏe ý nghĩa.',                        180000, '300g',  40, 'processed', '🍯', FALSE),
('Lychee Syrup',              'Siro vải đặc',              'Siro vải đậm đặc tự nhiên. Pha nước uống, làm cocktail, trang trí bánh kem. Chai 500ml.',                             95000,  '500ml', 70, 'processed', '🍯', FALSE),
('Lychee Vinegar',            'Giấm vải lên men',          'Giấm lên men từ vải thiều tươi. Vị chua thanh dịu, dùng trộn salad hoặc pha nước uống giải độc.',                    85000,  '300ml', 55, 'processed', '🍯', FALSE),
('Lychee Dipping Sauce',      'Tương chấm vải',            'Sốt vải ngọt cay đặc biệt, dùng chấm hải sản, thịt nướng. Công thức gia truyền 3 đời.',                              70000,  '200g',  90, 'processed', '🍯', FALSE),
('Lychee Powder',             'Bột vải sấy phun',          'Bột vải sấy phun công nghệ cao. Hòa tan nhanh, dùng làm bánh, kem, nước uống. Túi 100g.',                            120000, '100g',  80, 'processed', '🍯', FALSE),

-- BEVERAGE ────────────────────────────────────────────────────────────────────
('Lychee Wine 500ml',         'Rượu vải 500ml',            'Rượu vải truyền thống 12% ABV. Lên men tự nhiên, không pha cồn công nghiệp. Hương thơm quyến rũ.',                    180000, '500ml', 40, 'beverage',  '🍷', TRUE),
('Lychee Wine 750ml',         'Rượu vải 750ml',            'Chai rượu vải 750ml phù hợp tiệc tùng, biếu tặng. Nút bần sang trọng, nhãn thiết kế thủ công.',                      260000, '750ml', 25, 'beverage',  '🍷', FALSE),
('Lychee Wine Aged Oak',      'Rượu vải ủ thùng gỗ sồi',  'Rượu vải ủ 12 tháng trong thùng gỗ sồi. Màu vàng amber đẹp, hương phức hợp. Giới hạn 100 chai/năm.',                 420000, '500ml', 12, 'beverage',  '🍷', TRUE),
('Lychee Juice 1L',           'Nước ép vải 1L',            'Nước ép vải tươi nguyên chất 100%, không đường, không nước. Thanh nhiệt, giải khát tức thì.',                         85000,  '1L',   100, 'beverage',  '🥤', FALSE),
('Lychee Juice Can 330ml',    'Nước ép vải lon 330ml',     'Lon nước ép vải tiện lợi 330ml. Giữ lạnh ngon hơn. Thích hợp mang theo khi đi làm, đi học.',                         35000,  '330ml', 300, 'beverage',  '🥤', FALSE),
('Lychee Sparkling Water',    'Nước soda vải có ga',       'Nước có gas hương vải tự nhiên. Ít calo, không đường. Thức uống giải khát thời thượng.',                              45000,  '330ml', 200, 'beverage',  '🥤', FALSE),
('Lychee Flower Tea',         'Trà hoa vải',               'Túi trà hoa vải khô pha nóng hoặc lạnh. Hương thơm dịu nhẹ, thư giãn tinh thần. Hộp 20 túi.',                        65000,  'hộp',  120, 'beverage',  '🍵', FALSE),
('Lychee Kombucha',           'Kombucha vải men vi sinh',  'Trà lên men kombucha hương vải. Giàu men vi sinh, tốt cho đường ruột. Chai 350ml.',                                   75000,  '350ml',  80, 'beverage',  '🍵', FALSE),
('Lychee Smoothie Powder',    'Bột sinh tố vải sấy lạnh',  'Bột sinh tố vải thiều sấy lạnh. Chỉ cần thêm nước hoặc sữa là có ngay ly sinh tố. Túi 200g.',                        95000,  '200g',  90, 'beverage',  '🥤', FALSE),

-- FROZEN ──────────────────────────────────────────────────────────────────────
('Frozen Lychee Peeled 500g', 'Vải đông lạnh bóc vỏ 500g','Vải đã bóc vỏ, bỏ hạt, cấp đông IQF. Dùng ngay cho sinh tố, chè, dessert. Túi zip 500g.',                           70000,  '500g', 120, 'frozen',    '❄️', FALSE),
('Frozen Lychee Whole 1kg',   'Vải đông lạnh nguyên trái', 'Vải nguyên trái cấp đông nhanh. Rã đông là tươi ngon như vừa hái. Túi zip tiện lợi 1kg.',                            110000, '1kg',   80, 'frozen',    '❄️', FALSE),
('Frozen Lychee Puree',       'Nhuyễn vải đông lạnh',      'Purée vải thiều xay mịn cấp đông. Chuyên dùng làm kem, mousse, sorbet, bánh. Hộp 500g.',                             90000,  '500g',  60, 'frozen',    '❄️', FALSE),
('Lychee Ice Cream',          'Kem vải thiều thủ công',    'Kem vải thiều làm thủ công từ vải tươi và kem tươi nguyên chất. Không màu nhân tạo. Hộp 400ml.',                     85000,  '400ml',  70, 'frozen',    '🍦', TRUE),
('Lychee Sorbet Vegan',       'Sorbet vải thuần chay',     'Sorbet vải thuần chay, không sữa, không gluten. Giải nhiệt hoàn hảo ngày hè. Hộp 350ml.',                            75000,  '350ml',  55, 'frozen',    '🍦', FALSE),
('Frozen Lychee Dessert Kit', 'Bộ nguyên liệu chè vải',   'Bộ nguyên liệu làm chè vải: vải đông lạnh + thạch dừa + hạt chia. Đủ cho 4 người.',                                  150000, 'hộp',   40, 'frozen',    '❄️', FALSE),

-- OTHER ───────────────────────────────────────────────────────────────────────
('Lychee Seedling 2 Years',   'Cây giống vải 2 tuổi',      'Cây giống vải thiều Lục Ngạn 2 năm tuổi, chiết cành từ cây mẹ cho năng suất cao. Sẵn sàng trồng.',                  250000, 'cây',   30, 'other',     '🌱', FALSE),
('Lychee Bonsai',             'Vải bonsai cảnh',           'Cây vải trồng chậu kiểng, có trái mini đỏ đẹp. Trang trí ban công, phòng khách. Ý nghĩa phong thủy.',                650000, 'chậu',  10, 'other',     '🌱', TRUE),
('Lychee Skincare Set',       'Bộ dưỡng da chiết xuất vải','Bộ serum + kem dưỡng chiết xuất từ hạt vải thiều. Chống oxy hóa, làm sáng da. Thương hiệu VảiBeauty.',              450000, 'bộ',    25, 'other',     '✨', FALSE),
('Lychee Scented Candle',     'Nến thơm hương vải',        'Nến thơm hương vải thiều tự nhiên làm từ sáp đậu nành. Thư giãn tâm trí, thơm cả phòng. 150g.',                     95000,  'hũ',    50, 'other',     '🕯️', FALSE),
('Dried Lychee Blossom',      'Hoa vải sấy khô',           'Hoa vải sấy khô dùng trang trí, pha trà hoa hoặc làm xông hơi. Hương thơm tinh tế, nhẹ nhàng.',                     55000,  '50g',  100, 'other',     '🌸', FALSE),
('Lychee Recipe Book',        'Sách 50 công thức từ vải',  '50 công thức chế biến món ăn và đồ uống từ vải thiều. Ảnh đẹp, hướng dẫn chi tiết. Bìa cứng.',                       150000, 'cuốn',  30, 'other',     '📚', FALSE);

-- ── Đánh giá sản phẩm ────────────────────────────────────────────────────────
INSERT INTO reviews (product_id, author, rating, comment) VALUES
(1,  'Nguyễn Thị Lan',    5, 'Vải tươi cực ngon, giao hàng nhanh, đóng gói cẩn thận. Sẽ ủng hộ lần sau!'),
(1,  'Trần Văn Minh',     5, 'Đặt lần 2 rồi, chất lượng ổn định. Vải hạt nhỏ, thịt dày, ngọt lắm.'),
(1,  'Lê Hoàng Nam',      4, 'Vải ngon, giá hợp lý. Giao hàng có hơi chậm nhưng vải vẫn tươi tốt.'),
(3,  'Phạm Thu Hà',       5, 'Vải đầu mùa ngon tuyệt vời! Hương thơm đặc biệt, chưa mùa nào ngon như vậy.'),
(10, 'Hoàng Minh Tuấn',   5, 'Hộp quà đẹp lắm, mua biếu sếp được khen nhiều. Sẽ đặt thêm cho dịp Tết.'),
(11, 'Vũ Thị Hoa',        4, 'Hộp gỗ sang trọng, vải bên trong chất lượng tốt. Giao hàng đúng hẹn.'),
(19, 'Bùi Quốc Hùng',     5, 'Vải sấy giòn ngon không tưởng! Cả nhà nghiền, đặt túi 1kg cho tiết kiệm.'),
(18, 'Ngô Thị Mai',       5, 'Vải sấy không đường mà vẫn ngọt tự nhiên. Tốt cho sức khỏe, ăn không lo béo.'),
(23, 'Đinh Văn Long',     5, 'Mứt vải ngon hơn mứt ngoài hàng nhiều. Ăn với bánh mì buổi sáng thì tuyệt.'),
(26, 'Lý Thị Bình',       4, 'Mật ong vải thơm, màu đẹp. Hòa nước ấm uống sáng rất tốt cho họng.'),
(31, 'Phan Văn Đức',      5, 'Rượu vải thơm nhẹ, uống ngọt và mát. Mang ra ngoài bạn bè ai cũng thích.'),
(35, 'Tô Thị Ngọc',       4, 'Nước ép vải nguyên chất ngon, không ngọt quá. Mua cho cả nhà uống hàng ngày.'),
(40, 'Cao Minh Khoa',     5, 'Kem vải ngon xuất sắc! Vị vải rõ rệt, không bị ngọt giả tạo. Sẽ đặt thêm.'),
(42, 'Hà Thị Thu',        5, 'Sorbet vải nhẹ mát, hoàn hảo cho mùa hè TP.HCM. Cả nhà đều mê.'),
(48, 'Trương Văn Bảo',    4, 'Nến thơm hương vải rất dễ chịu, thắp lên phòng thơm ngát. Mua thêm lần 2 rồi.');