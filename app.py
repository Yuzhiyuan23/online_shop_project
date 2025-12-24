from flask import Flask, render_template, redirect, url_for, request, flash, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'final-project-secure-key'

# 【配置】数据库连接。请修改密码。如果密码中有 @ 请用 %40 代替。
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:Martin503%40@localhost/online_shop'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# --- 数据库模型 ---

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(20), default='customer') # customer, merchant, admin
    # 建立关联：商家拥有的商品。反向引用名设为 'owner' 供模板使用 p.owner
    products = db.relationship('Product', backref='owner', lazy=True)

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    price = db.Column(db.Float, nullable=False)
    stock = db.Column(db.Integer, default=0)
    merchant_id = db.Column(db.Integer, db.ForeignKey('user.id'))

class Orders(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    merchant_id = db.Column(db.Integer, nullable=False)
    total_price = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), default='待发货') # 待发货 -> 待收货 -> 已完成
    created_at = db.Column(db.DateTime, default=datetime.now)

class ActivityLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    username = db.Column(db.String(50))
    merchant_id = db.Column(db.Integer) 
    action = db.Column(db.String(50))   
    details = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.now)

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))

def log_activity(action, details, m_id=None):
    if current_user.is_authenticated:
        log = ActivityLog(user_id=current_user.id, username=current_user.username, 
                          action=action, details=details, merchant_id=m_id)
        db.session.add(log)
        db.session.commit()

# --- 初始化数据 ---

def init_db():
    if not User.query.filter_by(role='admin').first():
        admin = User(username='admin', password='super123', email='admin@mall.com', role='admin')
        db.session.add(admin)
        db.session.commit()
    
    if not User.query.filter_by(username='AppleStore').first():
        m1 = User(username='AppleStore', password='123', email='apple@test.com', role='merchant')
        m2 = User(username='XiaomiStore', password='123', email='mi@test.com', role='merchant')
        db.session.add_all([m1, m2])
        db.session.commit()

        p1 = Product(name='iPhone 15', description='A16芯片', price=5999.0, stock=50, merchant_id=m1.id)
        p2 = Product(name='小米14', description='徕卡影像', price=3999.0, stock=30, merchant_id=m2.id)
        db.session.add_all([p1, p2])
        db.session.commit()

# --- 路由 ---

@app.route('/')
def index():
    products = Product.query.all()
    return render_template('index.html', products=products)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        new_user = User(username=request.form['username'], password=request.form['password'], 
                        email=request.form['email'], role=request.form['role'])
        db.session.add(new_user)
        db.session.commit()
        flash('注册成功')
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = User.query.filter_by(username=request.form['username'], password=request.form['password']).first()
        if user:
            login_user(user)
            return redirect(url_for('index'))
        flash('账号或密码错误')
    return render_template('login.html')

@app.route('/logout')
def logout():
    logout_user()
    session.pop('cart', None)
    return redirect(url_for('index'))

@app.route('/add_to_cart/<int:product_id>', methods=['POST'])
@login_required
def add_to_cart(product_id):
    qty = int(request.form.get('quantity', 1))
    if 'cart' not in session: session['cart'] = {}
    pid_s = str(product_id)
    session['cart'][pid_s] = session['cart'].get(pid_s, 0) + qty
    session.modified = True
    flash('已加购物车')
    return redirect(url_for('index'))

@app.route('/cart')
@login_required
def cart():
    cart_dict = session.get('cart', {})
    items, total = [], 0
    for pid, q in cart_dict.items():
        p = db.session.get(Product, int(pid))
        if p:
            sub = p.price * q
            total += sub
            items.append({'id': p.id, 'name': p.name, 'price': p.price, 'qty': q, 'sub': sub, 'm_name': p.owner.username})
    return render_template('cart.html', products=items, total=total)

