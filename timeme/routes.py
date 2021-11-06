from flask import Flask, render_template, url_for, flash, redirect
from timeme import app, db, bcrypt, mail
from timeme.forms import *
from timeme.models import *
from flask_wtf import FlaskForm
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from sqlalchemy import *
from flask_bcrypt import Bcrypt
from flask_login import login_user, current_user, logout_user
from flask_mail import Message
import json

def check_user():
    if current_user.is_authenticated:
        if current_user.isAdmin == 1:
            return 1
        elif current_user.isAdmin == 0:
            return 0
    else:
        return 2
#done
@app.route('/')
def index():
    check = check_user()
    if check == 1:
        return redirect(url_for('viewclasses'))
    elif check == 0:
            return redirect(url_for('udash'))
    return render_template("index.html")
#done
@app.route('/aregister', methods=['GET', 'POST'])
def aregister():
    check = check_user()
    if check == 1:
        return redirect(url_for('viewclasses'))
    elif check == 0:
        return redirect(url_for('udash'))
    form = aRegistrationForm()
    if form.validate_on_submit():
        hashed_pass = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = Users(email=form.email.data, firstname=form.firstname.data, birthday=form.bday.data, lastname=form.lastname.data, password=hashed_pass, isAdmin=1)
        db.session.add(user)
        db.session.commit()
        flash(f'Login now','success')
        return redirect(url_for('login'))
    return render_template("admin/aregister.html", title="Register", form=form)
#done
@app.route('/uregister', methods=['GET', 'POST'])
def uregister():
    check = check_user()
    if check == 1:
        return redirect(url_for('viewclasses'))
    elif check == 0:
        return redirect(url_for('udash'))
    else:
        form = uRegistrationForm()
        if form.validate_on_submit():
            hashed_pass = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
            user = Users(email=form.email.data, firstname=form.firstname.data, lastname=form.lastname.data, birthday=form.bday.data, password=hashed_pass, isAdmin=0)
            db.session.add(user)
            db.session.commit()
            login_user(user)
            flash(f'Login now','success')
            return redirect(url_for('entercode'))
        return render_template("user/uregister.html", title="Register", form=form)
#done
@app.route('/choice', methods=['GET', 'POST'])
def choice():
    check = check_user()
    if check == 0:
        return redirect(url_for('udash'))
    elif check == 1:
        return redirect(url_for('adash'))
    return render_template("choice.html")
#done
@app.route('/admindash', methods=['GET', 'POST'])
def adash():
    check = check_user()
    if check == 0:
            return redirect(url_for('udash'))
    elif check == 1:
        #get a sum of the distance run of a user
        labels = []
        d_vs_t = db.session.query(UserDST.userID, UserDST.userDistance).filter_by(isAssignment = 0).all()
        for row in d_vs_t:
            name = db.session.query(Users.firstname).filter_by(id = row[0]).first()
            labels.append(name)
        labels = [row[0] for row in labels]
        values = [row[1] for row in d_vs_t]
        name = current_user.firstname
        return render_template("admin/admindash.html", labels=labels, values=values, name=name)
    else:
        return redirect(url_for('login'))
#done
@app.route('/userdash', methods=['GET', 'POST'])
def udash():
    check = check_user()
    if check == 1:
            return render_template("admin/admindash.html")
    elif check == 0:
        d_vs_t = list(db.session.query(UserDST.dstDateTime, UserDST.userDistance).filter_by(isAssignment = 0).all())
        print(d_vs_t)
        dates = []
        for i in d_vs_t:
            print("i", i)
            for j in i:
                print("j", j)
        labels = [row[0] for row in d_vs_t]
        values = [row[1] for row in d_vs_t]
        name = current_user.firstname
        return render_template("user/userdash.html", labels=labels, values=values, name=name)
    else:
        return redirect(url_for('login'))
