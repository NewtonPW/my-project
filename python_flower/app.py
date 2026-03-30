from flask import Flask, render_template, request, redirect, url_for, session
from models import db, User, Flower, Billing
import os
from werkzeug.utils import secure_filename
from billing import Product, CartItem, WholesaleOrder
import uuid
# Hiiiiiiii
app = Flask(__name__)
# ตั้งค่าโฟลเดอร์สำหรับเก็บรูปภาพที่อัปโหลด (ถ้าไม่มีให้สร้างอัตโนมัติ)
app.config['UPLOAD_FOLDER'] = 'static/uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
# Hiii
app.secret_key = 'super_secret_cat_flower_key'
# 67
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///shop.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app) # สั่งให้ Flask รู้จักกับ db

# 1. หน้าเข้าสู่ระบบ (ตั้งเป็นหน้าแรกของเว็บด้วย)
@app.route('/')
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username_from_web = request.form.get('username')
        password_from_web = request.form.get('password')
        login_role_from_web = request.form.get('login_role')

        user = User.query.filter_by(username=username_from_web).first()

        if user and user.password == password_from_web:
            
            # 🛑 ถ้าสิทธิ์ไม่ตรงกัน ให้ส่งข้อความ Error สีแดงกลับไปหน้า Login
            if user.role != login_role_from_web:
                error_text = f"คุณไม่มีสิทธิ์เข้าโหมดนี้! (คุณคือ {user.role}) ❌"
                return render_template('login.html', error_msg=error_text)

            session['username'] = user.username
            session['role'] = user.role

            if user.role == 'Administrator':
                return redirect(url_for('admin_page'))
            else:
                return redirect(url_for('shop_page'))
        
        else:
            # ❌ ถ้ารหัสผิด ให้ส่งข้อความ Error สีแดงกลับไปหน้า Login
            error_text = "ชื่อผู้ใช้ หรือ รหัสผ่าน ไม่ถูกต้อง กรุณาลองใหม่ ❌"
            return render_template('login.html', error_msg=error_text)

    # ถ้าเข้าเว็บมาตอนแรก (ยังไม่ได้กดปุ่มอะไร)
    return render_template('login.html')

@app.route('/logout')
def logout():
    # ล้างข้อมูลคนที่ล็อกอินอยู่ออกให้หมด
    session.clear()
    
    # ล้างเสร็จแล้ว ให้เด้งกลับไปที่หน้าแรกสุด (หน้า /)
    return redirect('/')

# 2. หน้าสมัครสมาชิก
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        # 📦 1. แกะกล่องพัสดุจากหน้าเว็บให้ครบทุกกล่อง
        new_fullname = request.form.get('fullname')  # รับชื่อ-นามสกุล
        new_phone = request.form.get('phone')        # รับเบอร์โทร
        new_email = request.form.get('email')        # รับอีเมล
        new_password = request.form.get('password')  # รับรหัสผ่าน
        confirm_password = request.form.get('confirm_password') # รับยืนยันรหัสผ่าน
        
        # 🛑 เช็คว่ากรอกรหัสผ่าน 2 ช่องตรงกันไหม?
        if new_password != confirm_password:
            return "รหัสผ่านและการยืนยันรหัสผ่านไม่ตรงกัน กรุณาลองใหม่ ❌"

        # 🔍 2. เช็คก่อนว่ามีคนใช้อีเมลนี้สมัครไปหรือยัง?
        existing_user = User.query.filter_by(username=new_email).first()
        if existing_user:
            return "อีเมลนี้มีคนใช้งานแล้ว กรุณาใช้อีเมลอื่น ❌"

        # 🏢 3. สร้าง User ใหม่ (ใส่ข้อมูลให้ครบทุกช่องตามที่เราสร้างไว้ในโกดัง)
        new_user = User(
            username=new_email, 
            fullname=new_fullname,  # 🌟 ใส่ชื่อ-นามสกุล
            phone=new_phone,        # 🌟 ใส่เบอร์โทร
            password=new_password, 
            role='Customer'
        )
        
        # 💾 4. สั่งบันทึกลงฐานข้อมูล
        db.session.add(new_user)
        db.session.commit()

        return render_template('login.html', success_msg="สมัครสมาชิกสำเร็จ! 🎉 กรุณาเข้าสู่ระบบเพื่อใช้งาน")

    return render_template('register.html')
