from flask import Flask, render_template, url_for, flash, redirect, session
#from flask.ext.session import Session
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

#session["isAssignment"] = 0

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
        classname = list(db.session.query(Classes.className).filter_by(classID=session["current_classid"]).first())
        classname = classname[0]
        for row in d_vs_t:
            name = db.session.query(Users.firstname).filter_by(id = row[0]).first()
            labels.append(name)
        labels = [row[0] for row in labels]
        values = [row[1] for row in d_vs_t]
        name = current_user.firstname
        return render_template("admin/admindash.html", labels=labels, values=values, name=name, classname=classname)
    else:
        return redirect(url_for('login'))
#done
@app.route('/userdash', methods=['GET', 'POST'])
def udash():
    check = check_user()
    if check == 1:
            return render_template("admin/admindash.html")
    elif check == 0:
        session["current_classid"] = (list(db.session.query(ClassesUsers.classID).filter_by(usersID=current_user.id).first()))[0]
        d_vs_t = list(db.session.query(UserDST.dstDateTime, UserDST.userDistance).filter_by(isAssignment = 0).all())
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
    #checks the user's authentication
    check = check_user()
    #if admin
    if check == 1:
        #form is set to SelectClass
        form = SelectClass()
        #getting the class names and codes to put in table
        classn = list(db.session.query(Classes.className, Classes.classCode).filter_by(classAdminID = current_user.id).all())
        #setting the headings of the columns
        headings = ('Class Name', 'Class Code')
        #if the form is validated
        if form.validate_on_submit():
            print(form.classname.data)
            #we get the classid from the name that we got from the form
            classid = list(db.session.query(Classes.classID).filter_by(className=str(form.classname.data), classAdminID=current_user.id).first())
            session["current_classid"] = classid[0]
            return redirect(url_for('adash'))
            #current_classid = classid[0]
            #print(current_classid)
            #if current_classid is not None:
                #pass
            #return redirect(url_for('adash'))
        return render_template("admin/viewclasses.html", headings=headings, classes=classn, form=form)
    elif check == 0:
        return redirect(url_for('udash'))
    else:
        return redirect(url_for('login'))
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
#done
@app.route('/enterdata', methods=['GET', 'POST'])
def enterdata():
    userSpeed = 0
    now = datetime.now()
    check = check_user()
    if check == 0:
        form = UserEnterData()
        assign = 0
        if session["isAssignment"] == 1:
            assign = 1
            print(session["isAssignment"])
            print(session["current_assignment"])
        if form.validate_on_submit():
            time = int(form.userTimeM.data)*60 + int(form.userTimeS.data)
            userSpeed = getspeed(time, str(form.eventDistance.data), userSpeed)
            dist = str(form.eventDistance.data)
            dist = int(dist)
            typeid = int(EventTypes.query.filter_by(type=str(form.eventType.data)).first().id)
            eventid = int(Events.query.filter_by(eventTypeID=typeid, eventDistance=int(str(form.eventDistance.data))).first().eventID)
            userdst = UserDST(userID=current_user.id, eventID=eventid, userDistance=dist, userTime=time , userSpeed=userSpeed, isAssignment=assign)
            if session["isAssignment"] == 1:
                assign = 1
                details = session["current_assignment"]
                time = int(form.userTimeM.data)*60 + int(form.userTimeS.data)
                typeid = int(EventTypes.query.filter_by(type=details[0]).first().id)
                eventid = int(Events.query.filter_by(eventTypeID=typeid, eventDistance=details[1]).first().eventID)
                userdst = UserDST(userID=current_user.id, eventID=eventid, userDistance=int(details[1]), userTime=time , userSpeed=0.1, isAssignment=assign)
            db.session.add(userdst)
            db.session.commit()
            if session["isAssignment"] == 1:
                userdstid = userdst.userDSTID
                assignment = ReturnedAssignment(schassid=session["current_assignmentid"], userdstid=userdstid, isLate=0)
                db.session.add(assignment)
                db.session.commit()
        return render_template("user/userenterdata.html", form=form)
    elif check == 1:
        form = AdminEnterData()
        if form.validate_on_submit():
            name = str(form.user.data)
            name = name.split(' ')
            fname = ''
            lname = ''
            if len(name) == 2:
                fname,lname = name[0], name[1]
            elif len(name) > 2:
                lname = name[len(name)-1]
                name.remove(lname)
                count = 0
                for i in name:
                    if count == 0:
                        fname += i + ' '
                        count += 1
                    else:
                        fname += i
                count = 0
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
#done
@app.route('/logout')
def logout():
    session["current_classid"] = 0
    val = session["current_classid"]
    print(val)
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
                time = int(form.eventTimeM.data)*60 + int(form.eventTimeS.data)
                neweve = Events(eventTypeID=eventid, eventDistance=0, eventTime=time)
                db.session.add(neweve)
            else:
                neweve = Events(eventTypeID=eventid, eventDistance=int(str(form.eventDistance.data)), eventTime=0)
                db.session.add(neweve)
            db.session.commit()
        return render_template("admin/createevent.html", form=form)
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
        return render_template("admin/createeventtype.html", form=form)
    elif check == 0:
        return redirect(url_for('udash'))
    else:
        return redirect(url_for('login'))
