from flask import render_template, request, redirect, url_for, session
from models import db, Flower, Billing
import os
from werkzeug.utils import secure_filename
import uuid

def register_admin_routes(app, UPLOAD_FOLDER):
    @app.route('/admin')
    def admin_page():
        if session.get('role') != 'Administrator':
            return redirect(url_for('login'))
        return render_template('admin.html')

    @app.route('/add_flower', methods=['POST'])
    def add_flower():
        if request.method == 'POST':
            new_name = request.form.get('name')
            new_date = request.form.get('stock_date')
            new_color = request.form.get('color')
            new_price = request.form.get('price')
            
            image_file = request.files.get('image')
            filename = 'default.jpg'
            
            if image_file and image_file.filename != '':
                filename = secure_filename(image_file.filename)
                image_file.save(os.path.join(UPLOAD_FOLDER, filename))
            
            new_flower = Flower(
                name=new_name,
                stock_date=new_date,
                color=new_color,
                price=float(new_price),
                image_file=filename
            )
            
            db.session.add(new_flower)
            db.session.commit()
            
            return render_template('admin.html', success_msg="เพิ่มดอกไม้เข้าสต็อกสำเร็จ! 🎉")

    @app.route('/delete_flower/<int:id>', methods=['POST'])
    def delete_flower(id):
        flower_to_delete = Flower.query.get_or_404(id)
        db.session.delete(flower_to_delete)
        db.session.commit()
        return redirect(url_for('manage_stock'))

    @app.route('/edit_flower/<int:id>', methods=['GET', 'POST'])
    def edit_flower(id):
        flower_to_edit = Flower.query.get_or_404(id)
        
        if request.method == 'POST':
            flower_to_edit.name = request.form['name']
            flower_to_edit.stock_date = request.form['stock_date']
            flower_to_edit.color = request.form['color']
            flower_to_edit.price = request.form['price']
            
            file = request.files['image']
            if file and file.filename != '':
                filename = secure_filename(file.filename)
                pic_name = str(uuid.uuid1()) + "_" + filename
                file.save(os.path.join(UPLOAD_FOLDER, pic_name))
                flower_to_edit.image_file = pic_name
                
            db.session.commit()
            return redirect(url_for('manage_stock'))
            
        return render_template('admin_edit.html', flower=flower_to_edit)

    @app.route('/manage_stock')
    def manage_stock():
        all_flowers = Flower.query.all()
        return render_template('admin_stock.html', flowers=all_flowers)

    @app.route('/manage_orders')
    def manage_orders():
        if session.get('role') != 'Administrator':
            return redirect(url_for('login'))
        all_bills = Billing.query.order_by(Billing.id.desc()).all()
        return render_template('admin_orders.html', bills=all_bills)

    @app.route('/update_order_status/<int:bill_id>', methods=['POST'])
    def update_order_status(bill_id):
        if session.get('role') != 'Administrator':
            return redirect(url_for('login'))
        bill = Billing.query.get_or_404(bill_id)
        new_status = request.form.get('status')
        bill.status = new_status
        db.session.commit()
        return redirect(url_for('manage_orders'))