# 3.รับข้อมูลดอกไม้
@app.route('/add_flower', methods=['POST'])
def add_flower():
    if request.method == 'POST':
        # 1. รับข้อมูลแบบข้อความ
        new_name = request.form.get('name')
        new_date = request.form.get('stock_date')
        new_color = request.form.get('color')
        new_price = request.form.get('price')
        
        # 2. จัดการเรื่องไฟล์รูปภาพ
        image_file = request.files.get('image')
        filename = 'default.jpg' # ถ้าไม่ได้อัปร้านจะใช้รูปนี้แทน
        
        if image_file and image_file.filename != '':
            # ทำให้ชื่อไฟล์ปลอดภัย (ลบตัวอักษรแปลกๆ ทิ้ง)
            filename = secure_filename(image_file.filename)
            # เซฟไฟล์รูปลงไปในโฟลเดอร์ static/uploads/
            image_file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        
        # 3. บันทึกข้อมูลลงฐานข้อมูล
        new_flower = Flower(
            name=new_name,
            stock_date=new_date,
            color=new_color,
            price=float(new_price), # แปลงราคาให้เป็นตัวเลขทศนิยม
            image_file=filename     # ใส่ชื่อไฟล์รูปลงไป
        )
        
        db.session.add(new_flower)
        db.session.commit()
        
        return render_template('admin.html', success_msg="เพิ่มดอกไม้เข้าสต็อกสำเร็จ! 🎉")

# ==========================================
# ฟังก์ชันลบดอกไม้
# ==========================================
@app.route('/delete_flower/<int:id>', methods=['POST'])
def delete_flower(id):
    flower_to_delete = Flower.query.get_or_404(id)
    
    # คำสั่งลบจาก Database
    db.session.delete(flower_to_delete)
    db.session.commit()
    
    # กลับไปหน้าจัดการสต็อก
    return redirect(url_for('manage_stock'))

# ==========================================
# ฟังก์ชันแก้ไขดอกไม้
# ==========================================
@app.route('/edit_flower/<int:id>', methods=['GET', 'POST'])
def edit_flower(id):
    flower_to_edit = Flower.query.get_or_404(id)
    
    if request.method == 'POST':
        # 1. รับค่าใหม่จากฟอร์มมาทับค่าเดิม
        flower_to_edit.name = request.form['name']
        flower_to_edit.stock_date = request.form['stock_date']
        flower_to_edit.color = request.form['color']
        flower_to_edit.price = request.form['price']
        
        # 2. เช็คว่ามีการอัปโหลดรูปภาพใหม่มาด้วยไหม?
        file = request.files['image']
        if file and file.filename != '':
            # สร้างชื่อไฟล์ใหม่และบันทึก
            filename = secure_filename(file.filename)
            pic_name = str(uuid.uuid1()) + "_" + filename
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], pic_name))
            
            # อัปเดตชื่อรูปใน Database
            flower_to_edit.image_file = pic_name
            
        # 3. เซฟลง Database
        db.session.commit()
        return redirect(url_for('manage_stock'))
        
    # ถ้าเป็น GET (แค่กดปุ่มเข้ามา) ให้เปิดหน้า admin_edit.html พร้อมส่งข้อมูลเก่าไปแสดง
    return render_template('admin_edit.html', flower=flower_to_edit)
