#!/usr/bin/python3
from flask import Flask, render_template, jsonify, redirect, url_for, flash, request, abort
from flask_login import LoginManager, login_user, logout_user, login_required, current_user, UserMixin
from forms import LoginForm, RegistrationForm, ForgotPasswordForm, ResetPasswordForm
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import Session
from werkzeug.security import generate_password_hash, check_password_hash
from pyfcm import FCMNotification
from flask_mail import Mail, Message
from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadSignature
from dotenv import load_dotenv
from functools import wraps
import requests
import psycopg2
import json
import os

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://hbnb_dev:ezzicZloooY65xKOArE6e03bfoXT4n77@dpg-cpctfplds78s738t12j0-a.oregon-postgres.render.com/hbnb_dev_db'
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
app.config['UPLOAD_FOLDER'] = 'static/uploads'
push_service = FCMNotification(api_key="your_firebase_server_key")

REVIEWS_FILE = 'reviews.json'
quotes = []

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
mail = Mail(app)
s = URLSafeTimedSerializer(app.config['SECRET_KEY'])


@app.template_filter('to_int')
def to_int(value):
    return int(value)

app.jinja_env.filters['to_int'] = to_int


#def admin_required(f):
#    @wraps(f)
 #   def decorated_function(*args, **kwargs):
  #      if not current_user.is_admin:
   #         abort(403)
    #    return f(*args, **kwargs)
   # return decorated_function


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(150), nullable=False)
    #is_admin = db.Column(db.Boolean, default=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def get_id(self):
        return self.id
    

#@app.before_first_request
#def create_default_admin():
 #   admin_email = os.getenv('ADMIN_EMAIL', 'admin@example.com')
  #  admin_password = os.getenv('ADMIN_PASSWORD', 'password')
   # admin_user = User.query.filter_by(email=admin_email).first()
   # if not admin_user:
    #    new_admin = User(email=admin_email, is_admin=True)
     #   new_admin.set_password(admin_password)
     #   db.session.add(new_admin)
      #  db.session.commit()
       # print('Default admin user created')


#@app.route('/admin')
#@login_required
#@admin_required
#def admin_dashboard():
 #   return render_template('admin_dashboard.html')


#@app.route('/admin_login', methods=['GET', 'POST'])
#def admin_login():
#    form = LoginForm()
#    if form.validate_on_submit():
#        email = form.email.data
#        password = form.password.data
#        user = User.query.filter_by(email=email, is_admin=True).first()
#        if user and user.check_password(password):
#            login_user(user)
#            flash('Logged in as admin successfully.', 'success')
#            return redirect(url_for('admin_dashboard'))
#        else:
#            flash('Invalid admin credentials.', 'error')
#    return render_template('admin_login.html', form=form)


@login_manager.user_loader
def load_user(user_id):
    session = Session(bind=db.engine)
    user = session.get(User, int(user_id))
    session.close()
    return user


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
        #is_admin = form.is_admin.data if current_user.is_admin else False
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


@app.route('/profile')
@login_required
def profile():
    user = User.query.get(current_user.id)
    return render_template('profile.html', user=user)


@app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    user = User.query.get(current_user.id)
    if request.method == 'POST':
        user.email = request.form.get('email')
        db.session.commit()
        flash('Profile updated successfully.', 'success')
        return redirect(url_for('profile'))
    return render_template('edit_profile.html', user=user)


@app.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    form = ForgotPasswordForm()
    if form.validate_on_submit():
        email = form.email.data
        user = User.query.filter_by(email=email).first()
        if user:
            token = s.dumps(email, salt='password-reset-salt')
            link = url_for('reset_password', token=token, _external=True)
            msg = Message('Password Reset Request',
                            sender=app.config['MAIL_USERNAME'],
                            recipients=[email])
            msg.body = f'Your link to reset your password is {link}. This link will expire in 1 hour.'
            mail.send(msg)
            flash('A password reset link has been sent to your email.', 'info')
        else:
            flash('No account found with that email.', 'warning')
        return redirect(url_for('forgot_password'))
    return render_template('forgot_password.html', form=form)