@app.route('/checkout', methods=['POST'])
@login_required
def checkout():
    cart_dict = session.get('cart', {})
    if not cart_dict: return redirect(url_for('index'))
    split_orders = {}
    for pid, q in cart_dict.items():
        p = db.session.get(Product, int(pid))
        if p:
            m_id = p.merchant_id
            split_orders[m_id] = split_orders.get(m_id, 0) + (p.price * q)
            p.stock -= q 
            log_activity('购买', f'结算了商品: {p.name}x{q}', m_id=m_id)
    for m_id, price in split_orders.items():
        db.session.add(Orders(user_id=current_user.id, merchant_id=m_id, total_price=price, status='待发货'))
    db.session.commit()
    session.pop('cart', None)
    flash('结算成功！请等待发货')
    return redirect(url_for('order_history'))

@app.route('/orders')
@login_required
def order_history():
    user_orders = Orders.query.filter_by(user_id=current_user.id).order_by(Orders.created_at.desc()).all()
    data = []
    for o in user_orders:
        m = db.session.get(User, o.merchant_id)
        data.append({'o': o, 'm_name': m.username if m else "未知"})
    return render_template('orders.html', orders=data)

@app.route('/customer/confirm_receipt/<int:order_id>')
@login_required
def confirm_receipt(order_id):
    order = db.session.get(Orders, order_id)
    if order and order.user_id == current_user.id:
        order.status = '已完成'
        db.session.commit()
        log_activity('确认收货', f'确认收货订单 #{order_id}', m_id=order.merchant_id)
    return redirect(url_for('order_history'))

# --- 商家端 ---

@app.route('/merchant')
@login_required
def merchant_dashboard():
    if current_user.role != 'merchant': return "拒绝", 403
    my_orders = Orders.query.filter_by(merchant_id=current_user.id).all()
    revenue = sum(o.total_price for o in my_orders if o.status == '已完成')
    p_count = Product.query.filter_by(merchant_id=current_user.id).count()
    return render_template('merchant/dashboard.html', revenue=revenue, o_count=len(my_orders), p_count=p_count)

@app.route('/merchant/products', methods=['GET', 'POST'])
@login_required
def merchant_products():
    if current_user.role != 'merchant': return "拒绝", 403
    if request.method == 'POST':
        new_p = Product(name=request.form['name'], price=float(request.form['price']), 
                        stock=int(request.form['stock']), description=request.form['desc'], 
                        merchant_id=current_user.id)
        db.session.add(new_p)
        db.session.commit()
    products = Product.query.filter_by(merchant_id=current_user.id).all()
    return render_template('merchant/products.html', products=products)

@app.route('/merchant/del_p/<int:id>')
@login_required
def delete_p(id):
    p = db.session.get(Product, id)
    if p and p.merchant_id == current_user.id:
        db.session.delete(p)
        db.session.commit()
        flash('删除成功')
    return redirect(url_for('merchant_products'))

@app.route('/merchant/orders')
@login_required
def merchant_orders():
    if current_user.role != 'merchant': return "拒绝", 403
    orders = Orders.query.filter_by(merchant_id=current_user.id).order_by(Orders.created_at.desc()).all()
    data = []
    for o in orders:
        u = db.session.get(User, o.user_id)
        data.append({'o': o, 'buyer': u.username if u else "未知"})
    return render_template('merchant/orders.html', orders=data)

@app.route('/merchant/ship/<int:order_id>')
@login_required
def ship_order(order_id):
    order = db.session.get(Orders, order_id)
    if order and order.merchant_id == current_user.id:
        order.status = '待收货'
        db.session.commit()
    return redirect(url_for('merchant_orders'))

@app.route('/merchant/customers')
@login_required
def merchant_customers():
    if current_user.role != 'merchant': return "拒绝", 403
    logs = ActivityLog.query.filter_by(merchant_id=current_user.id).order_by(ActivityLog.created_at.desc()).all()
    return render_template('merchant/customers.html', logs=logs)

# --- 管理员 ---

@app.route('/admin_panel')
@login_required
def admin_panel():
    if current_user.role != 'admin': return "拒绝", 403
    merchants = User.query.filter_by(role='merchant').all()
    customers = User.query.filter_by(role='customer').all()
    return render_template('admin/users.html', merchants=merchants, customers=customers)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        init_db()
    app.run(debug=True)