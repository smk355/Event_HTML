# app.py
from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import re
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'c7cbecd5248e0a912ea1b218eaec6574b83aec62ff2126b1'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root2:abcd1234@localhost/eventease'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)

class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    date = db.Column(db.DateTime, nullable=False)
    location = db.Column(db.String(100), nullable=False)
    organizer = db.Column(db.String(100), nullable=False)

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            flash('Logged in successfully!', 'success')
            return redirect(url_for('events'))
        else:
            flash('Invalid username or password', 'error')
        
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        username = request.form['username']
        password = request.form['password']

        if not re.match(r'.*@(vitstudent\.ac\.in|vit\.ac\.in)$', email):
            flash('Invalid email domain. Please use a VIT email address.', 'error')
            return render_template('login.html')

        if User.query.filter((User.username == username) | (User.email == email)).first():
            flash('Username or email already exists', 'error')
            return render_template('login.html')

        hashed_password = generate_password_hash(password)
        new_user = User(name=name, email=email, username=username, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()

        flash('Account created successfully! Please log in.', 'success')
        return redirect(url_for('login'))

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('home'))

@app.route('/events')
def events():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    events = Event.query.order_by(Event.date).all()
    return render_template('events.html', events=events)

@app.route('/create_event', methods=['GET', 'POST'])
def create_event():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        date = datetime.strptime(request.form['date'], '%Y-%m-%d')
        location = request.form['location']
        organizer = request.form['organizer']
        
        new_event = Event(title=title, description=description, date=date, location=location, organizer=organizer)
        db.session.add(new_event)
        db.session.commit()
        
        flash('Event created successfully!', 'success')
        return redirect(url_for('events'))
    
    return render_template('create_event.html')

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)