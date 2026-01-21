from flask import Flask, url_for, render_template, redirect 
from flask_cors import CORS # Added to allow other files to call the app
from flask_wtf import FlaskForm # For creating forms
from wtforms import StringField, SubmitField, PasswordField # For creating forms
from wtforms.validators import DataRequired # For creating forms
from flask_login import LoginManager, login_required, login_user # For ensuring user login protection
from pathlib import Path # For handling file paths
from flask_bootstrap import Bootstrap5 # Bootstrap CSS integration
from flask_sqlalchemy import SQLAlchemy #

base_dir = Path.cwd()
data_dir = (base_dir / "backend" / "data" / "data.sqlite")
template_dir = str(base_dir / "frontend" / "templates")

app = Flask(__name__, template_folder=template_dir)

CORS(app)

bootstrap = Bootstrap5(app)

app.config['SECRET_KEY'] = 'key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + str(data_dir)

db = SQLAlchemy(app)


@app.route('/')
def index():
    return render_template('index.html')


if __name__ == '__main__':
    app.run(debug=True)