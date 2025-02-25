from flask import Flask, render_template, request, redirect, url_for, session, jsonify, flash
import datetime
import os
from chatbot import GroceryStoreRecommender
from shop import Shop
from shopping import ShoppingCart

app = Flask(__name__)
app.secret_key = 'your-secret-key'

# Global dictionary to store shopping cart instances by username
user_carts = {}

# Instantiate the recommender once
recommender = GroceryStoreRecommender()

@app.route('/')
def home():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    username = request.form.get('username')
    if username and username.isalnum():
        session['username'] = username
        date_str = datetime.datetime.now().strftime("%Y%m%d")
        increment = 1
        if not os.path.exists('purchases'):
            os.makedirs('purchases')
        while True:
            receipt_filename = f"purchases/{username}.{date_str}.{increment}.receipt.txt"
            if not os.path.exists(receipt_filename):
                with open(receipt_filename, 'w') as f:
                    f.write(f"Receipt for {username} on {date_str}\n")
                session['receipt'] = receipt_filename
                break
            increment += 1
        return redirect(url_for('menu'))
    else:
        return render_template('login.html', error="Invalid username. Only letters and numbers allowed.")

@app.route('/add_to_cart', methods=['POST'])
def add_to_cart():
    data = request.get_json()
    item = data.get('item')
    quantity = data.get('quantity')
    if quantity and quantity.strip():
        try:
            qty = int(quantity)
        except ValueError:
            flash("Invalid quantity provided.")
            return jsonify({"message": "Invalid quantity provided."}), 400
        
        username = session.get('username')
        if not username:
            flash("User not found. Please log in again.")
            return jsonify({"message": "User not found. Please log in again."}), 400
        
        cart = user_carts.get(username)
        if not cart:
            cart = ShoppingCart()
            user_carts[username] = cart
        
        cart.add_to_cart(item.split(", ")[0], int(item.split(", ")[1]), qty)
        flash(f"Added {qty} of {item} to your cart.")
        return jsonify({"message": f"Added {qty} of {item} to your cart."})
    else:
        flash("Quantity not provided!")
        return jsonify({"message": "Quantity not provided!"}), 400

@app.route('/menu')
def menu():
    username = session.get('username')
    if not username:
        return redirect(url_for('home'))
    return render_template('menu.html', username=username)

@app.route('/recommend', methods=['GET', 'POST'])
def recommend():
    if request.method == 'POST':
        query = request.form.get('query')
        if query:
            recommendations = recommender.recommendItems(query)
            return render_template('recommend.html', query=query, recommendations=recommendations)
        else:
            return render_template('recommend.html', error="Please enter a query.")
    return render_template('recommend_form.html')

@app.route('/shop')
def shop():
    if 'username' not in session:
        return redirect(url_for('home'))
    shop_instance = Shop(ShoppingCart())  
    return render_template('shop.html', categories=shop_instance.categories)

@app.route('/category/<category>')
def view_category(category):
    shop_instance = Shop(ShoppingCart())
    items = shop_instance.display_products(category)
    if items:
        return render_template('category.html', category=category, items=items)
    else:
        flash("Category not found.")
        return redirect(url_for('shop'))

@app.route('/cart')
def cart():
    username = session.get('username')
    if not username or username not in user_carts:
        flash("No shopping cart found.")
        return redirect(url_for('menu'))
    user_cart = user_carts[username]
    return render_template('cart.html', cart=user_cart.cart)

@app.route('/checkout', methods=['POST'])
def checkout():
    receipt = session.get('receipt')
    username = session.get('username')
    if username and username in user_carts:
        cart = user_carts[username]
        if cart.checkout(receipt):
            flash("Checkout successful!")
        else:
            flash("Your cart is empty. Please add items before checking out.")
        user_carts.pop(username, None)
    else:
        flash("No cart found to checkout.")
    return render_template('checkout.html', receipt=receipt)

if __name__ == '__main__':
    app.run(debug=True)