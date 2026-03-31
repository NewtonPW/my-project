from flask import render_template, request, redirect, url_for, session
from models import db, User, Flower, Billing
from billing import CartItem, WholesaleOrder, Flower as OOPFlower

def register_checkout_routes(app):
    @app.route('/checkout', methods=['GET', 'POST'])
    def checkout():
        if 'username' not in session:
            return redirect(url_for('login'))

        cart = session.get('cart', {})
        if not cart:
            return redirect(url_for('shop_page'))
        
        total_quantity = sum(int(quantity) for quantity in cart.values())
        current_user = User.query.filter_by(username=session['username']).first()

        customer_name = session.get('username', 'Guest')
        my_order = WholesaleOrder(customer_name)
        
        cart_items_details = [] 
        
        for product_id, quantity in cart.items(): 
            flower = Flower.query.get(int(product_id))
            
            if flower:
                qty = int(quantity) 
                
                oop_flower = OOPFlower(
                    name=flower.name, 
                    price=float(flower.price), 
                    color=flower.color, 
                    meaning="ดอกไม้จัดช่อ"
                )
                
                cart_item_oop = CartItem(oop_flower, qty)
                my_order.add_item(cart_item_oop)
                
                cart_items_details.append({
                    'flower': flower, 
                    'quantity': qty, 
                    'subtotal': cart_item_oop.get_subtotal()
                })
                
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
                total_price=final_total,
                username=session['username']
            )
            
            try:
                db.session.add(new_order)
                db.session.commit()
            except Exception as e:
                db.session.rollback()
                return f"เกิดข้อผิดพลาดในการบันทึกข้อมูล: {e}"

            session.pop('cart', None)
            session.modified = True
            return redirect(url_for('shop_page'))

        return render_template('checkout.html', user=current_user, cart_items_details=cart_items_details, cart_total_price=final_total, total_quantity=total_quantity)

    @app.route('/my_orders')
    def my_orders():
        if 'username' not in session:
            return redirect(url_for('login'))
        
        current_username = session['username']
        current_user_info = User.query.filter_by(username=current_username).first()
        user_orders = Billing.query.filter_by(username=current_username).all()
        
        return render_template('my_orders.html', orders=user_orders, user=current_user_info)