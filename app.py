#!/usr/bin/python3
from flask import Flask, render_template, jsonify, redirect, url_for, flash
from flask_login import LoginManager, login_user, logout_user, login_required, UserMixin
from forms import LoginForm, RegistrationForm
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import requests

app = Flask(__name__)
app.config['SECRET_KEY'] = 'gabson'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:gabriel@localhost/hbnb_dev_db'

quotes = []

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


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


def fetch_quote():
    response = requests.get('https://zenquotes.io/api/random')
    quote = response.json()[0]['q']
    quotes.append(quote)


@app.route('/')
@login_required
def home():
    if not quotes:
        fetch_quote()
    return render_template('index.html', quote=quotes[-1])


@app.route('/next')
def next_quote():
    fetch_quote()
    return jsonify({'quote': quotes[-1]})

@app.route('/prev')
def prev_quote():
    if len(quotes) > 1:
        quotes.pop()
    return jsonify({'quote': quotes[-1]})


if __name__ == '__main__':
    app.run(debug=True)
