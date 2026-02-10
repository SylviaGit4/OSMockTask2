from flask import Flask, url_for, render_template, redirect, request, flash
from flask_login import LoginManager, login_required, login_user, current_user # For ensuring user login protection
from flask_cors import CORS # Added to allow other files to call the app
from pathlib import Path # For handling file paths
from flask_bootstrap import Bootstrap5 # Bootstrap CSS integration
from forms import LoginForm, RegistrationForm, BookingForm, RoomCreate # Importing forms from forms.py
from flask_sqlalchemy import SQLAlchemy # For database handling
from sqlalchemy.orm import DeclarativeBase
from datetime import date # For handling dates in hotel booking

base_dir = Path.cwd()
data_dir = (base_dir / "backend" / "data" / "data.sqlite")
template_dir = str(base_dir / "frontend" / "templates")
static_dir = str(base_dir / "frontend" / "static")

app = Flask(__name__, template_folder=template_dir, static_folder=static_dir)

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

class Base(DeclarativeBase):
  pass

db = SQLAlchemy(app, model_class=Base)

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

class Hotel_Booking(db.Model):
    __tablename__ = 'Hotel_Booking'
    hotel_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('Users.id'))
    start_date = db.Column(db.String(64))
    end_date = db.Column(db.String(64))
    room_id = db.Column(db.Integer, db.ForeignKey('Room.room_id'))

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

class Room(db.Model):
    __tablename__ = 'Room'
    room_id = db.Column(db.Integer, primary_key=True, index=True, autoincrement=True)
    room_type = db.Column(db.String(64), nullable=False)
    latest_checkin = db.Column(db.String(64))
    room_price = db.Column(db.Float, nullable=False)

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

@app.route('/admin', methods = ['GET', 'POST'])
@login_required
def admin():
    form = RoomCreate()

    if form.validate_on_submit():
        new_room = Room(
            room_type=form.room_type.data,
            room_price=form.room_price.data,
            latest_checkin=date(2000, 1, 1) # Set to a default date far in the past to indicate room is available
        )
        db.session.add(new_room)
        db.session.commit()
        flash('Room created successfully!', 'success')

    # Only allow admin users to access the admin page, otherwise redirect to dashboard.
    if Users.query.get(current_user.id).is_admin:
        return render_template('admin.html', form=form)
    else:
        return redirect(url_for('dashboard'))

@app.route('/booking', methods = ['GET', 'POST'])
@login_required
def booking():
    form = BookingForm()
 
    if form.validate_on_submit():

        # Check if at least one ticket is selected
        if form.child_tickets.data < 1 and form.adult_tickets.data < 1:
            flash('Please select at least one ticket (child or adult).', 'danger')
            return render_template('booking.html', form=form)
        
        # Check if dates are chronological
        if form.start_date_zoo.data > form.end_date_zoo.data:
            flash('End date must be after start date.', 'danger')
            return render_template('booking.html', form=form)

        new_zoo_booking = Zoo_Booking(
            start_date=form.start_date_zoo.data, # Start date of visit
            end_date=form.end_date_zoo.data, # End date of visit
            user_id=current_user.id,  # Links booking to logged-in user
            child_tickets=form.child_tickets.data, # Links number of child tickets
            adult_tickets=form.adult_tickets.data, # Links number of adult tickets
            educational_visit=form.educational_visit.data # Links to check if visit is educational
        )

        if form.start_date_hotel.data > form.end_date_hotel.data:
            flash('Hotel end date must be after start date.', 'danger')
            return render_template('booking.html', form=form)

        rooms = Room.query.filter_by(room_type=form.room_type.data).all() # Check if room type is available
        if not rooms:
            flash('Selected room type is not available.', 'danger')
            return render_template('booking.html', form=form)

        for room in rooms:
            if room.latest_checkin < form.start_date_hotel.data: # Check if room is available for selected dates
                selected_room=room.room_id
                break
        
        if not selected_room:
            flash('No rooms available for selected dates.', 'danger')
            return render_template('booking.html', form=form)

        new_hotel_booking = Hotel_Booking(
            start_date=form.start_date_hotel.data, # Start date of hotel stay
            end_date=form.end_date_hotel.data, # End date of hotel stay
            user_id=current_user.id,  # Links booking to logged-in user
            room_id=selected_room # Links to selected room for hotel booking
        )

        # Updates the latest check-in date for the selected room to ensure it is not double-booked for overlapping dates in the future
        room_update = Room.query.filter_by(room_id=selected_room).first()
        if room_update:
            room_update.latest_checkin=form.end_date_hotel.data

        db.session.add(new_hotel_booking)
        db.session.add(new_zoo_booking)
        db.session.commit()

        return redirect(url_for('dashboard'))
    
    return render_template('booking.html', form=form)

if __name__ == '__main__':
    app.run(debug=True)