#done
@app.route('/login', methods=['GET', 'POST'])
def login():
    check = check_user()
    if check == 1:
        return redirect(url_for('viewclasses'))
    elif check == 0:
        return redirect(url_for('udash'))
    form = LoginForm()
    if form.validate_on_submit():
        #if form.validate_on_submit():
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
    headings = ('Class Name', 'Class Code')
    data = ()
    classdata = []
    check = check_user()
    if check == 1:
        classN = Classes.query.filter_by(classAdminID=current_user.id).all()
        print("classN:", classN)
        for i in classN:
            classdata.append(i)
            for i in classdata:
                print(i)
    elif check == 0:
        return redirect(url_for('udash'))
    else:
        return redirect(url_for('login'))
    return render_template("admin/viewclasses.html")

@app.route('/addclass', methods=['GET', 'POST'])
def addclass():
    form=AddClass()
    if form.validate_on_submit():
        class1 = Classes(className=form.classname.data, classCode=form.classcode.data, classAdminID=current_user.id)
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
    check = check_user()
    if check == 0:
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
    elif check == 1:
        form = AdminEnterData()
        if form.validate_on_submit():
            name = str(form.user.data)
            name = name.split(' ')
            fname,lname = name[0], name[1]
            userid = int(Users.query.filter_by(firstname=fname, lastname=lname).first().id)
            typeid = int(EventTypes.query.filter_by(type=str(form.eventType.data)).first().id)
            time = int(form.userTimeM.data)*60 + int(form.userTimeS.data)
            userSpeed = getspeed(time, str(form.eventDistance.data), userSpeed)
            dist = str(form.eventDistance.data)
            dist = int(dist)
            eventid = int(Events.query.filter_by(eventTypeID=typeid, eventDistance=dist).first().eventID)
            userdst = UserDST(userID=userid, eventID=eventid, userDistance=dist, userTime=time , userSpeed=userSpeed, isAssignment=0)
            db.session.add(userdst)
            db.session.commit()
        return render_template("admin/adminenterdata.html", form=form)
    else:
        return redirect(url_for('login'))

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

#done
@app.route('/createE', methods=['GET', 'POST'])
def createevent():
    check = check_user()
    if check == 1:
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
    elif check == 0:
        return redirect(url_for('udash'))
    else:
        form = LoginForm()
        return redirect(url_for('login'))
#done
@app.route('/createET', methods=['GET', 'POST'])
def createET():
    check = check_user()
    if check == 1:
        form = CreateEventType()
        if form.validate_on_submit():
            newET = EventTypes(type=form.eventType.data)
            db.session.add(newET)
            db.session.commit()
        return render_template("createeventtype.html", form=form)
    elif check == 0:
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
    #form = Profile()
    fname = current_user.firstname
    lname = current_user.lastname
    about = current_user.about
    bday = current_user.birthday
    return render_template("profile.html", fname = fname, lname = lname, about = about, bday = bday)

def send_rp_email(user):
    token = user.get_token()
    mess = Message('Password Reset Request', sender="noreply@timeme.com", recipients=[user.email])
    mess.body = f'''This email has been sent since you want to reset your password.
If you did not request to reset your password, please ignore this email.
{url_for('reset_token', token=token, _external=True)}'''
    mail.send(mess)

@app.route('/requestpass', methods=['GET', 'POST'])
def reset_request():
    check = check_user()
    if current_user.is_authenticated:
        return redirect(url_for('adash'))
    form = RequestResetPass()
    if form.validate_on_submit():
        email = Users.query.filter_by(email=form.email.data).first()
        send_rp_email(email)
        flash('An email has been sent to your email address.', 'info')
        return redirect(url_for('login'))
    return render_template('requestrp.html', form=form)

@app.route('/resetpass/<token>', methods=['GET', 'POST'])
def reset_token(token):
    check = check_user()
    if check == 1:
        return redirect(url_for('adash'))
    elif check == 0:
        return redirect(url_for('udash'))
    user = Users.verify_token(token)
    if user is None:
        flash('Invalid token', 'warning')
        return redirect(url_for('reest_request'))
    form = ResetPass()
    if form.validate_on_submit():
        hashed_pass = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user.password = hashed_pass
        db.session.commit()
        flash(f'Login now','success')
        return redirect(url_for('login'))
    return render_template('resetpass.html', form=form)
