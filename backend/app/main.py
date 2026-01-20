from flask import Flask, url_for, render_template, redirect 
from flask_cors import CORS # Added to allow other files to call the app
from flask_wtf import FlaskForm # For creating forms
from wtforms import StringField, SubmitField, PasswordField # For creating forms
from wtforms.validators import DataRequired # For creating forms
from flask_login import LoginManager, login_required, login_user # For ensuring user login protection
from pathlib import Path # For handling file paths
from flask_bootstrap import Bootstrap5 # Bootstrap CSS integration
from flask_sqlalchemy import SQLAlchemy #

basedir = Path.cwd()
datadir = (basedir / "backend" / "data" / "data.sqlite")

app = Flask(__name__)

CORS(app)

bootstrap = Bootstrap5(app)

app.config['SECRET_KEY'] = 'key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + str(datadir)

db = SQLAlchemy(app)