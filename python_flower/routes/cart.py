from flask import Blueprint, render_template, request, redirect, url_for, session
from models import db, Flower
from werkzeug.utils import secure_filename
import os
import uuid

flower_bp = Blueprint('flower', __name__)

@flower_bp.route('/add_flower', methods=['POST'])
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
            image_file.save(os.path.join('static/uploads', filename))
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

@flower_bp.route('/delete_flower/<int:id>', methods=['POST'])
def delete_flower(id):
    flower_to_delete = Flower.query.get_or_404(id)
    db.session.delete(flower_to_delete)
    db.session.commit()
    return redirect(url_for('manage_stock'))

@flower_bp.route('/edit_flower/<int:id>', methods=['GET', 'POST'])
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
            file.save(os.path.join('static/uploads', pic_name))
            flower_to_edit.image_file = pic_name
        db.session.commit()
        return redirect(url_for('manage_stock'))
    return render_template('admin_edit.html', flower=flower_to_edit)

@flower_bp.route('/manage_stock')
def manage_stock():
    all_flowers = Flower.query.all()
    return render_template('admin_stock.html', flowers=all_flowers)