# ==========================================
# หน้าจัดการสต็อกดอกไม้ (Admin)
# ==========================================
@app.route('/manage_stock')
def manage_stock():
    # 1. สั่งให้ดึงข้อมูลดอกไม้ "ทั้งหมด" จาก Database
    all_flowers = Flower.query.all()
    
    # 2. ส่งข้อมูลไปที่หน้า admin_stock.html ผ่านตัวแปรชื่อ flowers
    return render_template('admin_stock.html', flowers=all_flowers)
# ==========================================
# 📦 หน้าจัดการคำสั่งซื้อ (สำหรับ Admin)
# ==========================================
@app.route('/manage_orders')
def manage_orders():
    # 1. ป้องกันไม่ให้คนอื่นแอบเข้า ต้องเป็นแอดมินเท่านั้น
    if session.get('role') != 'Administrator':
        return redirect(url_for('login'))
        
    # 2. ดึงข้อมูลคำสั่งซื้อทั้งหมดจากคลาส Billing (เรียงจากใหม่สุดไปเก่าสุด)
    # (สมมติว่าคุณมีคลาส Billing ใน models.py แล้วนะครับ)
    all_bills = Billing.query.order_by(Billing.id.desc()).all()
    
    return render_template('admin_orders.html', bills=all_bills)

# 🔄 ฟังก์ชันสำหรับกดเปลี่ยนสถานะคำสั่งซื้อ
@app.route('/update_order_status/<int:bill_id>', methods=['POST'])
def update_order_status(bill_id):
    if session.get('role') != 'Administrator':
        return redirect(url_for('login'))
        
    # ดึงบิลที่ต้องการแก้ขึ้นมา
    bill = Billing.query.get_or_404(bill_id)
    # รับค่าสถานะใหม่จาก Dropdown ที่แอดมินเลือก
    new_status = request.form.get('status')
    
    # อัปเดตและบันทึกลง Database
    bill.status = new_status
    db.session.commit()
    
    return redirect(url_for('manage_orders'))
# ==========================================
# หน้าสินค้าสำหรับลูกค้า (Shop Page)
# ==========================================
@app.route('/shop')
def shop_page():
    # 1. สั่งให้ดึงข้อมูลดอกไม้ "ทั้งหมด" จาก Database เพื่อมาโชว์ลูกค้า
    all_flowers = Flower.query.all()
    
    # 2. ส่งข้อมูลดอกไม้ไปที่หน้า products.html ผ่านตัวแปรชื่อ flowers
    # (เราอาจจะส่งค่าอื่นๆ ไปด้วย เช่น หัวข้อหน้าเว็บ)
    return render_template('products.html', flowers=all_flowers)

# 4. หน้าเกี่ยวกับเรา
@app.route('/about')
def about():
    return render_template('about.html')

# 5. หน้าติดต่อเรา
@app.route('/contact')
def contact():
    return render_template('contact.html')

# 6. หน้าแอดมิน (จัดการร้านดอกไม้) - มีระบบป้องกัน
@app.route('/admin')
def admin_page():
    # ตรวจสอบว่าสายรัดข้อมือ (session) มีคำว่า 'Administrator' ไหม?
    if session.get('role') != 'Administrator':
        # ถ้าไม่มี หรือไม่ได้ล็อกอิน ให้เด้งกลับไปหน้า login ทันที!
        return redirect(url_for('login'))
        
    # ถ้าใช่แอดมิน ถึงจะยอมให้เปิดหน้า admin.html
    return render_template('admin.html')

# ==========================================
# 🛒 ระบบตะกร้าสินค้า (Cart System)
# ==========================================

