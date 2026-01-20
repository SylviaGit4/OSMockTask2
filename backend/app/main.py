from flask import Flask, url_for, render_template, redirect
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField
from wtforms.validators import DataRequired
from flask_login import LoginManager, login_required, login_user
from pathlib import Path

from flask_bootstrap import Bootstrap5

import os
from flask_sqlalchemy import SQLAlchemy
basedir = Path.cwd()
print(str(basedir / "backend" / "data" / "data.sqlite"))

app = Flask(__name__)

bootstrap = Bootstrap5(app)

app.config['SECRET_KEY'] = 'key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + str(basedir / "backend" / "data" / "data.sqlite")

db = SQLAlchemy(app)