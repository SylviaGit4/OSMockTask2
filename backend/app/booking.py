from flask import Flask, request
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
from sqlalchemy.orm import DeclarativeBase
from flask_sqlalchemy import SQLAlchemy

class BookingForm(FlaskForm):
    start_date_zoo = StringField('Start Date', validators=[DataRequired()])
    end_date_zoo = StringField('End Date', validators=[DataRequired()])
    submit = SubmitField('Book')


def get_booking_from_request():
    """Helper to read booking fields from request.form inside a request context.
    Call this from within a view function (not at import time).
    """
    return {
        'start_date_zoo': request.form.get('zoo_start'),
        'end_date_zoo': request.form.get('zoo_end')
    }
