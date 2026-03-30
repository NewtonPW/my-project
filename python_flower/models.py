from flask_sqlalchemy import SQLAlchemy

# สร้างตัวแทนของ Database
db = SQLAlchemy()

# 1. สร้างตารางเก็บข้อมูลผู้ใช้งาน (User)
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False) # เราจะเก็บ "อีเมล" ไว้ช่องนี้
    fullname = db.Column(db.String(100))                             # 🌟 ชั้นวางใหม่: ชื่อ-นามสกุล
    phone = db.Column(db.String(20))                                 # 🌟 ชั้นวางใหม่: เบอร์โทร
    password = db.Column(db.String(100), nullable=False)             # รหัสผ่าน
    role = db.Column(db.String(20), nullable=False)                  # ตำแหน่ง (Admin/Customer)

# 2. สร้างตารางเก็บข้อมูลดอกไม้ (Flower)
class Flower(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)                 # ชื่อดอกไม้
    price = db.Column(db.Float, nullable=False)                      # ราคา
    color = db.Column(db.String(50))                                 # สี
    stock_date = db.Column(db.String(50))                            # วันที่นำเข้า
    image_file = db.Column(db.String(255), nullable=True, default='default.jpg')

# ==========================================
# ตารางเก็บข้อมูลคำสั่งซื้อ (บิลลูกค้า)
# ==========================================
class Billing(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    customer_name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    address = db.Column(db.Text, nullable=False)
    payment_method = db.Column(db.String(50), nullable=False)
    total_price = db.Column(db.Float, nullable=False, default=0.0)
    status = db.Column(db.String(50), default='Pending') # สถานะคำสั่งซื้อ (Pending, Completed, Cancelled)