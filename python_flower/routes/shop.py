from flask import Blueprint, render_template, request, redirect, url_for, session
from models import db, Flower, User, Billing
from billing import Product, CartItem, WholesaleOrder

bp_shop = Blueprint('shop', __name__)

# หน้าสินค้าสำหรับลูกค้า
@bp_shop.route('/shop')
def shop_page():
    all_flowers = Flower.query.all()
    return render_template('products.html', flowers=all_flowers)

# เกี่ยวกับเรา
@bp_shop.route('/about')
def about():
    return render_template('about.html')

# ติดต่อเรา
@bp_shop.route('/contact')
def contact():
    return render_template('contact.html')

# เพิ่มสินค้าลงตะกร้า
@bp_shop.route('/add_to_cart/<int:product_id>', methods=['POST'])
def add_to_cart(product_id):
    Flower.query.get_or_404(product_id)
    cart = session.get('cart', {})
    pid_str = str(product_id)
    if pid_str in cart:
        cart[pid_str] += 1
    else:
        cart[pid_str] = 1
    session['cart'] = cart
    session.modified = True
    return redirect(request.referrer or url_for('shop.shop_page'))

# ลบสินค้าออกจากตะกร้า
@bp_shop.route('/remove_from_cart/<int:product_id>')
def remove_from_cart(product_id):
    cart = session.get('cart', {})
    pid_str = str(product_id)
    if pid_str in cart:
        del cart[pid_str]
        session['cart'] = cart
        session.modified = True
    return redirect(request.referrer or url_for('shop.shop_page'))

# อัปเดตจำนวนสินค้าในตะกร้า
@bp_shop.route('/update_cart_quantity/<int:product_id>', methods=['POST'])
def update_cart_quantity(product_id):
    cart = session.get('cart', {})
    pid_str = str(product_id)
    action = request.form.get('action')
    if pid_str in cart:
        if action == 'increase':
            cart[pid_str] += 1
        elif action == 'decrease':
            if cart[pid_str] > 1:
                cart[pid_str] -= 1
            else:
                del cart[pid_str]
        session['cart'] = cart
        session.modified = True
    return redirect(request.referrer or url_for('shop.shop_page'))

# Checkout
@bp_shop.route('/checkout', methods=['GET', 'POST'])
def checkout():
    if 'username' not in session:
        return redirect(url_for('auth.login'))
    cart = session.get('cart', {})
    if not cart:
        return redirect(url_for('shop.shop_page'))
    total_quantity = sum(int(quantity) for quantity in cart.values())
    current_user = User.query.filter_by(username=session['username']).first()
    customer_name = session.get('username', 'Guest')
    my_order = WholesaleOrder(customer_name)
    cart_items_details = []
    for product_id, quantity in cart.items():
        flower = Flower.query.get(int(product_id))
        if flower:
            qty = int(quantity)
            subtotal = flower.price * qty
            cart_items_details.append({'flower': flower, 'quantity': qty, 'subtotal': subtotal})
            prod = Product(flower.name, float(flower.price))
            cart_item_oop = CartItem(prod, qty)
            my_order.add_item(cart_item_oop)
    final_total = my_order.calculate_total()
    if request.method == 'POST':
        new_fullname = request.form.get('fullname')
        new_phone = request.form.get('phone')
        new_address = request.form.get('address')
        new_payment = request.form.get('payment_method')
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
        session.pop('cart', None)
        session.modified = True
        return redirect(url_for('shop.shop_page'))
    return render_template('checkout.html', user=current_user, cart_items_details=cart_items_details, cart_total_price=final_total, total_quantity=total_quantity)

# Cart context processor
from flask import current_app
@bp_shop.app_context_processor
def inject_cart():
    cart = session.get('cart', {})
    total_items_in_cart = 0
    total_price = 0
    cart_items_details = []
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
    return dict(
        cart_items_details=cart_items_details,
        cart_total_price=total_price,
        cart_total_items=total_items_in_cart
    )
