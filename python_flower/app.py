from flask import Flask, render_template, request, redirect, url_for, session
from models import db, User, Flower, Billing
import os
from config import config

# 🔧 Routes
from routes.auth import register_auth_routes
from routes.admin import register_admin_routes
from routes.shop import register_shop_routes
from routes.cart import inject_cart, register_cart_routes
from routes.checkout import register_checkout_routes

# ==========================================
# สร้าง Flask App
# ==========================================
app = Flask(__name__)

# ==========================================
# ตั้งค่า Config
# ==========================================
app.config.from_object(config['development'])  # ← ใช้ Development config

# ==========================================
# สร้างโฟลเดอร์ uploads (ถ้ายังไม่มี)
# ==========================================
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# ==========================================
# ตั้งค่า Database
# ==========================================
db.init_app(app)

# ==========================================
# ลงทะเบียน Routes ทั้งหมด
# ==========================================
register_auth_routes(app)
register_admin_routes(app, app.config['UPLOAD_FOLDER'])
register_shop_routes(app)
register_cart_routes(app)
register_checkout_routes(app)

# ==========================================
# Context Processor (ส่งข้อมูลตะกร้าไปหน้า HTML)
# ==========================================
app.context_processor(inject_cart)

# ==========================================
# รันแอพ
# ==========================================
if __name__ == '__main__':
    with app.app_context():
        # สร้างตารางทั้งหมดในฐานข้อมูล
        db.create_all()
        
        # ตรวจสอบว่ามี Admin อยู่หรือไม่
        if not User.query.filter_by(username='admin').first():
            new_admin = User(
                username='admin', 
                fullname='ผู้ดูแลระบบ สูงสุด',
                phone='080-999-9999',
                password='1234', 
                role='Administrator'
            )
            db.session.add(new_admin)
            db.session.commit()
            print("✅ สร้างบัญชี Admin เริ่มต้นให้แล้ว! (User: admin / Pass: 1234)")
        
        print("🌸 Flora Haven App พร้อมใช้งาน!")

    # 🚀 รันเซิร์ฟเวอร์
    app.run(debug=True)