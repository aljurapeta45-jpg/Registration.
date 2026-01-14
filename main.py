import os
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug.security import generate_password_hash

app = Flask(__name__)
app.secret_key = 'Apeta'

# =======================
# DATABASE CONFIG (RAILWAY)
# =======================
app.config['SQLALCHEMY_DATABASE_URI'] = (
    f"mysql+pymysql://{os.environ['MYSQLUSER']}:"
    f"{os.environ['MYSQLPASSWORD']}@"
    f"{os.environ['MYSQLHOST']}:"
    f"{os.environ['MYSQLPORT']}/"
    f"{os.environ['MYSQLDATABASE']}"
)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# =======================
# MODELS
# =======================

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    birthday = db.Column(db.Date, nullable=False)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class License(db.Model):
    __tablename__ = 'licenses'

    id = db.Column(db.Integer, primary_key=True)
    license_number = db.Column(db.String(100), unique=True, nullable=False)
    license_type = db.Column(db.String(50), nullable=False)
    issue_date = db.Column(db.Date, nullable=False)
    expiry_date = db.Column(db.Date, nullable=False)

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    user = db.relationship('User', backref=db.backref('licenses', lazy=True))

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# =======================
# ROUTES
# =======================

@app.route('/')
def home():
    return render_template('register.html')

# -------- USER REGISTRATION --------
@app.route('/register', methods=['POST'])
def register():
    birthday_str = request.form.get('birthday')
    first_name = request.form.get('first_name')
    last_name = request.form.get('last_name')
    email = request.form.get('email')
    password = request.form.get('password')
    confirm_password = request.form.get('confirm_password')

    if password != confirm_password:
        flash('Passwords do not match!', 'error')
        return redirect(url_for('home'))

    try:
        birthday = datetime.strptime(birthday_str, '%Y-%m-%d').date()
    except ValueError:
        flash('Invalid birthday format!', 'error')
        return redirect(url_for('home'))

    if User.query.filter_by(email=email).first():
        flash('Email already exists!', 'error')
        return redirect(url_for('home'))

    hashed_password = generate_password_hash(password)

    new_user = User(
        birthday=birthday,
        first_name=first_name,
        last_name=last_name,
        email=email,
        password=hashed_password
    )

    try:
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('license_register'))
    except:
        db.session.rollback()
        flash('Database error occurred!', 'error')
        return redirect(url_for('home'))

# -------- LICENSE REGISTRATION --------
@app.route('/license/register', methods=['GET', 'POST'])
def license_register():
    if request.method == 'GET':
        users = User.query.all()
        return render_template('license_register.html', users=users)

    user_id = request.form.get('user_id')
    license_number = request.form.get('license_number')
    license_type = request.form.get('license_type')
    issue_date_str = request.form.get('issue_date')
    expiry_date_str = request.form.get('expiry_date')

    try:
        issue_date = datetime.strptime(issue_date_str, '%Y-%m-%d').date()
        expiry_date = datetime.strptime(expiry_date_str, '%Y-%m-%d').date()
    except ValueError:
        flash('Invalid date format!', 'error')
        return redirect(url_for('license_register'))

    if License.query.filter_by(license_number=license_number).first():
        flash('License number already exists!', 'error')
        return redirect(url_for('license_register'))

    new_license = License(
        license_number=license_number,
        license_type=license_type,
        issue_date=issue_date,
        expiry_date=expiry_date,
        user_id=user_id
    )

    try:
        db.session.add(new_license)
        db.session.commit()
        return redirect(url_for('success'))
    except:
        db.session.rollback()
        flash('Database error occurred!', 'error')
        return redirect(url_for('license_register'))

# -------- VIEW USERS --------
@app.route('/users')
def users():
    users = User.query.all()
    return render_template('users.html', users=users)

# -------- VIEW LICENSES --------
@app.route('/licenses')
def licenses():
    licenses = License.query.all()
    return render_template('licenses.html', licenses=licenses)

@app.route('/success')
def succes
