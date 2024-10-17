from flask import Flask, render_template, request, redirect, session
import firebase_admin
from firebase_admin import credentials, db

app = Flask(__name__)
app.secret_key = 'secret_key'  # Change this to a more secure key.

# Initialize Firebase Admin SDK
cred = credentials.Certificate('firebase-adminsdk.json')
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://opmdb-firebase-default-rtdb.asia-southeast1.firebasedatabase.app'
})

# Login route
@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        ref = db.reference(f'users/{username}')
        user = ref.get()

        if user and user['password'] == password:
            session['username'] = username
            session['role'] = user['role']

            if user['role'] == 'admin':
                return redirect('/admin_dashboard')
            else:
                return redirect('/customer_dashboard')
        else:
            return 'Invalid credentials', 401

    return render_template('index.html')

# Customer dashboard
@app.route('/customer_dashboard')
def customer_dashboard():
    if 'username' in session and session['role'] == 'customer':
        return render_template('customer_dashboard.html', username=session['username'])
    return redirect('/')

# Admin dashboard
@app.route('/admin_dashboard')
def admin_dashboard():
    if 'username' in session and session['role'] == 'admin':
        return render_template('admin_dashboard.html', username=session['username'])
    return redirect('/')

# Logout route
@app.route('/logout')
def logout():
    session.pop('username', None)
    session.pop('role', None)
    return redirect('/')

if __name__ == "__main__":
    # Get the port from the environment variable, defaulting to 8080
    #port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=8080)