#done
@app.route('/createassignment', methods=['GET', 'POST'])
def createassignment():
    form = SetAssignment()
    if form.validate_on_submit():
        typeid = int(EventTypes.query.filter_by(type=str(form.eventtype.data)).first().id)
        eventid = int(Events.query.filter_by(eventTypeID=typeid, eventDistance=int(str(form.eventdist.data))).first().eventID)
        a = ScheduledAssignments(classID=session["current_classid"], eventID=eventid, returnDate=form.dday.data)
        db.session.add(a)
        db.session.commit()
    return render_template("admin/assignments.html", form=form)

@app.route('/assignment', methods=['GET', 'POST'])
def submitassignment():
    check = check_user()
    if check == 0:
        assign = []
        form = SelectAssignment()
        headings = ['Event Type', 'Event Distance', 'Due Date']
        assignment = list(db.session.query(EventTypes.type, Events.eventDistance, ScheduledAssignments.returnDate).select_from(EventTypes).join(Events).join(ScheduledAssignments).all())
        print(assignment)
        form.assignmentname.choices = assignment
        #for type, event, assign in assignment:
            #schass = [str(type), str(event), str(assign)]
            #schass2 = [i for i in schass]
            #assign.append(schass2)
        #print("schass2", schass2)
        count = 1
        for type, event, assign in assignment:
            #print("tea",type,event,assign)
            schass = [str(count), str(type) + " "  + str(event) + " " + str(assign)]
            schass2 = [i for i in schass]
            schass3 = [i.split() for i in schass]
            schass4 = [schass[1]]
        print("schass4", schass4)
        #    schass3 = [str(count), str(type), str(assign)]
        #    schass4 = [i for i in schass3]
        #    print(schass4)
        #    assignments.append(schass2)
        if form.validate_on_submit():
            session["isAssignment"] = 1
            print("assignmentname", form.assignmentname.data)
            #for i in form.assignmentname.data:
                #print("assignmentname", i)
            assignment1 = form.assignmentname.data
            #(type, event, assign) = assignment1
            type = assignment1[1][0]
            event = assignment[1][1]
            assign = assignment[1][2]
            #assign = assignment[2]
            print("type", type)
            print("event", event)
            print("assign", assign)
            #print("assignment1", assignment1)
            #for type, event, assign in assignment1:
                #assignmentlist = [str(type), str(event), str(assign)]
                #print("assignmentlist", assignmentlist)
            #for i in form.assignmentname.data:
                #print("i", i)
            assignmentlist = ['Sprint', '1000', '2021-10-20']
            session["current_assignment"] = assignmentlist
            typeid = int(EventTypes.query.filter_by(type=assignmentlist[0]).first().id)
            eventid = int(Events.query.filter_by(eventTypeID=typeid, eventDistance=assignmentlist[1]).first().eventID)
            print(typeid, eventid)
            print(eventid, assignmentlist[2])
            session["current_assignmentid"] = ScheduledAssignments.query.filter_by(classID=session["current_classid"], eventID=eventid, returnDate=str(assignmentlist[2])).first()
            #print ("assignmentid", session["current_assignmentid"])
            #print(assignmentlist[2])
            return redirect(url_for('enterdata'))
        return render_template('user/assignments.html', headings=headings, assignments=assignment, form=form)
    else:
        return redirect(url_for('login'))
        #assignment = list(db.session.query(EventTypes, Events, ScheduledAssignments).select_from(EventTypes).join(Events).join(ScheduledAssignments).all())
        #print(assignment)
        #print(assignments)
        #for type, event, assign in assignment:
            #print (str(type.type), str(event.eventDistance), str(assign.returnDate))
        #assign = []
        #for type, event, assign in assignment:
        #    schass = [str(type.type) + ' ' + str(event.eventDistance), str(assign.returnDate)]
        #    print(schass)
            #labels = [row[0] for row in labels]
            #values = [row[1] for row in d_vs_t]

        #print(assign)

        #setting the headings of the columns
        #headings = ('Event Type', 'EventDistance','Event Time' 'Due Date')

            #classid = list(db.session.query(Classes.classID).filter_by(className=str(form.classname.data), classAdminID=current_user.id).first())
    #        session["isAssignment"] = 1
    #        return redirect(url_for('enterdata'))

@app.route('/data')
def data():
    return render_template("temp.html")

@app.route('/timer')
def timer():
    return render_template("temp.html")

@app.route('/profile')
def profile():
    image_file = url_for('static', filename='pics/' + current_user.photo)
    return render_template("profile.html")

def send_rp_email(user):
    token = user.get_token()
    mess = Message('Password Reset Request', sender="raja8450@dubaicollege.org", recipients=[user.email])
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
        return redirect(url_for('reset_request'))
    form = ResetPass()
    if form.validate_on_submit():
        hashed_pass = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user.password = hashed_pass
        db.session.commit()
        flash(f'Login now','success')
        return redirect(url_for('login'))
    return render_template('resetpass.html', form=form)
