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

# Default route
@app.route('/')
def home():
    # Login interface
    return render_template('login.html')

# Login route
@app.route('/login', methods=['POST'])
def login():
    # Get the username and login type from the form
    username = request.form.get('username')
    logintype = request.form.get('login_type')
    
    # Check if the login type is admin
    if logintype == 'admin':
        # Hardcoded admin credentials
        admin_username = 'admin'
        admin_password = 'admin'
        password = request.form.get('password')
        
        # Check if the credentials are correct
        if username == admin_username and password == admin_password:
            session['username'] = username
            session['logintype'] = 'admin'
            # Redirect to the dashboard (Admin Page)
            return redirect(url_for('dashboard'))
        else:
            # Return an error message if the credentials are invalid
            return render_template('login.html', error="Invalid admin credentials.")
    # Check if the login type is user
    elif logintype == 'user':
        # Check if the username is alphanumeric
        if username and username.isalnum():
            # Set the username and login type in the session
            session['username'] = username
            session['logintype'] = 'user'
            # Generate a unique receipt filename
            date_str = datetime.datetime.now().strftime("%Y%m%d")
            increment = 1
            # Create a 'purchases' directory if it doesn't exist
            if not os.path.exists('purchases'):
                os.makedirs('purchases')
            # Find a unique filename for the receipt
            while True:
                receipt_filename = f"purchases/{username}.{date_str}.{increment}.receipt.txt"
                # If the filename doesn't exist, break the loop
                if not os.path.exists(receipt_filename):
                    # Write a header to the receipt file
                    with open(receipt_filename, 'w') as f:
                        f.write(f"Receipt for {username} on {date_str}\n")
                    session['receipt'] = receipt_filename
                    break
                increment += 1
            # Redirect to the menu page after successful login
            return redirect(url_for('menu'))
        else:
            # Return an error message if the username is invalid
            return render_template('login.html', error="Invalid username. Only letters and numbers allowed.")
    else:
        # Return an error message if the login type is invalid
        return render_template('login.html', error="Invalid login type.")

# Add to cart route for AJAX requests
@app.route('/add_to_cart', methods=['POST'])
def add_to_cart():
    # Get the item and quantity from the AJAX request
    data = request.get_json()
    item = data.get('item')
    quantity = data.get('quantity')
    # Check if the quantity is provided
    if quantity and quantity.strip():
        try:
            # Convert the quantity to an integer
            qty = int(quantity)
        except ValueError:
            flash("Invalid quantity provided.")
            return jsonify({"message": "Invalid quantity provided."}), 400
        
        # Get the username from the session
        username = session.get('username')
        # Check if the username exists
        if not username:
            flash("User not found. Please log in again.")
            return jsonify({"message": "User not found. Please log in again."}), 400
        # Get the user's shopping cart or create a new one
        cart = user_carts.get(username)
        # Create a new shopping cart if it doesn't exist
        if not cart:
            # Create a new shopping cart instance
            cart = ShoppingCart()
            # Add the shopping cart to the global dictionary
            user_carts[username] = cart
        
        # Add the item to the shopping cart
        item_name, item_price = item.split(', ')
        # Add the item to the cart
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
    # Get the username from the session
    username = session.get('username')
    if not username:
        # Redirect to the home page if the username is not found
        return redirect(url_for('home'))
    # Render the menu template
    return render_template('menu.html', username=username)

# Recommendation route
@app.route('/recommend', methods=['GET', 'POST'])
def recommend():
    # Check if the request is a POST request
    if request.method == 'POST':
        # Get the query from the form
        data = request.get_json()
        # Get the query from the form
        query = data.get('query', '').strip()
        
        # Use the GroceryStoreRecommender to get recommendations
        recommendations = recommender.recommendItems(query)

        # Return the recommendations as a JSON response
        return jsonify({"query": query, "recommendations": recommendations})
    # Render the recommendation template
    return render_template('recommend.html')

# Cart route
@app.route('/cart')
def cart():
    # Get the username from the session
    username = session.get('username')
    # Check if the username exists and the user has a shopping cart
    if not username or username not in user_carts:
        flash("No shopping cart found.")
        return redirect(url_for('menu'))
    # Get the user's shopping cart
    user_cart = user_carts[username]
    # Calculate the total price of the items in the cart
    total = sum(price * quantity for item, price, quantity in user_cart.cart)
    # Render the cart template
    return render_template('cart.html', cart=user_cart.cart, total=total, username=username)

