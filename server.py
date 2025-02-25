from flask import Flask, render_template, jsonify, request, redirect, url_for, session
import os

app = Flask(__name__)
app.secret_key = 'your-secret-key'  # Change this to a secure secret key

@app.route('/')
def index():
    return render_template('login.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Get form data
        login_type = request.form.get('login_type')
        username = request.form.get('username')
        password = request.form.get('password')
        
        # Python equivalent of the JavaScript login check
        if login_type == 'admin' and username == 'admin' and password == 'admin':
            session['logged_in'] = True
            session['user_type'] = 'admin'
            return redirect(url_for('dashboard'))
        else:
            return render_template('login.html', error='Invalid credentials')
    
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if session.get('logged_in') and session.get('user_type') == 'admin':
        return render_template('dashboard.html')
    return redirect(url_for('index'))

@app.route('/admin')
def admin():
    return render_template('admin.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

@app.route('/get_purchases')
def get_purchases():
    if not session.get('logged_in') or session.get('user_type') != 'admin':
        return jsonify({'error': 'Unauthorized'}), 401
    purchases = []
    purchase_dir = 'purchases'
    if os.path.exists(purchase_dir):
        for file in os.listdir(purchase_dir):
            if file.endswith('.receipt.txt'):
                with open(os.path.join(purchase_dir, file), 'r') as f:
                    purchases.append({
                        'filename': file,
                        'content': f.read()
                    })
    return jsonify({'purchases': purchases})

@app.route('/get_items/<category>')
def get_items(category):
    if not session.get('logged_in') or session.get('user_type') != 'admin':
        return jsonify({'error': 'Unauthorized'}), 401
    items = []
    items_dir = 'items'
    if os.path.exists(items_dir):
        if category == 'all':
            files = [f for f in os.listdir(items_dir) if f.endswith('.txt')]
        else:
            files = [f for f in os.listdir(items_dir) if f.endswith('.txt') and category in f]
            
        for file in files:
            with open(os.path.join(items_dir, file), 'r') as f:
                items.extend(f.read().splitlines())
    return jsonify({'items': items})

if __name__ == '__main__':
    app.debug = True
    app.run(port=5000) 