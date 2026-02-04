from flask_wtf import FlaskForm # For creating forms
from wtforms import StringField, SubmitField, PasswordField # For creating forms
from wtforms.validators import DataRequired # For creating forms

class RegistrationForm(FlaskForm):
    username = StringField(validators=[DataRequired()])
    email = StringField(validators=[DataRequired()])
    password = PasswordField(validators=[DataRequired()])
    submit = SubmitField("Register")

class LoginForm(FlaskForm):
    email = StringField(validators=[DataRequired()])
    password = PasswordField(validators=[DataRequired()])
    submit = SubmitField("Login")

