from flask import Flask, render_template, request, redirect, session , url_for
import firebase_admin
import logging
from firebase_admin import credentials, db
import requests

app = Flask(__name__)
app.secret_key = 'your_secure_key'  # Use a more secure key in production

# Initialize Firebase Admin SDK
cred = credentials.Certificate('opmdb-firebase-firebase-adminsdk-bpw2q-1f67990e42.json')
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://opmdb-firebase-default-rtdb.asia-southeast1.firebasedatabase.app'
})

def generate_quote():
    response = requests.get("https://zenquotes.io/api/random")
    if response.status_code == 200:    
        data = response.json()
        quote = data[0]['q']
        author = data[0]['a']
        return f'{quote} - {author}'
    else:
        return 'Failed to fetch a quote'
    
@app.errorhandler(401)
def invalid_credentials(e):
    return render_template('401.html'), 401
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404
@app.errorhandler(405)
def method_not_allowed(e):
    return render_template('405.html'), 405

#Register route
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        name = request.form['name']
        nim = request.form['nim']
        role = 'customer'
        img_url = request.form.get('img_url', 'https://raw.githubusercontent.com/wardota/OnePunchman/refs/heads/main/frontend/img/opm-logo.png')  
        if img_url =="":
            img_url='https://raw.githubusercontent.com/wardota/OnePunchman/refs/heads/main/frontend/img/opm-logo.png'
        ref = db.reference(f'users/{username}')
        if ref.get() is not None:
            return 'Username already exists, please choose another one', 409
        user_data = {
            'img_url': img_url,
            'name': name,
            'nim': nim,
            'password': password,
            'role': role
        }
        ref.set(user_data)
        return redirect('/')
    return render_template('register.html')

# Login route
@app.route('/', methods=['GET', 'POST'])
def login():
    if 'username' in session:
        if session['role'] == 'admin':
            return redirect('/admin_dashboard')
        elif session['role'] == 'customer':
            return redirect('/customer_dashboard')
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        ref = db.reference(f'users/{username}')
        user = ref.get()
        logging.info(f'User data for {username}: {user}')

        if user and user['password'] == password:
            session['username'] = username
            session['role'] = user['role']
            session['name'] = user['name']
            session['nim'] = user['nim']
            session['img_url'] = user['img_url']
            session['qotd'] = generate_quote()
            session['git_url'] = f'https://github.com/{username}'
            
            # Redirect based on role
            if user['role'] == 'admin':
                return redirect('/home')
            elif user['role'] == 'customer':
                return redirect('/home')
            else:
                return redirect('/')
        else:
            return invalid_credentials(401)

    return render_template('index.html')

# Customer dashboard
@app.route('/customer_dashboard')
def customer_dashboard():
    if 'username' in session and session['role'] == 'customer':
        return render_template('customer_dashboard.html', username=session['username'], name=session['name'],img_url=session['img_url'],nim=session['nim'],qotd=session['qotd'],git_url=session['git_url'])
    return redirect('/login')

# Admin dashboard
@app.route('/admin_dashboard')
def admin_dashboard():
    if 'username' in session and session['role'] == 'admin':
        return render_template('admin_dashboard.html',username=session['username'], name=session['name'],img_url=session['img_url'],nim=session['nim'],qotd=session['qotd'],git_url=session['git_url'])
    return redirect('/login')
@app.route('/')
def index():
    loginText='Login'
    if 'username' in session:
        loginText=session['username'] 

    return render_template('index.html',loginText=loginText)
@app.route('/home')
def home():
    loginText='Login'
    if 'username' in session:
        if session['role'] == 'admin':
            return render_template('home.html',to_dashboard='/admin_dashboard',qotd=session['qotd'])
        elif session['role'] == 'customer':
            return render_template('home.html',to_dashboard='/customer_dashboard',qotd=session['qotd'])
# Logout route
@app.route('/logout')
def logout():
    session.pop('username', None)
    session.pop('role', None)
    return redirect('/')

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080, debug=True)
