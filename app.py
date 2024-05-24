#!/usr/bin/python3
from flask import Flask, render_template, jsonify, redirect, url_for, flash, request
from flask_login import LoginManager, login_user, logout_user, login_required, UserMixin
from forms import LoginForm, RegistrationForm
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from pyfcm import FCMNotification
from flask_mail import Mail, Message
from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadSignature
import requests
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'gabson'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://hbnb_dev:hbnb_dev_pwd@localhost/hbnb_dev_db'
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'gabrielakinshola021@gmail.com'
app.config['MAIL_PASSWORD'] = 'yourpassword'
push_service = FCMNotification(api_key="your_firebase_server_key")

quotes = []

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
mail = Mail(app)
s = URLSafeTimedSerializer(app.config['SECRET_KEY'])


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(150), nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def get_id(self):
        return self.id


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data
        remember = form.remember_me.data
        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password):
            login_user(user, remember=remember)
            flash('Logged in successfully.', 'success')
            return redirect(url_for('home'))
        else:
            flash('Invalid email or password.', 'error')
    return render_template('login.html', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logged out successfully.', 'success')
    return redirect(url_for('login'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash('Email already registered. Please login.', 'error')
            return redirect(url_for('login'))
        else:
            new_user = User(email=email)
            new_user.set_password(password)
            db.session.add(new_user)
            db.session.commit()
            flash('Registration successful. You can now login.', 'success')
            return redirect(url_for('login'))
    return render_template('register.html', form=form)


@app.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form.get('email')
        user = User.query.filter_by(email=email).first()
        if user:
            token = s.dumps(email, salt='password-reset-salt')
            link = url_for('reset_password', token=token, _external=True)
            msg = Message('Password Reset Request', sender='noreply@demo.com', recipients=[email])
            msg.body = f'Your link to reset your password is {link}. This link will expire in 1 hour.'
            mail.send(msg)
            flash('A password reset link has been sent to your email.', 'info')
        else:
            flash('No account found with that email.', 'warning')
        return redirect(url_for('forgot_password'))
    return render_template('forgot_password.html')


@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    try:
        email = s.loads(token, salt='password-reset-salt', max_age=3600)
    except SignatureExpired:
        return '<h1>The token is expired!</h1>'
    except BadSignature:
        return '<h1>Invalid token!</h1>'

    if request.method == 'POST':
        password = request.form.get('password')
        user = User.query.filter_by(email=email).first()
        if user:
            user.set_password(password)
            db.session.commit()
            flash('Your password has been updated!', 'success')
            return redirect(url_for('login'))

    return render_template('reset_password.html')


def fetch_quote():
    response = requests.get('https://zenquotes.io/api/random')
    quote = response.json()[0]['q']
    quotes.append(quote)


@app.route('/')
def dashboard():
    return render_template('dashboard.html')


@app.route('/home')
@login_required
def home():
    if not quotes:
        fetch_quote()
    return render_template('index.html', quote=quotes[-1])


@app.route('/next')
def next_quote():
    fetch_quote()
    return jsonify({'quote': quotes[+1]})

@app.route('/prev')
def prev_quote():
    if len(quotes) > 1:
        quotes.pop()
    return jsonify({'quote': quotes[-1]})


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/review')
def review():
    return render_template('review.html')


@app.route('/send-notification', methods=['POST'])
def send_push_notification():
    data = request.get_json()
    registration_id = data.get('email')
    title = data.get('title')
    body = data.get('body')

    if not registration_id or not title or not body:
        return jsonify({"error": "Missing data"}), 400

    message = {
            "registration_ids": [registration_id],
            "notification": {
                "title": title,
                "body": body
            }
    }
    result = push_service.notify_single_device(**message)
    print(result)
    return jsonify({"message": "Notification sent successfully"}), 200


if __name__ == '__main__':
    app.run(debug=True)
