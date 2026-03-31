from flask import Blueprint, render_template, request, redirect, url_for, session
from models import db, User

bp_auth = Blueprint('auth', __name__)

# หน้าเข้าสู่ระบบ
@bp_auth.route('/', methods=['GET', 'POST'])
@bp_auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username_from_web = request.form.get('username')
        password_from_web = request.form.get('password')
        login_role_from_web = request.form.get('login_role')

        user = User.query.filter_by(username=username_from_web).first()

        if user and user.password == password_from_web:
            if user.role != login_role_from_web:
                error_text = f"คุณไม่มีสิทธิ์เข้าโหมดนี้! (คุณคือ {user.role}) ❌"
                return render_template('login.html', error_msg=error_text)
            session['username'] = user.username
            session['role'] = user.role
            if user.role == 'Administrator':
                return redirect(url_for('admin.admin_page'))
            else:
                return redirect(url_for('shop.shop_page'))
        else:
            error_text = "ชื่อผู้ใช้ หรือ รหัสผ่าน ไม่ถูกต้อง กรุณาลองใหม่ ❌"
            return render_template('login.html', error_msg=error_text)
    return render_template('login.html')

@bp_auth.route('/logout')
def logout():
    session.clear()
    return redirect('/')

# หน้าสมัครสมาชิก
@bp_auth.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        new_fullname = request.form.get('fullname')
        new_phone = request.form.get('phone')
        new_email = request.form.get('email')
        new_password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        if new_password != confirm_password:
            return "รหัสผ่านและการยืนยันรหัสผ่านไม่ตรงกัน กรุณาลองใหม่ ❌"
        existing_user = User.query.filter_by(username=new_email).first()
        if existing_user:
            return "อีเมลนี้มีคนใช้งานแล้ว กรุณาใช้อีเมลอื่น ❌"
        new_user = User(
            username=new_email,
            fullname=new_fullname,
            phone=new_phone,
            password=new_password,
            role='Customer'
        )
        db.session.add(new_user)
        db.session.commit()
        return render_template('login.html', success_msg="สมัครสมาชิกสำเร็จ! 🎉 กรุณาเข้าสู่ระบบเพื่อใช้งาน")
    return render_template('register.html')
