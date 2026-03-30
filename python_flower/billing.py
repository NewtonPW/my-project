# 1. คลาสแม่ของสินค้า
class Product:
    def __init__(self, name, price):
        self.name = name
        self.price = price

# 2. คลาสลูก (สืบทอดจาก Product) 🌟 Inheritance 1
class Flower(Product):
    def __init__(self, name, price, color, meaning):
        super().__init__(name, price) # ดึงคุณสมบัติ ชื่อ, ราคา จากคลาสแม่มาใช้
        self.color = color
        self.meaning = meaning

# 3. คลาสรายการสินค้าในตะกร้า (สินค้า 1 ชนิด + จำนวนที่ซื้อ)
class CartItem:
    def __init__(self, product, quantity):
        self.product = product
        self.quantity = quantity

    def get_subtotal(self):
        return self.product.price * self.quantity # ราคา x จำนวน

# 4. คลาสแม่ของใบสั่งซื้อ (คิดเงินราคาปกติ)
class Order:
    def __init__(self, customer_name):
        self.customer_name = customer_name
        self.items = [] # กล่องใส่สินค้า

    def add_item(self, cart_item):
        self.items.append(cart_item)

    def calculate_total(self):
        # รวมเงินทุกรายการในตะกร้า
        return sum(item.get_subtotal() for item in self.items)

# 5. คลาสลูก (สืบทอดจาก Order) 🌟 Inheritance 2 -> โหมดคิดเงินแบบมีส่วนลด 10%
class WholesaleOrder(Order):
    def calculate_total(self):
        # เรียกใช้การคำนวณยอดรวมปกติจากคลาสแม่มาก่อน
        base_total = super().calculate_total()
        
        # นับจำนวนชิ้นสินค้าทั้งหมดในตะกร้า
        total_quantity = sum(item.quantity for item in self.items)
        
        # ถ้ายอดสั่งซื้อรวมกันตั้งแต่ 10 ชิ้นขึ้นไป ลดเลย 10%
        if total_quantity >= 10:
            discount = base_total * 0.10
            return base_total - discount
        
        # ถ้าไม่ถึง 10 ชิ้น ก็จ่ายราคาเต็ม
        return base_total