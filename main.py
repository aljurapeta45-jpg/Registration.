from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'Apeta'

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:@localhost/license_registration'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# MODEL
class License(db.Model):
    __tablename__ = 'licenses'

    id = db.Column(db.Integer, primary_key=True)
    license_number = db.Column(db.String(50), unique=True, nullable=False)
    license_type = db.Column(db.String(50), nullable=False)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    birthday = db.Column(db.Date, nullable=False)
    email = db.Column(db.String(150), nullable=False)
    expiration_date = db.Column(db.Date, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# ROUTES
@app.route('/')
def home():
    return render_template('license_register.html')

@app.route('/register', methods=['POST'])
def register():
    license_number = request.form.get('license_number')
    license_type = request.form.get('license_type')
    first_name = request.form.get('first_name')
    last_name = request.form.get('last_name')
    email = request.form.get('email')

    birthday_str = request.form.get('birthday')
    expiration_str = request.form.get('expiration_date')

    try:
        birthday = datetime.strptime(birthday_str, '%Y-%m-%d').date()
        expiration_date = datetime.strptime(expiration_str, '%Y-%m-%d').date()
    except ValueError:
        flash('Invalid date format!', 'error')
        return redirect(url_for('home'))

    existing_license = License.query.filter_by(
        license_number=license_number
    ).first()

    if existing_license:
        flash('License number already exists!', 'error')
        return redirect(url_for('home'))

    new_license = License(
        license_number=license_number,
        license_type=license_type,
        first_name=first_name,
        last_name=last_name,
        birthday=birthday,
        email=email,
        expiration_date=expiration_date
    )

    try:
        db.session.add(new_license)
        db.session.commit()
        return redirect(url_for('success'))
    except:
        db.session.rollback()
        flash('Database error occurred!', 'error')
        return redirect(url_for('home'))

@app.route('/success')
def success():
    return render_template('success.html')

@app.route('/licenses')
def licenses():
    licenses = License.query.all()
    return render_template('licenses.html', licenses=licenses)

# RUN
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