@app.context_processor
def inject_cart():
    # ดึงตะกร้าจาก Session (ถ้าไม่มีให้เป็น dict ว่าง)
    cart = session.get('cart', {})
    total_items_in_cart = 0
    total_price = 0
    cart_items_details = []

    # ถ้าในตะกร้ามีของ ให้ไปดึงรายละเอียดจาก Database มาคำนวณราคา
    if cart:
        for product_id_str, quantity in cart.items():
            product_id = int(product_id_str)
            flower = Flower.query.get(product_id)
            if flower:
                subtotal = flower.price * quantity
                total_items_in_cart += quantity
                total_price += subtotal
                cart_items_details.append({
                    'flower': flower,
                    'quantity': quantity,
                    'subtotal': subtotal
                })
    
    # ส่งตัวแปรพวกนี้ไปให้ HTML ใช้ได้ทันที
    return dict(
        cart_items_details=cart_items_details, 
        cart_total_price=total_price, 
        cart_total_items=total_items_in_cart
    )

# ➕ 1. ฟังก์ชันเพิ่มสินค้าลงตะกร้า (ใช้ POST)
@app.route('/add_to_cart/<int:product_id>', methods=['POST'])
def add_to_cart(product_id):
    # ตรวจสอบว่ามีสินค้านี้จริงไหม
    Flower.query.get_or_404(product_id)
    
    cart = session.get('cart', {}) # ดึงตะกร้าเดิม

    # ทำให้เป็น string เพื่อใช้เป็น Key ใน Dictionary ของ Session
    pid_str = str(product_id)
    
    if pid_str in cart:
        cart[pid_str] += 1 # ถ้ามีแล้ว เพิ่มจำนวน
    else:
        cart[pid_str] = 1 # ถ้ายังไม่มี เพิ่มใหม่
    
    session['cart'] = cart # เซฟกลับลง session
    session.modified = True # แจ้ง Flask ว่าข้อมูลมีการเปลี่ยนแปลง

    # กลับไปหน้าเดิมที่ลูกค้ากดมา
    return redirect(request.referrer or url_for('shop_page'))

# ❌ 2. ฟังก์ชันลบสินค้าออกจากตะกร้า
@app.route('/remove_from_cart/<int:product_id>')
def remove_from_cart(product_id):
    cart = session.get('cart', {})
    pid_str = str(product_id)
    
    if pid_str in cart:
        del cart[pid_str] # ลบ Key นี้ทิ้ง
        session['cart'] = cart
        session.modified = True
        
    return redirect(request.referrer or url_for('shop_page'))

# 🔄 3. ฟังก์ชันอัปเดตจำนวนสินค้า (กดปุ่ม + หรือ - ในตะกร้า)
@app.route('/update_cart_quantity/<int:product_id>', methods=['POST'])
def update_cart_quantity(product_id):
    cart = session.get('cart', {})
    pid_str = str(product_id)
    action = request.form.get('action') # 'increase' หรือ 'decrease'

    if pid_str in cart:
        if action == 'increase':
            cart[pid_str] += 1
        elif action == 'decrease':
            if cart[pid_str] > 1:
                cart[pid_str] -= 1
            else:
                del cart[pid_str] # ถ้าน้อยกว่า 1 ให้ลบทิ้ง
                
        session['cart'] = cart
        session.modified = True
        
    return redirect(request.referrer or url_for('shop_page'))

