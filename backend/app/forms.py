from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, IntegerField, BooleanField, PasswordField
from wtforms.validators import DataRequired, Optional

class ZooBookingForm(FlaskForm):
    start_date_zoo = StringField('Start Date', validators=[DataRequired()])
    end_date_zoo = StringField('End Date', validators=[DataRequired()])
    child_tickets = IntegerField('Child Tickets', default=0, validators=[Optional()])
    adult_tickets = IntegerField('Adult Tickets', default=0, validators=[Optional()])
    educational_visit = BooleanField('Educational Visit')
    submit = SubmitField('Book')

class RegistrationForm(FlaskForm):
    username = StringField(validators=[DataRequired()])
    email = StringField(validators=[DataRequired()])
    password = PasswordField(validators=[DataRequired()])
    submit = SubmitField("Register")

class LoginForm(FlaskForm):
    email = StringField(validators=[DataRequired()])
    password = PasswordField(validators=[DataRequired()])
    submit = SubmitField("Login")
