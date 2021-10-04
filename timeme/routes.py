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
#done
@app.route('/')
def index():
    if current_user.is_authenticated:
        if current_user.isAdmin == 1:
            return redirect(url_for('viewclasses'))
        else:
            return redirect(url_for('udash'))
    return render_template("index.html")
#done
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
#done
@app.route('/uregister', methods=['GET', 'POST'])
def uregister():
    if current_user.is_authenticated:
        if current_user.isAdmin == 1:
            return redirect(url_for('adash'))
        else:
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
    else:
        return redirect(url_for('login'))
#done
@app.route('/choice', methods=['GET', 'POST'])
def choice():
    if current_user.is_authenticated:
        if current_user.isAdmin == 0:
            return redirect(url_for('udash'))
        else:
            return redirect(url_for('adash'))
    else:
        return render_template("choice.html")
#done
@app.route('/admindash', methods=['GET', 'POST'])
def adash():
    if current_user.is_authenticated:
        if current_user.isAdmin == 0:
            return redirect(url_for('udash'))
        elif current_user.isAdmin == 1:
            return render_template("admin/admindash.html")
    else:
        return redirect(url_for('login'))
#done
@app.route('/userdash', methods=['GET', 'POST'])
def udash():
    if current_user.is_authenticated:
        if current_user.isAdmin == 1:
            return render_template("admin/admindash.html")
        else:
            return render_template("user/userdash.html")
    else:
        return redirect(url_for('login'))
#done
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
                    return redirect(url_for('udash'))
        else:
            flash('Login Unsuccessful. Please check username and password', 'danger')
    return render_template("login.html", title="Login", form=form)

@app.route('/viewclass', methods=['GET', 'POST'])
def viewclasses():
    if current_user.is_authenticated and current_user.isAdmin == 1:
        classN = Classes.query.filter_by(classAdminID=current_user.id).all().classCode
        print(className)
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

from python.getspeed import *

@app.route('/enterdata', methods=['GET', 'POST'])
def enterdata():
    userSpeed = 0
    now = datetime.now()
    if current_user.isAdmin == 0:
        form = UserEnterData()
        if form.validate_on_submit():
            time = int(form.userTimeM.data)*60 + int(form.userTimeS.data)
            userSpeed = getspeed(time, str(form.eventDistance.data), userSpeed)
            dist = str(form.eventDistance.data)
            dist = int(dist)
            typeid = int(EventTypes.query.filter_by(type=str(form.eventType.data)).first().id)
            eventid = int(Events.query.filter_by(eventTypeID=typeid, eventDistance=int(str(form.eventDistance.data))).first().eventID)
            userdst = UserDST(userID=current_user.id, eventID=eventid, userDistance=dist, userTime=time , userSpeed=userSpeed, isAssignment=0)
            db.session.add(userdst)
            db.session.commit()
        return render_template("user/userenterdata.html", form=form)
    elif current_user.isAdmin == 1:
        form = AdminEnterData()
        if form.validate_on_submit():
            name = str(form.user.data)
            name = name.split(' ')
            fname,lname = name[0], name[1]
            userid = int(Users.query.filter_by(firstname=fname, lastname=lname).first().id)
            typeid = int(EventTypes.query.filter_by(type=str(form.eventType.data)).first().id)
            time = int(form.userTimeM.data)*60 + int(form.userTimeS.data)
            userSpeed = getspeed(time, str(form.eventDistance.datfa), userSpeed)
            dist = str(form.eventDistance.data)
            dist = int(dist)
            eventid = int(Events.query.filter_by(eventTypeID=typeid, eventDistance=dist).first().eventID)
            userdst = UserDST(userID=userid, eventID=eventid, userDistance=dist, userTime=time , userSpeed=userSpeed, isAssignment=0)
            db.session.add(userdst)
            db.session.commit()
        return render_template("admin/adminenterdata.html", form=form)
    else:
        return render_template("login.html")

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

#done
@app.route('/createE', methods=['GET', 'POST'])
def createevent():
    if current_user.isAdmin == 1:
        form = CreateEvent()
        if form.validate_on_submit():
            eventid = int(EventTypes.query.filter_by(type=str(form.eventType.data)).first().id)
            dist = form.eventDistance.data
            if form.eventDistance.data is None:
                time = int(form.userTimeM.data)*60 + int(form.userTimeS.data)
                neweve = Events(eventTypeID=eventid, eventDistance=0, eventTime=time)
                db.session.add(neweve)
            else:
                neweve = Events(eventTypeID=eventid, eventDistance=int(str(form.eventDistance.data)), eventTime=0)
                db.session.add(neweve)
            db.session.commit()
        return render_template("createevent.html", form=form)
    elif current_user.isAdmin == 0:
        return redirect(url_for('udash'))
    else:
        form = LoginForm()
        return redirect(url_for('login'))
#done
@app.route('/createET', methods=['GET', 'POST'])
def createET():
    if current_user.isAdmin == 1:
        form = CreateEventType()
        if form.validate_on_submit():
            newET = EventTypes(type=form.eventType.data)
            db.session.add(newET)
            db.session.commit()
        return render_template("createeventtype.html", form=form)
    elif current_user.isAdmin == 0:
        return redirect(url_for('udash'))
    else:
        return redirect(url_for('login'))

@app.route('/classposts')
def classposts():
    return render_template("temp.html")

@app.route('/gallery')
def gallery():
    return render_template("temp.html")

@app.route('/assignments')
def assignments():
    return render_template("temp.html")

@app.route('/posts')
def posts():
    return render_template("temp.html")

@app.route('/data')
def data():
    return render_template("temp.html")

@app.route('/journal')
def journal():
    return render_template("temp.html")

@app.route('/timer')
def timer():
    return render_template("temp.html")

@app.route('/profile')
def profile():
    return render_template("temp.html")
