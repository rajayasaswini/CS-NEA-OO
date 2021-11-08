import os
from flask import Flask, render_template, url_for, flash, redirect
from flask_wtf import FlaskForm
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from sqlalchemy import *
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_mail import Mail

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///TimeMe.db'
app.config['SECRET_KEY'] = 'cb1414668bb6f2a30c99cfb0e9c1441b'

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_man = LoginManager(app)
app.config['MAIL_SERVER'] = 'smtp.office365.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
<<<<<<< HEAD
app.config['MAIL_USERNAME'] = 'email-outlook'
app.config['MAIL_PASSWORD'] = 'password'
=======
app.config['MAIL_USERNAME'] = 'raja8450@dubaicollege.org'
app.config['MAIL_PASSWORD'] = 'sweety'
>>>>>>> ba7b071bb452ab4ef0285940b60b0c44c8b26801
mail = Mail(app)

from timeme import routes
