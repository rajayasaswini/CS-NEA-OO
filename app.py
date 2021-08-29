from flask import Flask, render_template, url_for, flash, redirect
from forms import *
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Length, Email, EqualTo
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from sqlalchemy.sql import text
from sqlalchemy import *
from sqlalchemy.orm import relationship, backref
from sqlalchemy.ext.declarative import declarative_base
from flask_bcrypt import Bcrypt
from models import *

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///TimeMe.db'
app.config['SECRET_KEY'] = 'cb1414668bb6f2a30c99cfb0e9c1441b'

# this variable, db, will be used for all SQLAlchemy commands
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/aregister', methods=['GET', 'POST'])
def aregister():
    form = aRegistrationForm()
    if form.validate_on_submit():
        flash(f'Account created for {form.firstname.data}!','success')
        return redirect(url_for('login'))
    return render_template("admin/aregister.html", title="Register", form=form)

@app.route('/uregister', methods=['GET', 'POST'])
def uregister():
    form = uRegistrationForm()
    if form.validate_on_submit():
        flash(f'Account created for {form.firstname.data}!','success')
        return redirect(url_for('login'))
    return render_template("user/uregister.html", title="Register", form=form)

@app.route('/choice', methods=['GET', 'POST'])
def choice():
    return render_template("choice.html")

@app.route('/enterclasscode', methods=['GET','POST'])
def entercode():
    form = ClassForm()
    if form.validate_on_submit():
        return redirect(url_for('udash'))
    return render_template("entercode.html", title="Enter Code", form=form)

@app.route('/admindash', methods=['GET', 'POST'])
def adash():
    return render_template("admin/admindash.html")

@app.route('/userdash', methods=['GET', 'POST'])
def udash():
    return render_template("user/userdash.html")

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = Users.query.filter_by(email=form.email.data).first()
        if user and Bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('admindash'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
    return render_template("login.html", title="Login", form=form)

@app.route('/admindashboard', methods=['GET', 'POST'])
def admindash():
    return render_template("admin/admindash.html")

if __name__ == "__main__":
    app.run(debug=True)
