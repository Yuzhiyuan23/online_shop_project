-- 1. 创建数据库
CREATE DATABASE IF NOT EXISTS online_shop DEFAULT CHARACTER SET utf8mb4;
USE online_shop;

-- 2. 用户表 (增加 role 字段区分商家和顾客)
CREATE TABLE IF NOT EXISTS user (
    id INT PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(50) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    email VARCHAR(100) NOT NULL,
    role ENUM('customer', 'merchant') DEFAULT 'customer'
);

-- 3. 商品表
CREATE TABLE IF NOT EXISTS product (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    price DECIMAL(10, 2) NOT NULL,
    stock INT NOT NULL
);

-- 4. 订单表
CREATE TABLE IF NOT EXISTS orders (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT,
    username VARCHAR(50),
    total_price DECIMAL(10, 2),
    status VARCHAR(20) DEFAULT '已支付',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 5. 活动日志表 (记录浏览/购买行为)
CREATE TABLE IF NOT EXISTS activity_log (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT,
    username VARCHAR(50),
    action VARCHAR(50), -- 如：'浏览', '购买', '登录'
    details TEXT,       -- 如：'浏览了商品: 拯救者笔记本'
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 6. 插入初始测试数据 (可选)
-- 初始商家账号 (密码 admin123)
INSERT IGNORE INTO user (username, password, email, role) VALUES ('admin', 'admin123', 'admin@shop.com', 'merchant');

-- 初始商品
INSERT IGNORE INTO product (name, description, price, stock) VALUES 
('拯救者笔记本', '高性能游戏本', 7499.00, 10),
('华为手机 P60', '超感光影像', 4988.00, 20),
('机械键盘', 'RGB背光红轴', 299.00, 50),
('电竞鼠标', '16000 DPI', 199.00, 100),
('降噪耳机', '无线蓝牙主动降噪', 1299.00, 30);