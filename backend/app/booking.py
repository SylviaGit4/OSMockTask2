from flask import Flask, request
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, IntegerField, BooleanField
from wtforms.validators import DataRequired, Optional
from sqlalchemy.orm import DeclarativeBase
from flask_sqlalchemy import SQLAlchemy

class BookingForm(FlaskForm):
    start_date_zoo = StringField('Start Date', validators=[DataRequired()])
    end_date_zoo = StringField('End Date', validators=[DataRequired()])
    child_tickets = IntegerField('Child Tickets', default=0, validators=[Optional()])
    adult_tickets = IntegerField('Adult Tickets', default=0, validators=[Optional()])
    educational_visit = BooleanField('Educational Visit')
    submit = SubmitField('Book')
