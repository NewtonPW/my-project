from flask import render_template, redirect, url_for
from models import Flower

def register_shop_routes(app):
    @app.route('/shop')
    def shop_page():
        all_flowers = Flower.query.all()
        return render_template('products.html', flowers=all_flowers)

    @app.route('/about')
    def about():
        return render_template('about.html')

    @app.route('/contact')
    def contact():
        return render_template('contact.html')