# Checkout route
@app.route('/checkout', methods=['POST'])
def checkout():
    # Get the username from the session
    username = session.get('username')
    # Get the receipt filename from the session
    receipt_filename = session.get('receipt').replace('purchases/', '')
    # Check if the username exists and the user has a shopping cart
    if not username or username not in user_carts:
        flash("No cart found to checkout.")
        return redirect(url_for('cart'))
    # Get the user's shopping cart
    cart = user_carts[username]
    # Check if the cart is empty
    if not cart.cart:
        flash("Your cart is empty. Please add items before checking out.")
        return redirect(url_for('cart'))

    # Compute total before clearing the cart
    checked_out_cart = cart.cart.copy()
    # Calculate the total price of the items in the cart
    total = sum(price * quantity for item, price, quantity in checked_out_cart)

    # Generate receipt content
    receipt_content = {
        "Items": checked_out_cart,
        "Total": total
    }

    # Call checkout function to save receipt file
    success = cart.checkout(receipt_filename)

    # Check if the checkout was successful
    if success:
        flash("Checkout successful! Receipt has been saved.")
        user_carts.pop(username, None)  # Clear the cart after checkout
        return render_template('checkout.html', receipt=receipt_content, username=username)
    # If the checkout failed
    else:
        flash("Error generating receipt file. Try again.")
        return redirect(url_for('cart'))

# Logout route
@app.route('/shop')
def shop():
    # Get the username from the session
    username = session.get('username')
    if not username:
        return redirect(url_for('home'))
    # Get the user's shopping cart or create a new one
    if username not in user_carts:
        user_carts[username] = ShoppingCart()
    # Create a new Shop instance for the user
    shop_instance = Shop(user_carts[username])
    # Render the shop template
    return render_template('shop.html', categories=shop_instance.categories, username=username)

# Get products from category route for AJAX requests
@app.route('/get_products', methods=['POST'])
def get_products():
    # Get the category filename from the AJAX request
    data = request.get_json()
    # Check if the category filename is provided
    category_filename = data.get('category')
    if not category_filename:
        return jsonify({"message": "Category not provided!"}), 400
    # Create a new Shop instance for the user
    shop_instance = Shop(user_carts[session['username']])
    # Get the products from the category
    products = shop_instance.display_products(category_filename)
    # Return the products as a JSON response
    products_html = render_template('products.html', products=products)
    # Return the products HTML
    return products_html

# Add to cart route for AJAX requests
@app.route('/get_purchases')
def get_purchases():
    # Create an Admin instance
    admin = Admin()
    # Get the purchases
    purchases = admin.get_purchases()
    # Return the purchases as a JSON response
    return jsonify({'purchases': purchases})

# Admin dashboard route
@app.route('/dashboard')
def dashboard():
    # Check if the user is logged in as an admin
    if 'username' in session and session.get('logintype') == 'admin':
        # Render the dashboard template
        return render_template('dashboard.html')
    # Redirect to the home page if the user is not an admin
    else:
        return redirect(url_for('home'))

# Logout route
@app.route('/logout')
def logout():
    # Clear the session
    session.clear()
    # Redirect to the home page
    return redirect(url_for('home'))

# API routes for admin operations
@app.route('/get_all_items')
def get_all_items():
    # Create an Admin instance
    admin = Admin()
    # Get all items
    items = admin.get_all_categories()
    # Return the items as a JSON response
    return jsonify({'items': items})

# API route to get all categories
@app.route('/get_all_categories')
def get_all_categories():
    # Create an Admin instance
    admin = Admin()
    # Get all categories
    items = admin.get_all_categories()
    print(items)
    # Return the categories as a JSON response
    return jsonify({'items': items})

# API route to get items by category
@app.route('/get_items/<category>')
def get_items(category):
    # Create an Admin instance
    admin = Admin()
    # Get items by category
    items = admin.get_items_by_category(category)
    # Return the items as a JSON response
    return jsonify({'items': items})

# API route to add or update an item
@app.route('/add_update_item', methods=['POST'])
def add_update_item():
    # Get the data from the AJAX request
    data = request.get_json()
    # Get the category, item, and price from the data
    category = data.get('category')
    item = data.get('item')
    price = data.get('price')
    # Create an Admin instance
    admin = Admin()
    # Add or update the item
    result = admin.add_update_item(category, item, price)
    # Return the result as a JSON response
    return jsonify({'message': result})

# API route to delete an item
@app.route('/delete_item', methods=['POST'])
def delete_item():
    # Get the data from the AJAX request
    data = request.get_json()
    # Get the category and item from the data
    category = data.get('deleteCategory')
    item = data.get('deleteItem')
    # Create an Admin instance
    admin = Admin()
    # Delete the item
    result = admin.delete_item(category, item)
    # Return the result as a JSON response
    return jsonify({'message': result})

# API route to edit an item
@app.route('/edit_item', methods=['POST'])
def edit_item():
    # Get the data from the AJAX request
    data = request.get_json()
    # Get the category, old item, new item, and price from the data
    category = data.get('category')
    old_item = data.get('oldItem')
    new_item = data.get('newItem')
    price = data.get('price')
    # Create an Admin instance
    admin = Admin()
    # Edit the item
    result = admin.edit_item(category, old_item, new_item, price)
    # Return the result as a JSON response
    return jsonify({'message': result})

# API route to get purchases
@app.route('/chatbot')
def chatbot():
    # Render the chatbot template
    return render_template('chatbot.html', username=session.get('username', 'User'))

# Main
if __name__ == '__main__':
    app.run(debug=True)