@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    try:
        email = s.loads(token, salt='password-reset-salt', max_age=3600)
    except SignatureExpired:
        flash('The token has expired. Please try again.', 'warning')
        return redirect(url_for('forgot_password'))
    except BadSignature:
        flash('Invalid token. Please try again.', 'danger')
        return redirect(url_for('forgot_password'))

    form = ResetPasswordForm()
    if form.validate_on_submit():
        password = form.password.data
        user = User.query.filter_by(email=email).first()
        if user:
            user.set_password(password)
            db.session.commit()
            flash('Your password has been updated!', 'success')
            return redirect(url_for('login'))
    return render_template('reset_password.html')


def fetch_quote():
    try:
        response = requests.get('https://zenquotes.io/api/random')
        quote = response.json()[0]['q']
        quotes.append(quote)
    except requests.exceptions.RequestException as e:
        print('Error fetching quote:', e)
        return None


@app.route('/inspiration')
def inspiration():
    response = requests.get('https://zenquotes.io/api/quotes/inspiration')
    quote = response.json()[0]['q']
    quotes.append(quote)
    return render_template('inspiration.html', quote=quotes[-1])


@app.route('/motivation')
def motivation():
    response = requests.get('https://zenquotes.io/api/quotes/motivation')
    quote = response.json()[0]['q']
    quotes.append(quote)
    return render_template('motivation.html', quote=quotes[-1])


@app.route('/emotional')
def emotional():
    response = requests.get('https://zenquotes.io/api/quotes/emotional')
    quote = response.json()[0]['q']
    quotes.append(quote)
    return render_template('emotional.html', quote=quotes[-1])


@app.route('/happiness')
def happiness():
    response = requests.get('https://zenquotes.io/api/quotes/happiness')
    quote = response.json()[0]['q']
    quotes.append(quote)
    return render_template('happiness.html', quote=quotes[-1])


@app.route('/moody')
def moody():
    response = requests.get('https://zenquotes.io/api/quotes/moody')
    quote = response.json()[0]['q']
    quotes.append(quote)
    return render_template('moody.html', quote=quotes[-1])


@app.route('/strength')
def strength():
    response = requests.get('https://zenquotes.io/api/quotes/strength')
    quote = response.json()[0]['q']
    quotes.append(quote)
    return render_template('strength.html', quote=quotes[-1])


@app.route('/sad')
def sad():
    response = requests.get('https://zenquotes.io/api/quotes/sad')
    quote = response.json()[0]['q']
    quotes.append(quote)
    return render_template('sad.html', quote=quotes[-1])


@app.route('/float')
def float():
    response = requests.get('https://zenquotes.io/api/quotes/float')
    quote = response.json()[0]['q']
    quotes.append(quote)
    return render_template('float.html', quote=quotes[-1])


@app.route('/spiritual')
def spiritual():
    response = requests.get('https://zenquotes.io/api/quotes/spiritual')
    quote = response.json()[0]['q']
    quotes.append(quote)
    return render_template('spiritual.html', quote=quotes[-1])


@app.route('/energetic')
def energetic():
    response = requests.get('https://zenquotes.io/api/quotes/energetic')
    quote = response.json()[0]['q']
    quotes.append(quote)
    return render_template('energetic.html', quote=quotes[-1])


@app.route('/')
def dashboard():
    return render_template('dashboard.html')


@app.route('/home')
@login_required
def home():    
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


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/review')
def review():
    reviews = load_reviews()
    return render_template('review.html', reviews=reviews)


@app.route('/features')
def features():
    return render_template('features.html')


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


def load_reviews():
    try:
        with open(REVIEWS_FILE, 'r') as f:
            reviews = json.load(f)
        return reviews
    except FileNotFoundError:
        return []
    except json.JSONDecodeError:
        return []


def save_reviews(reviews):
    with open(REVIEWS_FILE, 'w') as file:
        json.dump(reviews, file, indent=4)
    print("Saved reviews:", reviews)


@app.route('/submit_review', methods=['POST'])
def submit_review():
    avatar_filename = ''
    if 'avatar' in request.files:
        avatar = request.files['avatar']
        if avatar.filename != '':
            avatar_filename = avatar.filename
            avatar.save(os.path.join(app.config['UPLOAD_FOLDER'], avatar_filename))

    review = {
        'name': request.form.get('name'),
        'job': request.form.get('job'),
        'avatar': avatar_filename,
        'rating': float(request.form.get('rating')),
        'review': request.form.get('review')
    }
    
    reviews = load_reviews()
    reviews.append(review)
    save_reviews(reviews)
    
    return jsonify({'success': True})


if __name__ == '__main__':
    app.run(debug=True)
