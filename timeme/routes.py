from flask import Flask, render_template, url_for, flash, redirect
from timeme import app
from timeme.forms import *
from timeme.models import *
from flask_wtf import FlaskForm
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from sqlalchemy import *
from flask_bcrypt import Bcrypt

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
        if form.email.data == 'admin@timeme.com' and form.password.data == 'password':
            flash('You have been logged in!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Login Unsuccessful. Please check username and password', 'danger')
    return render_template("login.html", title="Login", form=form)
