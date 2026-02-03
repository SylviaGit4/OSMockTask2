from flask import Flask, url_for, render_template, redirect 
from flask_login import LoginManager, login_required, login_user # For ensuring user login protection
from flask_cors import CORS # Added to allow other files to call the app
from flask_wtf import FlaskForm # For creating forms
from wtforms import StringField, SubmitField, PasswordField # For creating forms
from wtforms.validators import DataRequired # For creating forms
from pathlib import Path # For handling file paths
from flask_bootstrap import Bootstrap5 # Bootstrap CSS integration
from forms import LoginForm, RegistrationForm
from flask_sqlalchemy import SQLAlchemy # For database handling

base_dir = Path.cwd()
data_dir = (base_dir / "backend" / "data" / "data.sqlite")
template_dir = str(base_dir / "frontend" / "templates")

app = Flask(__name__, template_folder=template_dir)

CORS(app)

bootstrap = Bootstrap5(app)

app.config['SECRET_KEY'] = 'key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + str(data_dir)

login_handler = LoginManager()
login_handler.login_view = '/login'
login_handler.init_app(app)

@login_handler.user_loader
def load_user(user_id):
    return Users.query.get(int(user_id))

db = SQLAlchemy(app)

class Users(db.Model):
    __tablename__ = 'Users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64))
    email = db.Column(db.String(64), unique=True) 
    password = db.Column(db.String(64))
    is_admin = db.Column(db.Boolean, default=False)
    loyalty_points = db.Column(db.Integer, default=0)
    is_premium = db.Column(db.Boolean, default=False)

    # Flask-Login required properties/methods
    @property
    def is_authenticated(self):
        return True

    @property
    def is_active(self):
        return True

    @property
    def is_anonymous(self):
        return False

    def get_id(self):
        return str(self.id)

class Zoo_Booking(db.Model):
    __tablename__ = 'Zoo_Booking'
    visit_id = db.Column(db.Integer, primary_key=True)
    start_date = db.Column(db.String(64))
    end_date = db.Column(db.String(64))
    child_tickets = db.Column(db.Integer)
    adult_tickets = db.Column(db.Integer())
    educational_visit = db.Column(db.Boolean, default=False)
    user_id = db.Column(db.Integer, db.ForeignKey('Users.id'))

class Hotel_Booking(db.Model):
    __tablename__ = 'Hotel_Booking'
    hotel_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('Users.id'))
    start_date = db.Column(db.String(64))
    end_date = db.Column(db.String(64))
    room_id = db.Column(db.Integer, db.ForeignKey('Room.room_id'))

class Room(db.Model):
    __tablename__ = 'Room'
    room_id = db.Column(db.Integer, primary_key=True)
    room_type = db.Column(db.String(64))
    latest_checkin = db.Column(db.String(64))
    room_price = db.Column(db.Float)

with app.app_context():
    db.create_all()


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods = ['GET', 'POST'])
def login():
    form = LoginForm()
    loginError = None
    
    if form.validate_on_submit():   
        user = Users.query.filter_by(email=form.email.data).first() 
        password = form.password.data
        
        if user and user.password == password:
            load_user(user.id)
            login_user(user)
            return redirect(url_for('dashboard'))      
        else:
            loginError = "Invalid email or password."

    return render_template('login.html', form=form, loginError=loginError)

@app.route('/register', methods = ['GET', 'POST'])
def register():
    form = RegistrationForm()
    registerError = None

    existing_user = Users.query.filter_by(email=form.email.data).first()
    if form.validate_on_submit() and not existing_user:
        user = Users(username=form.username.data, email=form.email.data, password=form.password.data)
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('login'))
    
    elif form.validate_on_submit():
        registerError = "Email already registered."

    return render_template('register.html', form=form, registerError=registerError)

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html')

@app.route('/booking')
@login_required
def booking():
    return render_template('booking.html')

if __name__ == '__main__':
    app.run(debug=True)