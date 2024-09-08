from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from pymongo import MongoClient
import os
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Replace with your actual secret key

# Set up MongoDB connection
client = MongoClient('mongodb+srv://siddharthtomar003:oUIcyUk7xwraNjqp@cluster0.664o03z.mongodb.net/SIH', serverSelectionTimeoutMS=50000)
db = client['SIH']
users_collection = db['users']
collection = db['SIHcollection']

# Collection for issue tracking
db = client['issue_tracker']
issues_collection = db['issues']

@app.route('/home')
def home():
    # Fetch issues from MongoDB
    issues_list = list(issues_collection.find())
    
    # Render the home template with data
    return render_template('home.html', issues=issues_list)

@app.route('/logout')
def logout():
    session.pop('username', None)  # Remove the username from the session
    flash('You have been logged out')
    return redirect(url_for('login'))

@app.route('/', methods=['GET', 'POST'])
def login():
    if 'username' in session:
        return redirect(url_for('home'))

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        if not username or not password:
            flash('Username and password are required')
            return redirect(url_for('login'))

        user = users_collection.find_one({'username': username})

        if user and check_password_hash(user['password'], password):
            session['username'] = username
            return redirect(url_for('home'))
        else:
            flash('Invalid username or password')
            return redirect(url_for('login'))

    return render_template('login.html')


# Only admin has authority to create username and password
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        if not username or not password:
            flash('Username and password are required')
            return redirect(url_for('register'))

        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')

        if users_collection.find_one({'username': username}):
            flash('Username already exists')
            return redirect(url_for('register'))

        users_collection.insert_one({'username': username, 'password': hashed_password})
        flash('Registration successful')
        return redirect(url_for('login'))

    return render_template('register.html')

if __name__ == '__main__':
    app.run(debug=True)
