from flask import session
from models import Flower
from billing import CartItem, WholesaleOrder, Flower as OOPFlower

def inject_cart():
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
