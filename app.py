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

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form.get('password', '')  # password might be empty for user login
        login_type = request.form['loginType']

        if login_type == 'user':
            # Add your user validation logic here
            return redirect(url_for('menu'))
        elif login_type == 'admin':
            # Add your admin validation logic here
            if password:  # Check if password is provided for admin
                return redirect(url_for('menu'))
            
        # If validation fails, you might want to show an error
        return redirect(url_for('login'))

    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    username = session.get('username')
    if username == 'admin':
        return render_template('dashboard.html')
    return redirect(url_for('home'))

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

@app.route('/get_purchases')
def get_purchases():
    if not session.get('logged_in') or session.get('user_type') != 'admin':
        return jsonify({'error': 'Unauthorized'}), 401
    
    purchases = []
    purchase_dir = 'purchases'
    
    if os.path.exists(purchase_dir):
        for root, dirs, files in os.walk(purchase_dir):
            for file in files:
                if file.endswith('.receipt.txt'):
                    file_path = os.path.join(root, file)
                    try:
                        with open(file_path, 'r') as f:
                            content = f.read()
                            # Skip the header line when getting items
                            items = [line.strip() for line in content.split('\n')[1:] if line.strip()]
                            purchases.append({
                                'filename': file,
                                'content': content,
                                'items': items
                            })
                    except IOError as e:
                        print(f"Error reading file {file_path}: {e}")
                        
    return jsonify({'purchases': purchases})

if __name__ == '__main__':
    app.run(debug=True)
