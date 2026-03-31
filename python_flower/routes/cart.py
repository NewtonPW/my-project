from flask import session, request, redirect, url_for
from models import Flower
from billing import CartItem, WholesaleOrder, Flower as OOPFlower

def inject_cart():
    """🌟 Context processor สำหรับส่งข้อมูลตะกร้าไปให้ HTML"""
    cart = session.get('cart', {})
    cart_items_details = []
    total_items_in_cart = 0
    
    my_order = WholesaleOrder("ลูกค้าทั่วไป")

    if cart:
        for product_id_str, quantity in cart.items():
            flower_db = Flower.query.get(int(product_id_str))
            
            if flower_db:
                qty = int(quantity)
                total_items_in_cart += qty
                
                oop_flower = OOPFlower(
                    name=flower_db.name,
                    price=flower_db.price,
                    color=flower_db.color,
                    meaning="ดอกไม้สื่อความหมายดีๆ"
                )
                
                item_oop = CartItem(product=oop_flower, quantity=qty)
                my_order.add_item(item_oop)
                
                cart_items_details.append({
                    'flower': flower_db,
                    'quantity': qty,
                    'subtotal': item_oop.get_subtotal() 
                })
    
    return dict(
        cart_items_details=cart_items_details, 
        cart_total_price=my_order.calculate_total(), 
        cart_total_items=total_items_in_cart
    )

def register_cart_routes(app):
    @app.route('/add_to_cart/<int:product_id>', methods=['POST'])
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
        return redirect(request.referrer or url_for('shop_page'))

    @app.route('/remove_from_cart/<int:product_id>')
    def remove_from_cart(product_id):
        cart = session.get('cart', {})
        pid_str = str(product_id)
        
        if pid_str in cart:
            del cart[pid_str]
            session['cart'] = cart
            session.modified = True
            
        return redirect(request.referrer or url_for('shop_page'))

    @app.route('/update_cart_quantity/<int:product_id>', methods=['POST'])
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
            
        return redirect(request.referrer or url_for('shop_page'))