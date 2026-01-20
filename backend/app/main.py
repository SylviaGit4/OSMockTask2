from flask import Flask, url_for, render_template, redirect
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField
from wtforms.validators import DataRequired
from flask_login import LoginManager, login_required, login_user

from flask_bootstrap import Bootstrap5

import os
from flask_sqlalchemy import SQLAlchemy
basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)

bootstrap = Bootstrap5(app)

app.config['SECRET_KEY'] = 'key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'data.sqlite')

db = SQLAlchemy(app)