@app.route('/checkout', methods=['GET', 'POST'])
def checkout():
    # 🔴 1. เช็คก่อนว่าลูกค้าล็อกอินหรือยัง? (เช็คจาก session)
    if 'username' not in session:
        return redirect(url_for('login'))

    # 🔴 2. ถ้าไม่มีของในตะกร้า ให้กลับไปหน้าสินค้า
    cart = session.get('cart', {})
    if not cart:
        return redirect(url_for('shop_page')) # เปลี่ยนเป็นชื่อฟังก์ชันหน้าสินค้าของคุณ
    
    total_quantity = sum(int(quantity) for quantity in cart.values())

    # 🌟 3. ดึงข้อมูลลูกค้าคนปัจจุบันจาก Database
    current_user = User.query.filter_by(username=session['username']).first()

    # ==========================================
    # 🌟 เริ่มเรียกใช้คลาส OOP เพื่อคำนวณยอดรวม
    # ==========================================
    customer_name = session.get('username', 'Guest')
    my_order = WholesaleOrder(customer_name)
    
    cart_items_details = [] 
    
    # 🌟 สังเกตตรงนี้: เปลี่ยนจาก item เป็น quantity เพราะมันคือตัวเลขจำนวนชิ้นเลย
    for product_id, quantity in cart.items(): 
        flower = Flower.query.get(int(product_id))
        
        if flower:
            # ใช้ตัวเลข quantity ได้เลยตรงๆ ไม่ต้องมี ['quantity'] แล้ว
            qty = int(quantity) 
            subtotal = flower.price * qty
            
            # เก็บข้อมูลใส่ list ไว้ส่งไปโชว์ที่หน้าเว็บ
            cart_items_details.append({'flower': flower, 'quantity': qty, 'subtotal': subtotal})
            
            # แปลงของในตะกร้าให้เป็น Object เพื่อใส่ในบิล (OOP)
            prod = Product(flower.name, float(flower.price))
            cart_item_oop = CartItem(prod, qty)
            my_order.add_item(cart_item_oop)
        
    # ให้ระบบคำนวณยอดรวมให้ (ถ้าถึง 10 ชิ้น จะหัก 10% อัตโนมัติ)
    final_total = my_order.calculate_total()
    # ==========================================

    if request.method == 'POST':
        # 📦 รับข้อมูลจากฟอร์มที่ลูกค้ากรอก
        new_fullname = request.form.get('fullname')
        new_phone = request.form.get('phone')
        new_address = request.form.get('address')
        new_payment = request.form.get('payment_method')

        # ==========================================
        # 💾 ส่วนที่เพิ่มเข้ามา: บันทึกลงตาราง Billing (ส่งให้ Admin)
        # ==========================================
        new_order = Billing(
            customer_name=new_fullname,
            phone=new_phone,
            address=new_address,
            payment_method=new_payment,
            total_price=final_total
        )
        
        try:
            db.session.add(new_order)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            return f"เกิดข้อผิดพลาดในการบันทึกข้อมูล: {e}"
        # ==========================================

        # 🧹 ล้างข้อมูลในตะกร้าทิ้งเมื่อสั่งซื้อและบันทึกข้อมูลเสร็จ
        session.pop('cart', None)
        session.modified = True

        # 🚀 สั่งซื้อสำเร็จ ให้เด้งกลับไปหน้าแรก (เปลี่ยน 'shop_page' ให้ตรงกับชื่อหน้าของคุณ)
        return redirect(url_for('shop_page'))

    # 🌟 4. ส่งข้อมูลไปหน้า HTML
    return render_template('checkout.html', user=current_user, cart_items_details=cart_items_details, cart_total_price=final_total, total_quantity=total_quantity)

if __name__ == '__main__':
   # --- เพิ่มบล็อกนี้เพื่อเนรมิต Database ก่อนรันเว็บ ---
 with app.app_context():
    db.create_all() # สร้างตารางทั้งหมดตามที่เขียนไว้ใน models.py
    
    # เช็คว่ามีแอดมินอยู่ในระบบหรือยัง? ถ้ายังให้สร้างขึ้นมา 1 คน
    if not User.query.filter_by(username='admin').first():
        new_admin = User(
            username='admin', 
            fullname='ผู้ดูแลระบบ สูงสุด',     # 🌟 เพิ่มข้อมูลชื่อ
            phone='080-999-9999',         # 🌟 เพิ่มข้อมูลเบอร์โทร
            password='1234', 
            role='Administrator'
        )
        db.session.add(new_admin)
        db.session.commit()
        print("✅ สร้างบัญชี Admin เริ่มต้นให้แล้ว! (User: admin / Pass: 1234)")
# ---------------------------------------------------

    app.run(debug=True)
