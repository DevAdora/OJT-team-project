from flask import Flask, render_template, request, redirect, url_for, session, jsonify, flash
import datetime
import os
from chatbot import GroceryStoreRecommender
from shop import Shop
from cart import ShoppingCart
from admin import Admin

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
    logintype = request.form.get('login_type')
    
    if logintype == 'admin':
        admin_username = 'admin'
        admin_password = 'admin'
        password = request.form.get('password')
        
        if username == admin_username and password == admin_password:
            session['username'] = username
            session['logintype'] = 'admin'
            return redirect(url_for('dashboard'))
        else:
            return render_template('login.html', error="Invalid admin credentials.")
    
    elif logintype == 'user':
        if username and username.isalnum():
            session['username'] = username
            session['logintype'] = 'user'
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
    else:
        return render_template('login.html', error="Invalid login type.")

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
        
        item_name, item_price = item.split(', ')
        cart.add_to_cart(item_name, int(item_price), qty)
        flash(f"Added {qty} of {item_name} to your cart.")
        return jsonify({"message": f"Added {qty} of {item_name} to your cart."})
    else:
        flash("Quantity not provided!")
        return jsonify({"message": "Quantity not provided!"}), 400
    
@app.route('/get_receipt/<filename>')
def get_receipt(filename):
    folder_path = "purchases"  # Folder where receipt files are stored
    file_path = os.path.join(folder_path, filename)

    if not os.path.exists(file_path):
        return jsonify({"error": "Receipt not found"}), 404

    try:
        with open(file_path, "r", encoding="utf-8") as file:
            lines = file.readlines()

        if len(lines) < 3:
            return jsonify({"error": "Invalid receipt format"}), 400

        # Extract customer name from filename (e.g., "tiki.20250226.txt" -> "tiki")
        customer = filename.split(".")[0]
        date = filename.split(".")[1]  # Extract date part from filename
        formatted_date = f"{date[:4]}-{date[4:6]}-{date[6:]}"  # Convert to YYYY-MM-DD

        items = []
        total = "0"

        for line in lines[2:]:  # Skip the first two lines
            line = line.strip()
            if line.startswith("- "):  # Item purchased
                items.append(line[2:])  # Remove "- " prefix
            elif line.lower().startswith("total:"):  # Extract total
                total = line.split("₱")[1].strip()

        return jsonify({
            "customer": customer,
            "date": formatted_date,
            "items": items,
            "total": total
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500
@app.route('/menu')
def menu():
    username = session.get('username')
    if not username:
        return redirect(url_for('home'))
    return render_template('menu.html', username=username)

@app.route('/recommend', methods=['GET', 'POST'])
def recommend():
    if request.method == 'POST':
        data = request.get_json()
        query = data.get('query', '').strip()
        
        # Use the GroceryStoreRecommender to get recommendations
        recommendations = recommender.recommendItems(query)

        return jsonify({"query": query, "recommendations": recommendations})

    return render_template('recommend.html')


@app.route('/cart')
def cart():
    username = session.get('username')
    if not username or username not in user_carts:
        flash("No shopping cart found.")
        return redirect(url_for('menu'))
    user_cart = user_carts[username]
    total = sum(price * quantity for item, price, quantity in user_cart.cart)
    return render_template('cart.html', cart=user_cart.cart, total=total, username=username)

@app.route('/checkout', methods=['POST'])
def checkout():
    username = session.get('username')
    receipt_filename = session.get('receipt').replace('purchases/', '')

    if not username or username not in user_carts:
        flash("No cart found to checkout.")
        return redirect(url_for('cart'))

    cart = user_carts[username]

    if not cart.cart:
        flash("Your cart is empty. Please add items before checking out.")
        return redirect(url_for('cart'))

    # Compute total before clearing the cart
    checked_out_cart = cart.cart.copy()
    total = sum(price * quantity for item, price, quantity in checked_out_cart)

    # Generate receipt content
    receipt_content = {
        "Items": checked_out_cart,
        "Total": total
    }

    # Call checkout function to save receipt file
    success = cart.checkout(receipt_filename)

    if success:
        flash("Checkout successful! Receipt has been saved.")
        user_carts.pop(username, None)  # Clear the cart after checkout
        return render_template('checkout.html', receipt=receipt_content)
    else:
        flash("Error generating receipt file. Try again.")
        return redirect(url_for('cart'))

@app.route('/shop')
def shop():
    username = session.get('username')
    if not username:
        return redirect(url_for('home'))
    if username not in user_carts:
        user_carts[username] = ShoppingCart()
    shop_instance = Shop(user_carts[username])
    return render_template('shop.html', categories=shop_instance.categories, username=username)

@app.route('/get_products', methods=['POST'])
def get_products():
    data = request.get_json()
    category_filename = data.get('category')
    if not category_filename:
        return jsonify({"message": "Category not provided!"}), 400

    shop_instance = Shop(user_carts[session['username']])
    products = shop_instance.display_products(category_filename)
    products_html = render_template('products.html', products=products)
    return products_html

@app.route('/get_purchases')
def get_purchases():
    admin = Admin()
    purchases = admin.get_purchases()
    return jsonify({'purchases': purchases})

@app.route('/dashboard')
def dashboard():
    if 'username' in session and session.get('logintype') == 'admin':
        return render_template('dashboard.html')
    else:
        return redirect(url_for('home'))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))

@app.route('/get_all_items')
def get_all_items():
    admin = Admin()
    items = admin.get_all_categories()
    return jsonify({'items': items})

@app.route('/get_all_categories')
def get_all_categories():
    admin = Admin()
    items = admin.get_all_categories()
    print(items)
    return jsonify({'items': items})

@app.route('/get_items/<category>')
def get_items(category):
    admin = Admin()
    items = admin.get_items_by_category(category)
    return jsonify({'items': items})

@app.route('/add_update_item', methods=['POST'])
def add_update_item():
    data = request.get_json()
    category = data.get('category')
    item = data.get('item')
    price = data.get('price')
    admin = Admin()
    result = admin.add_update_item(category, item, price)
    return jsonify({'message': result})

@app.route('/delete_item', methods=['POST'])
def delete_item():
    data = request.get_json()
    category = data.get('deleteCategory')
    item = data.get('deleteItem')
    admin = Admin()
    result = admin.delete_item(category, item)
    return jsonify({'message': result})

@app.route('/edit_item', methods=['POST'])
def edit_item():
    data = request.get_json()
    category = data.get('category')
    old_item = data.get('oldItem')
    new_item = data.get('newItem')
    price = data.get('price')
    admin = Admin()
    result = admin.edit_item(category, old_item, new_item, price)
    return jsonify({'message': result})

@app.route('/chatbot')
def chatbot():
    return render_template('chatbot.html', username=session.get('username', 'User'))

if __name__ == '__main__':
    app.run(debug=True)