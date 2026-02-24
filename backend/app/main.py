from flask import Flask, url_for, render_template, redirect, request, flash
from flask_login import LoginManager, login_required, login_user, current_user # For ensuring user login protection
from flask_cors import CORS # Added to allow other files to call the app
from pathlib import Path # For handling file paths
from flask_bootstrap import Bootstrap5 # Bootstrap CSS integration
from forms import LoginForm, RegistrationForm, BookingForm, RoomCreate # Importing forms from forms.py
from flask_sqlalchemy import SQLAlchemy # For database handling
from sqlalchemy.orm import DeclarativeBase
from datetime import date, datetime # For handling dates in hotel booking
from payment_calculation import calculate_cost # For calculating the cost of the booking based on user selections

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
            latest_checkin=date(2000, 1, 1) # Set to a default date
        )
        db.session.add(new_room)
        db.session.commit()
        flash('Room created successfully.', 'success')

    # Only allow admin users to access the admin page, otherwise redirect to dashboard.
    if Users.query.get(current_user.id).is_admin:
        return render_template('admin.html', form=form)
    else:
        return redirect(url_for('dashboard'))

@app.route('/booking', methods = ['GET', 'POST'])
@login_required
def booking():
    form = BookingForm()

    # Initializing flag for validation error.
    ''' Used to correctly validate that a room for selected dates is available.
    If there is an error, room_validation will remain false & the database will not have a new commit and a flash message will be shown.
    If there are no errors, room_validation will be set to true and the database will be updated with the new booking.'''
    room_validation = False
    hotel_booked = False

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


        if form.room_type.data != 'none': # If hotel booking fields are filled out, validate hotel booking
            if not form.start_date_hotel.data and form.end_date_hotel.data:
                flash('Please enter a start date for the hotel booking.', 'danger')

            else:
                if form.start_date_hotel.data >= form.end_date_hotel.data:
                    flash('Hotel end date must be after start date, and last at least one night.', 'danger')

                rooms = Room.query.filter_by(room_type=form.room_type.data).all() # Check if room type is available
                if not rooms:
                    flash('Selected room type is not available.', 'danger')

                for room in rooms:
                    if room.latest_checkin <= form.start_date_hotel.data: # Check if room is available for selected dates
                        selected_room=room.room_id
                        room_validation = True
                        break
                    else:
                        room_validation = False 
                        selected_room = None


                new_hotel_booking = Hotel_Booking(
                    start_date=form.start_date_hotel.data, # Start date of hotel stay
                    end_date=form.end_date_hotel.data, # End date of hotel stay
                    user_id=current_user.id,  # Links booking to logged-in user
                    room_id=selected_room # Links to selected room for hotel booking
                )

                hotel_booked = True

            if hotel_booked == True and room_validation == True:
                db.session.add(new_hotel_booking)

            # Updates the latest check-in date for the selected room to ensure it is not double-booked for overlapping dates in the future
            room_update = Room.query.filter_by(room_id=selected_room).first()
            if room_update:
                room_update.latest_checkin = form.end_date_hotel.data

        ''' These variables are used to pass relevant booking information to the payment page after successful validation.
        The ticket information is used to calculate the cost of each ticket, before being multiplied by the visit time to get the total cost of the zoo visit.
        The educational visit boolean is used to apply a discount to the total cost of the zoo visit if applicable.
        The room price is multiplied by the hotel time to get the total cost of the hotel stay.'''
        child_tickets = form.child_tickets.data
        adult_tickets = form.adult_tickets.data
        visit_time = 1 + (datetime.strptime(form.end_date_zoo.data, '%Y-%m-%d') - datetime.strptime(form.start_date_zoo.data, '%Y-%m-%d')).days
        educational_visit = form.educational_visit.data
        loyalty_points = Users.query.filter_by(id=current_user.id).first().loyalty_points

        if hotel_booked == True and room_validation == True:
            room_price = Room.query.filter_by(room_id=selected_room).first().room_price
            hotel_time = (datetime.strptime(form.end_date_hotel.data, '%Y-%m-%d') - datetime.strptime(form.start_date_hotel.data, '%Y-%m-%d')).days
            total_cost = calculate_cost(child_tickets, adult_tickets, visit_time, educational_visit, room_price, hotel_time, loyalty_points)
        elif hotel_booked == False:
            hotel_time = 0
            room_price = 0
            total_cost = calculate_cost(child_tickets, adult_tickets, visit_time, educational_visit, room_price, hotel_time, loyalty_points)
        else:
            flash('Hotel booking validation failed. Please correct the errors and try again.', 'danger')
            return redirect(url_for('booking'))

        loyalty_update = Users.query.filter_by(id=current_user.id).first()
        if loyalty_update:
            if loyalty_update.loyalty_points < 10: # Only adds loyalty points if the user has fewer than 10
                loyalty_update.loyalty_points += 1
            else:
                loyalty_update.loyalty_points = 0 # Resets loyalty points if 10 or more are reached.

        db.session.add(new_zoo_booking)
        db.session.add(loyalty_update)
        db.session.commit()
        flash('Booking successful! Total cost: £{:.2f}'.format(total_cost), 'success')
    
    return render_template('booking.html', form=form)

if __name__ == '__main__':
    app.run(debug=True)