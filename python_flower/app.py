
from flask import Flask
from models import db, User
import os

app = Flask(__name__)
# ตั้งค่าโฟลเดอร์สำหรับเก็บรูปภาพที่อัปโหลด (ถ้าไม่มีให้สร้างอัตโนมัติ)
app.config['UPLOAD_FOLDER'] = 'static/uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

app.secret_key = 'super_secret_cat_flower_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///shop.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app) # สั่งให้ Flask รู้จักกับ db


# ===== Register Blueprints =====
from routes.auth import bp_auth
from routes.admin import bp_admin
from routes.shop import bp_shop

app.register_blueprint(bp_auth)
app.register_blueprint(bp_admin)
app.register_blueprint(bp_shop)

if __name__ == '__main__':
    # --- เพิ่มบล็อกนี้เพื่อเนรมิต Database ก่อนรันเว็บ ---
    with app.app_context():
        db.create_all() # สร้างตารางทั้งหมดตามที่เขียนไว้ใน models.py
        # เช็คว่ามีแอดมินอยู่ในระบบหรือยัง? ถ้ายังให้สร้างขึ้นมา 1 คน
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
    app.run(debug=True)
