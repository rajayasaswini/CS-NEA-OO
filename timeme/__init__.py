from flask import Flask, render_template, url_for, flash, redirect
from flask_wtf import FlaskForm
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from sqlalchemy import *
from flask_bcrypt import Bcrypt
from flask_login import LoginManager

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///TimeMe.db'
app.config['SECRET_KEY'] = 'cb1414668bb6f2a30c99cfb0e9c1441b'

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

from timeme import routes
