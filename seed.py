""" This will create the database. 
Call: heroku run python seed.py first
and then
heroku pg:psql < data.sql
"""
from classes.models import db

db.create_all()
