from flask import Flask, render_template, url_for, flash, redirect
from timeme import app, db, bcrypt
from timeme.forms import *
from timeme.models import *
from flask_wtf import FlaskForm
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from sqlalchemy import *
from flask_bcrypt import Bcrypt
from flask_login import login_user, current_user, logout_user

@app.route('/')
def index():
    if current_user.is_authenticated:
        if current_user.isAdmin == 1:
            return redirect(url_for('viewclasses'))
        else:
            return redirect(url_for('udash'))
    return render_template("index.html")

@app.route('/aregister', methods=['GET', 'POST'])
def aregister():
    if current_user.is_authenticated and current_user.isAdmin == 1:
        return redirect(url_for('viewclasses'))
    form = aRegistrationForm()
    if form.validate_on_submit():
        hashed_pass = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = Users(email=form.email.data, firstname=form.firstname.data, lastname=form.lastname.data, password=hashed_pass, isAdmin=1)
        db.session.add(user)
        db.session.commit()
        flash(f'Login now','success')
        return redirect(url_for('login'))
    return render_template("admin/aregister.html", title="Register", form=form)

@app.route('/uregister', methods=['GET', 'POST'])
def uregister():
    if current_user.is_authenticated and current_user.isAdmin == 1:
        return redirect(url_for('udash'))
    form = uRegistrationForm()
    if form.validate_on_submit():
        hashed_pass = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = Users(email=form.email.data, firstname=form.firstname.data, lastname=form.lastname.data, password=hashed_pass, isAdmin=0)
        db.session.add(user)
        db.session.commit()
        login_user(user)
        flash(f'Login now','success')
        return redirect(url_for('entercode'))
    return render_template("user/uregister.html", title="Register", form=form)

@app.route('/choice', methods=['GET', 'POST'])
def choice():
    return render_template("choice.html")

@app.route('/admindash', methods=['GET', 'POST'])
def adash():
    return render_template("admin/admindash.html")

@app.route('/userdash', methods=['GET', 'POST'])
def udash():
    return render_template("user/userdash.html")

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        if current_user.isAdmin == 1:
            return redirect(url_for('viewclasses'))
        else:
            return redirect(url_for('udash'))
    form = LoginForm()
    if form.validate_on_submit():
        if form.validate_on_submit():
            user1 = Users.query.filter_by(email=form.email.data).first()
            if user1 and bcrypt.check_password_hash(user1.password, form.password.data):
                login_user(user1, remember=form.remember.data)
                if user1.isAdmin == 1:
                    return redirect(url_for('viewclasses'))
                else:
                    return redirect(url_for('entercode'))
        else:
            flash('Login Unsuccessful. Please check username and password', 'danger')
    return render_template("login.html", title="Login", form=form)

@app.route('/viewclass', methods=['GET', 'POST'])
def viewclasses():
    data = Classes.query.all()
    return render_template("admin/viewclasses.html", data=data)

@app.route('/addclass', methods=['GET', 'POST'])
def addclass():
    form=AddClass()
    if form.validate_on_submit():
        class1 = Classes(classCode=form.classcode.data, classAdminID=current_user.id)
        db.session.add(class1)
        db.session.commit()
        flash(f'Class Created','success')
        return redirect(url_for('viewclasses'))
    return render_template("admin/addclass.html", form=form)

@app.route('/enterclasscode', methods=['GET','POST'])
def entercode():
    form = EnterCode()
    if form.validate_on_submit():
        classid = Classes.query.filter_by(classCode=form.classcode.data).first().classID
        classc = ClassesUsers(classID=classid, usersID=current_user.id)
        db.session.add(classc)
        db.session.commit()
        return redirect(url_for('udash'))
    return render_template("entercode.html", title="Enter Code", form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))
