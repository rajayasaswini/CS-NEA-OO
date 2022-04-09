from flask import Flask, render_template, url_for, flash, redirect, session, request
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
import numpy as np
from sklearn.linear_model import LinearRegression
from datetime import timedelta

test = 'abc'
#done
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
@app.route('/help', methods=['GET', 'POST'])
def help():
    logout_user()
    return redirect(url_for('index'))
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
    return render_template("choice.html", choice=1)
#done
@app.route('/admindash', methods=['GET', 'POST'])
def adash():
    check = check_user()
    if check == 0:
            return redirect(url_for('udash'))
    elif check == 1:
        #get a sum of the distance run of a user
        labels = []
        distances = []
        #using the current_classid, get the ids
        #then with the ids, get their firstnames and their distances
        #first get the firstname and append it to the labels list
        #then with the id, get all the distances that they have run
        #with all the distances that they have run, get the sum of the distance
        #add the names to the labels list
        #add the distances to the values list
        #all ids of the users in the class are added into a list
        ids = [row[0] for row in list(db.session.query(ClassesUsers.usersID).filter_by(classID=session["current_classid"]).all())]
        #all the names that are related to the userids are stored in the list
        names = [(db.session.query(Users.firstname).filter_by(id = row).first())[0] for row in ids]
        #for every id
        for i in ids:
            #sum of all the distances that they have run is saved
            distance = sum([row[0] for row in db.session.query(UserDST.userDistance).filter_by(userID=i).all()])
            #the total distance is saved in the list
            distances.append(distance)
        #getting the class name
        classname = (list(db.session.query(Classes.className).filter_by(classID=session["current_classid"]).first()))[0]
        #gets the name of the user
        name = current_user.firstname
        return render_template("admin/admindash.html", labels=names, values=distances, name=name, classname=classname)
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
#done
@app.route('/viewclass', methods=['GET', 'POST'])
def viewclasses():
    #checks the user's authentication
    check = check_user()
    session["current_classid"] = 0
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
            classid = list(db.session.query(Classes.classID).filter_by(className=str(form.classname.data), classAdminID=current_user.id).first())
            session["current_classid"] = classid[0]
            return redirect(url_for('adash'))
        return render_template("admin/viewclasses.html", headings=headings, classes=classn, form=form)
    elif check == 0:
        return redirect(url_for('udash'))
    else:
        return redirect(url_for('login'))
#done
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
#done
def send_classcode(user, classcode):
    mess = Message('Class Code', sender="raja8450@dubaicollege.org", recipients=[user])
    mess.body = f'''Your teacher has sent you a class code: {classcode}'''
    mail.send(mess)
#done
@app.route('/addmember', methods=['GET', 'POST'])
def addmember():
    form = UserEmail()
    if form.addUser.data:
        form.user.append_entry()
        return render_template("admin/addmemberemail.html", form=form)
    if form.submit.data:
        classcode = [i for i in db.session.query(Classes.classCode).filter(Classes.classID == session['current_classid']).first()][0]
        for i in form.user.data:
            email = i['userEmail']
            if len(email) != 0:
                send_classcode(email, classcode)
    return render_template("admin/addmemberemail.html", title="Add Member", form=form)
#done
@app.route('/enterclasscode', methods=['GET','POST'])
def entercode():
    form = EnterCode()
    if form.validate_on_submit():
        classid = Classes.query.filter_by(classCode=form.classcode.data).first().classID
        classc = ClassesUsers(classID=classid, usersID=current_user.id)
        db.session.add(classc)
        db.session.commit()
        return redirect(url_for('udash'))
    return render_template("user/entercode.html", title="Enter Code", form=form)

from python.getspeed import *
#done
def intervals(userid, intervaldata, userdstid):
    for i in intervaldata:
        id = UserDST.query.filter_by(userID=userid).all()
        if userdstid is not None:
            interval = Intervals.query.filter_by(userdstid=userdstid).all()
            if not len(interval):
                for j in intervaldata:
                    dist = j["intervalDist"]
                    timeM = int(j["intervalM"])
                    timeS = int(j["intervalS"])
                    time = timeM*60 + timeS
                    newinterval = Intervals(userdstid=userdstid, dist=dist, time=time)
                    db.session.add(newinterval)
            else:
                pass
    db.session.commit()
#done

def get_student_names():
    ids = [i[0] for i in db.session.query(ClassesUsers.usersID).filter_by(classID = session['current_classid'])]
    names = returnname(ids)
    return names

@app.route('/enterdata', methods=['GET', 'POST'])
def enterdata():
    userSpeed = 0
    now = datetime.now()
    check = check_user()
    error = ''
    if check == 0:
        form = UserEnterData()
        assign = 0
        form.eventDistance.choices = [i[0] for i in db.session.query(Events.eventDistance).filter(Events.eventDistance!=0)]
        if form.addInterval.data:
            form.userInterval.append_entry()
            return render_template("user/userenterdata.html", form=form, error=error)
        if form.validate_on_submit():
            time = int(form.userTimeM.data)*60 + int(form.userTimeS.data)
            userSpeed = getspeed(time, str(form.eventDistance.data), userSpeed)
            dist = str(form.eventDistance.data)
            dist = int(dist)
            typeid = int(EventTypes.query.filter_by(type=str(form.eventType.data)).first().id)
            eventid = int(Events.query.filter_by(eventTypeID=typeid, eventDistance=int(str(form.eventDistance.data))).first().eventID)
            if eventid == None:
                error = 'That event does not exist'
                return redirect(url_for('enterdata'))
            userdst = UserDST(userID=current_user.id, eventID=eventid, userDistance=dist, userTime=time , userSpeed=userSpeed, isAssignment=assign)
            db.session.add(userdst)
            db.session.commit()
            dstid = int(UserDST.query.filter_by(userID=current_user.id).all()[-1].userDSTID)
            intervals(current_user.id, form.userInterval.data, dstid)
        return render_template("user/userenterdata.html", form=form, error=error)
    elif check == 1:
        form = AdminEnterData()
        form.eventDistance.choices = [i[0] for i in db.session.query(Events.eventDistance).filter(Events.eventDistance!=0)]
        form.user.choices = get_student_names()
        if form.addInterval.data:
            form.userInterval.append_entry()
            return render_template("user/userenterdata.html", form=form, error=error)
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
            dstid = int(UserDST.query.filter_by(userID=userid).all()[-1].userDSTID)
            intervals(current_user.id, form.userInterval.data, dstid)
        return render_template("admin/adminenterdata.html", form=form, error=error)
    else:
        return redirect(url_for('login'))
#done
@app.route('/enterdist', methods=['GET', 'POST'])
def enterdist():
    userSpeed = 0
    now = datetime.now()
    check = check_user()
    error = ''
    if check == 0:
        form = UserEnterDist()
        assign = 0
        if form.addInterval.data:
            form.userInterval.append_entry()
            return render_template("user/userenterdata.html", form=form)
        times = [i[0] for i in db.session.query(Events.eventTime).filter(Events.eventTime!=0).all()]
        timeMS = []
        #changes time into MM:SS format
        for time in times:
            min = time//60
            sec = time - (min*60)
            if len(str(sec)) == 1:
                sec = "0"+str(sec)
            elif len(str(sec)) == 2:
                sec = str(sec)
            digtime = str(min) + ":" + sec
            timeMS.append(digtime)
        form.userTime.choices = timeMS
        if form.validate_on_submit():
            userSpeed = 0
            time = form.userTime.data
            times = [int(i) for i in time.split(":")]
            timeinS = times[0]*60 + times[1]
            userSpeed = getspeed(timeinS, str(form.eventDistance.data), userSpeed)
            dist = str(form.eventDistance.data)
            typeid = int(EventTypes.query.filter_by(type=str(form.eventType.data)).first().id)
            eventid = int(Events.query.filter_by(eventTypeID=typeid, eventTime=timeinS).first().eventID)
            if eventid == None:
                error = 'That event does not exist'
                return redirect(url_for('enterdist'))
            userdst = UserDST(userID=current_user.id, eventID=eventid, userDistance=dist, userTime=timeinS , userSpeed=userSpeed, isAssignment=assign)
            db.session.add(userdst)
            db.session.commit()
            dstid = int(UserDST.query.filter_by(userID=current_user.id).all()[-1].userDSTID)
            intervals(current_user.id, form.userInterval.data, dstid)
        return render_template("user/userenterdist.html", form=form, error = error)
    elif check == 1:
        form = AdminEnterDist()
        times = [i[0] for i in db.session.query(Events.eventTime).filter(Events.eventTime!=0).all()]
        timeMS = []
        for time in times:
            min = time//60
            sec = time - (min*60)
            if len(str(sec)) == 1:
                sec = "0"+str(sec)
            elif len(str(sec)) == 2:
                sec = str(sec)
            digtime = str(min) + ":" + sec
            timeMS.append(digtime)
        form.userTime.choices = timeMS
        form.user.choices = get_student_names()
        if form.addInterval.data:
            form.userInterval.append_entry()
            return render_template("admin/adminenterdist.html", form=form)
        if form.validate_on_submit():
            name = [str(form.user.data)]
            userid = (returnid(name))[0]
            fname = ''
            lname = ''
            userSpeed = 0
            time = form.userTime.data
            times = [int(i) for i in time.split(":")]
            timeinS = times[0]*60 + times[1]
            userSpeed = getspeed(timeinS, str(form.eventDistance.data), userSpeed)
            dist = int(str(form.eventDistance.data))
            typeid = int(EventTypes.query.filter_by(type=str(form.eventType.data)).first().id)
            eventid = int(Events.query.filter_by(eventTypeID=typeid, eventTime=timeinS).first().eventID)
            if eventid == None:
                error = 'That event does not exist'
                return redirect(url_for('enterdist'))
            userdst = UserDST(userID=userid, eventID=eventid, userDistance=dist, userTime=timeinS , userSpeed=userSpeed, isAssignment=0)
            db.session.add(userdst)
            db.session.commit()
            dstid = int(UserDST.query.filter_by(userID=userid).all()[-1].userDSTID)
            intervals(current_user.id, form.userInterval.data, dstid)
        return render_template("admin/adminenterdist.html", form=form, error = error)
    else:
        return redirect(url_for('login'))
#done
@app.route('/enterdatachoice', methods=['GET', 'POST'])
def enterdatachoice():
    return render_template("choice.html", choice=2)
#done
@app.route('/logout')
def logout():
    session["current_classid"] = 0
    val = session["current_classid"]
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
    error = ' '
    if check == 1:
        form = CreateEventType()
        if form.validate_on_submit():
            events = [str(i[0]).upper() for i in db.session.query(EventTypes.type).all()]
            if (form.eventType.data).upper() in events:
                error = 'There is already an event called ' + str(form.eventType.data)
                return render_template("admin/createeventtype.html", form=form, error=error)
            else:
                newET = EventTypes(type=form.eventType.data)
                db.session.add(newET)
                db.session.commit()
        return render_template("admin/createeventtype.html", form=form, error=error)
    elif check == 0:
        return redirect(url_for('udash'))
    else:
        return redirect(url_for('login'))
#done
@app.route('/setassignmentchoice', methods=['GET', 'POST'])
def setassignmentchoice():
    return render_template("choice.html", choice=3)
#done
@app.route('/createdistassignment', methods=['GET', 'POST'])
def createdistassignment():
    check = check_user()
    if check == 1:
        form = SetDistAssignment()
        distances = [i[0] for i in db.session.query(Events.eventDistance).filter(Events.eventDistance!=0).all()]
        form.eventDistance.choices = distances
        if form.validate_on_submit():
            typeid = int(EventTypes.query.filter_by(type=str(form.eventType.data)).first().id)
            eventid = int(Events.query.filter_by(eventTypeID=typeid, eventDistance=int(str(form.eventDistance.data))).first().eventID)
            a = ScheduledAssignments(classID=session["current_classid"], eventID=eventid, returnDate=form.dday.data)
            db.session.add(a)
            db.session.commit()
        return render_template("admin/distassignments.html", form=form)
    elif check == 0:
        return redirect(url_for('udash'))
    else:
        return redirect(url_for('login'))
#done
@app.route('/createtimedassignment', methods=['GET', 'POST'])
def createtimedassignment():
    check = check_user()
    if check == 1:
        form = SetTimedAssignment()
        times = [i[0] for i in db.session.query(Events.eventTime).filter(Events.eventTime!=0).all()]
        timeMS = []
        #changes time into MM:SS format
        for time in times:
            min = time//60
            sec = time - (min*60)
            if len(str(sec)) == 1:
                sec = "0"+str(sec)
            elif len(str(sec)) == 2:
                sec = str(sec)
            digtime = str(min) + ":" + sec
            timeMS.append(digtime)
        form.eventTime.choices = timeMS
        if form.validate_on_submit():
            time = form.eventTime.data
            times = [int(i) for i in time.split(":")]
            typeid = int(EventTypes.query.filter_by(type=str(form.eventType.data)).first().id)
            timeinS = times[0]*60 + times[1]
            eventid = int(Events.query.filter_by(eventTypeID=typeid, eventTime=timeinS).first().eventID)
            a = ScheduledAssignments(classID=session["current_classid"], eventID=eventid, returnDate=form.dday.data)
            db.session.add(a)
            db.session.commit()
        return render_template("admin/timeassignments.html", form=form)
    elif check == 0:
        return redirect(url_for('udash'))
    else:
        return redirect(url_for('login'))
#done but could format it better
@app.route('/submitassignment', methods=['GET', 'POST'])
def submitassignment():
    check = check_user()
    error = ' '
    if check == 0:
        assign = []
        form = SelectAssignment()
        headings = ['Assignment ID', 'Event Type', 'Event Distance', 'Event Time', 'Due Date']
        assignment = [list(i) for i in db.session.query(ScheduledAssignments.assignmentID, EventTypes.type, Events.eventDistance, Events.eventTime, ScheduledAssignments.returnDate).select_from(EventTypes).join(Events).join(ScheduledAssignments).all()]
        count = 1
        if form.validate_on_submit():
            session["isAssignment"] = 1
            session["current_assignmentid"] = form.assignmentID.data
            in_db = db.session.query(ReturnedAssignment.rassid).select_from(ReturnedAssignment).join(UserDST).join(ScheduledAssignments).filter(UserDST.userID==current_user.id, ReturnedAssignment.schassid==form.assignmentID.data).first()
            if in_db is None:
                return redirect(url_for('enterassignment'))
            else:
                error = "You have already submitted this assignment."
        return render_template('user/assignments.html', headings=headings, assignments=assignment, form=form, assign=1, error=error)
    else:
        return redirect(url_for('login'))
#done
@app.route('/enterassignment', methods=['GET', 'POST'])
def enterassignment():
    userSpeed = 0
    now = datetime.now()
    check = check_user()
    if check == 0:
        form = SubmitAssignment()
        assign = 0
        if session["isAssignment"] == 1:
            assid = session["current_assignmentid"]
            eventID = [i for i in db.session.query(ScheduledAssignments.eventID).filter(ScheduledAssignments.assignmentID==assid).first()][0]
            event = [i for i in db.session.query(EventTypes.type, Events.eventDistance, Events.eventTime).select_from(EventTypes).join(Events).filter(Events.eventID == eventID).first()]
            form.eventType.choices = [event[0]]
            form.eventDistance.choices = [event[1]]
            form.eventTime.choices = [event[2]]
            if event[1] == 0:
                form.userTimeM.data = event[2]//60
                form.userTimeS.data = event[2]%60
            elif event[2] == 0:
                form.userDistance.data = event[1]
        if form.addInterval.data:
            form.userInterval.append_entry()
            return render_template("user/submitassignment.html", form=form)
        if form.validate_on_submit():
            if session["isAssignment"] == 1:
                time = int(form.userTimeM.data)*60 + int(form.userTimeS.data)
                speed = 0
                speed = getspeed(time, form.userDistance.data, speed)
                typeid = int(EventTypes.query.filter_by(type=str(form.eventType.data)).first().id)
                eventid = int(Events.query.filter_by(eventTypeID=typeid, eventDistance=event[1], eventTime=event[2]).first().eventID)
                userdst = UserDST(userID=current_user.id, eventID=eventid, userDistance=form.userDistance.data, userTime=time , userSpeed=speed, isAssignment=1)
                db.session.add(userdst)
                db.session.commit()
                userdstid = userdst.userDSTID
                assignment = ReturnedAssignment(schassid=session["current_assignmentid"], userdstid=userdstid, isLate=0)
                db.session.add(assignment)
                db.session.commit()
                intervals(current_user.id, form.userInterval.data, userdstid)
                session["isAssignment"] == 0
    return render_template("user/submitassignment.html", form=form)

def returnname(ids):
    names = []
    for i in ids:
        name = [str(i[0])+" "+str(i[1]) for i in db.session.query(Users.firstname, Users.lastname).filter_by(id = i)]
        names.append(name[0])
    return names

def returnid(names):
    namelist = [i.split(' ') for i in names]
    ids = []
    for i in namelist:
        id = [i for i in db.session.query(Users.id).filter_by(firstname=i[0], lastname=i[1]).first()]
        ids.append(id[0])
    return ids
#done
@app.route('/viewsetassignments', methods=['GET', 'POST'])
def viewsetassignments():
    check = check_user()
    if check == 1:
        form = ReviewAssignment()
        assignments = []
        session["review_assignment"] = 0
        #get ids of students in class
        #get those ids and get their names
        error = ' '
        form.user.choices = get_student_names()
        assignments = []
        assignment_query = db.session.query(ScheduledAssignments.assignmentID, ScheduledAssignments.eventID, ScheduledAssignments.scheduledDate, ScheduledAssignments.returnDate).filter_by(classID = session["current_classid"])
        for i in assignment_query:
            eventdetails = db.session.query(Events.eventDistance, Events.eventTime).filter_by(eventID = int(i[1])).first()
            eventtypeID = [i for i in db.session.query(Events.eventTypeID).filter_by(eventID = int(i[1])).first()][0]
            eventtypes = []
            eventtype = [i for i in db.session.query(EventTypes.type).filter_by(id = eventtypeID).first()][0]
            eventtypes.append(eventtype[0])
            num_of_people = len(list(ReturnedAssignment.query.filter_by(schassid = i.assignmentID)))
            assid = i.assignmentID
            eventid = i.eventID
            scheduled = (str(i.scheduledDate).split(" "))[0]
            returndate = i.returnDate
            dist = eventdetails.eventDistance
            time = eventdetails.eventTime
            assignment = (assid, eventid, scheduled, returndate, eventtype, dist, time, num_of_people)
            assignments.append(assignment)
        headings = ('Assignment ID', 'Event ID', 'Set Date', 'Due Date', 'Event Type', 'Event Distance', 'Event Time', 'Handed In')
        if form.validate_on_submit():
            fullname = (form.user.data).split(" ")
            id = [i for i in db.session.query(Users.id).filter_by(firstname = fullname[0], lastname = fullname[1]).first()][0]
            assignment = db.session.query(ReturnedAssignment.userdstid).select_from(UserDST).join(ReturnedAssignment).join(Users).filter(UserDST.userID == id, ReturnedAssignment.schassid == form.id.data).first()
            if assignment is None:
                error = 'The user has not submitted this assignment.'
            else:
                global dstid
                session["review_assignment"] = [i for i in assignment][0]
                dstid = [i for i in assignment][0]
                return redirect(url_for('reviewdata'))
    return render_template("admin/schassignment.html", assignments=assignments, headings=headings, form=form, error = error)


dstid = 0
studentname = ''

@app.route('/data', methods=['GET', 'POST'])
def data():
    check = check_user()
    headings = ('ID', 'Date', 'Distance (m)', 'Time (s)', 'Speed (m/s)', 'AssignmentID')
    global dstid
    form = ChooseDSTID()
    if check == 0:
        userID = current_user.id
    if check == 1:
        userID = (returnid([session["review_student_name"]]))[0]
    userdst = [list(i) for i in db.session.query(UserDST.userDSTID, UserDST.dstDateTime, UserDST.userDistance, UserDST.userTime, UserDST.userSpeed).filter_by(userID=userID).all()]
    for i in userdst:
        assignmentID = db.session.query(ReturnedAssignment.schassid).filter(ReturnedAssignment.userdstid==i[0]).first()
        if assignmentID is None:
            i.append(' ')
        else:
            i.append(assignmentID[0])
    if form.review.data:
        dstid = form.id.data
        return redirect(url_for('reviewdata'))
    if form.edit.data:
        dstid = form.id.data
        return redirect(url_for('editdata'))
    return render_template("data.html", headings=headings, data=userdst, form=form, user=check, student=session["review_student_name"])

@app.route('/choosestudent', methods=['GET', 'POST'])
def choosestudent():
    check = check_user()
    if check == 1:
        session["review_student_name"] = None
        form = ChooseStudent()
        ids = [i[0] for i in db.session.query(ClassesUsers.usersID).filter_by(classID = session['current_classid'])]
        form.user.choices = returnname(ids)
        if form.validate_on_submit:
            session["review_student_name"] = form.user.data
            return redirect(url_for('data'))
        return render_template("admin/choosestudent.html", form=form)
    elif check == 0:
        return redirect(url_for('udash'))

#done
@app.route('/editdata', methods=['GET', 'POST'])
def editdata():
    check = check_user()
    global dstid
    eventtype = []
    eventdist = []
    id = dstid
    speed = 0
    eventID = [i for i in db.session.query(UserDST.eventID).filter_by(userDSTID=id).first()][0]
    event = [i for i in db.session.query(EventTypes.type, Events.eventDistance, Events.eventTime).select_from(EventTypes).join(Events).filter(Events.eventID == eventID).first()]
    timeMS = []
    for time in [event[2]]:
        min = time//60
        sec = time - (min*60)
        if len(str(sec)) == 1:
            sec = "0"+str(sec)
        elif len(str(sec)) == 2:
            sec = str(sec)
        digtime = str(min) + ":" + sec
        timeMS.append(digtime)
    time = list(db.session.query(UserDST.userTime).filter_by(userDSTID=dstid).first())[0]
    usertimeM = time//60
    usertimeS = time - usertimeM*60
    dstdetails = UserDST.query.filter_by(userDSTID=id).first()
    if check == 0:
        form = SubmitAssignment()
        form.eventType.choices = [event[0]]
        form.eventDistance.choices = [event[1]]
        form.eventTime.choices = timeMS
        if form.validate_on_submit():
            speed = 0
            typeid = int(EventTypes.query.filter_by(type=str(form.eventType.data)).first().id)
            eventid = int(Events.query.filter_by(eventTypeID=typeid, eventDistance=int(str(form.eventDistance.data))).first().eventID)
            updatedtime = form.userTimeM.data*60 + form.userTimeS.data
            speed = getspeed(updatedtime, form.eventDistance.data, speed)
            userdstid = UserDST.query.filter_by(userDSTID=id).first()
            dstdetails.eventID = eventID
            dstdetails.userDistance = int(str(form.eventDistance.data))
            dstdetails.userTime = updatedtime
            dstdetails.userSpeed = speed
            db.session.commit()
            return redirect(url_for('data'))
        elif request.method == 'GET':
            form.userTimeM.data = usertimeM
            form.userTimeS.data = usertimeS
            form.userDistance.data = dstdetails.userDistance
        return render_template("user/submitassignment.html", form=form, timeM=usertimeM, timeS=usertimeS, assign=0)
    elif check == 1:
        form = AdminEditData()
        dstdetails = UserDST.query.filter(UserDST.userDSTID==dstid).first()
        classuserids = [i[0] for i in db.session.query(ClassesUsers.usersID).filter(ClassesUsers.classID==session["current_classid"]).all()]
        form.user.choices = returnname(classuserids)
        form.eventType.choices = [event[0]]
        form.eventDistance.choices = [event[1]]
        form.eventTime.choices = timeMS
        if form.validate_on_submit():
            typeid = int(EventTypes.query.filter_by(type=str(form.eventType.data)).first().id)
            eventid = int(Events.query.filter_by(eventTypeID=typeid, eventDistance=int(str(form.eventDistance.data))).first().eventID)
            updatedtime = int(form.userTimeM.data)*60 + int(form.userTimeS.data)
            speed = getspeed(updatedtime, form.eventDistance.data, speed)
            name = (form.user.data).split(' ')
            userID =  [i for i in db.session.query(Users.id).filter(Users.firstname==name[0], Users.lastname==name[1]).first()][0]
            dstdetails.userID = userID
            dstdetails.eventID = eventID
            dstdetails.userDistance = int(str(form.eventDistance.data))
            dstdetails.userTime = updatedtime
            dstdetails.userSpeed = speed
            db.session.commit()
            return redirect(url_for('data'))
        elif request.method == 'GET':
            form.userTimeM.data = usertimeM
            form.userTimeS.data = usertimeS
            form.userDistance.data = dstdetails.userDistance
        return render_template("admin/admineditdata.html", form=form, usertimeM=usertimeM, usertimeS=usertimeS)


@app.route('/reviewdata', methods=['GET', 'POST'])
def reviewdata():
    global dstid
    check = check_user()
    details = []
    dst_details = UserDST.query.filter_by(userDSTID = dstid).first()
    event = [i for i in db.session.query(EventTypes.type, Events.eventDistance, Events.eventTime).select_from(EventTypes).join(Events).filter(Events.eventID == dst_details.eventID).first()]
    labels = [i[0] for i in db.session.query(Intervals.time).filter_by(userdstid=dstid).all()]
    values = [i[0] for i in db.session.query(Intervals.dist).filter_by(userdstid=dstid).all()]
    speeds = []
    for i in range(0,len(labels)):
        speed = 0
        speed = getspeed(labels[i], values[i], speed)
        speeds.append(speed)
    if check == 0:
        details.append(' ')
    elif check == 1:
        userid = [dst_details.userID]
        details = []
        details.append((returnname(userid))[0])
    details.append(event[0])
    details.append(event[1])
    details.append(dst_details.userDistance)
    details.append(event[2])
    details.append(dst_details.userTime)
    details.append(dst_details.userSpeed)
    no_intervals = False
    if len(labels) == 0 and len(values)==0:
        no_intervals = True
    return render_template("reviewdata.html", user=check, labels=labels, values=values, speed=speeds, details=details, no_intervals=no_intervals)

review_event = ' '
#filtering through events
@app.route('/chooseeventdata', methods=['GET', 'POST'])
def chooseeventdata():
    global review_event
    global error
    check = check_user()
    form = CheckEventData()
    eventdist = [i[0] for i in db.session.query(Events.eventDistance).filter(Events.eventDistance!=0)]
    form.eventdist.choices = [0] + eventdist
    times = [i[0] for i in db.session.query(Events.eventTime).filter(Events.eventTime!=0)]
    timeMS = []
    #changes time into MM:SS format
    for time in times:
        min = time//60
        sec = time - (min*60)
        if len(str(sec)) == 1:
            sec = "0"+str(sec)
        elif len(str(sec)) == 2:
            sec = str(sec)
        digtime = str(min) + ":" + sec
        timeMS.append(digtime)
    form.eventtime.choices = [0] + timeMS
    if form.validate_on_submit():
        global review_event
        event = ' '
        error = ' '
        type = str(form.eventtype.data)
        dist = int(form.eventdist.data)
        time = form.eventtime.data
        if form.eventdist.data == 0 and form.eventtime.data == 0:
            error = 'You can only enter data in the distance or time dropdowns'
        elif int(form.eventdist.data) != 0 and str(form.eventtime.data) != '0':
            error = 'You can only enter data in the distance or time dropdowns'
        elif int(form.eventdist.data) != 0 and str(form.eventtime.data) == '0':
            update_event(form.eventtype.data, form.eventdist.data)
        elif int(form.eventdist.data) == 0 and str(form.eventtime.data) != '0':
            update_event(form.eventtype.data, form.eventtime.data)
        return redirect(url_for('alldata'))
    return render_template("datachooseevent.html", user=check, form=form, error=error)
error = ''
#all data for a specific event and forecast
@app.route('/alldata', methods=['GET', 'POST'])
def alldata():
    current_event = return_event()
    values = []
    is_time = 0
    global error
    check = check_user()
    userID = 0
    if check == 0:
        userID = current_user.id
    elif check == 1:
        name = [str(session["review_student_name"])]
        userID = (returnid(name))[0]
    event = current_event
    eventdetails = event.split(' ')
    eventid = 0
    typeid = db.session.query(EventTypes.id).filter_by(type=str(eventdetails[0])).first()
    typeid = [int(i) for i in typeid][0]
    if ':' not in eventdetails[1]:
        eventid = int(Events.query.filter_by(eventTypeID=typeid, eventDistance=int(eventdetails[1])).first().eventID)
        is_time = False
    else:
        time = eventdetails[1]
        times = [int(i) for i in time.split(":")]
        timeinS = times[0]*60 + times[1]
        eventid = int(Events.query.filter_by(eventTypeID=typeid, eventTime=timeinS).first().eventID)
        is_time = True
    if eventid is None:
        error = 'There is no such event'
        return redirect(url_for('chooseeventdata'))
    if is_time == False:
        values = [i[0] for i in db.session.query(UserDST.userTime).filter_by(userID=userID, eventID=eventid).all()]
    elif is_time == True:
        values = [i[0] for i in db.session.query(UserDST.userDistance).filter_by(userID=userID, eventID=eventid).all()]
    firstdate = [i for i in db.session.query(UserDST.dstDateTime).filter_by(userID=userID, eventID=eventid).first()]
    days = []
    date = [str(i[0].day)+'-'+str(i[0].month)+'-'+str(i[0].year) for i in db.session.query(UserDST.dstDateTime).filter_by(userID=userID, eventID=eventid).all()]
    dates = [i for i in db.session.query(UserDST.dstDateTime).filter_by(userID=userID, eventID=eventid).all()]
    for i in dates:
        date_object = ([j for j in i][0]).date()
        day = str(date_object - (firstdate[0]).date())
        if day == '0:00:00':
            day = 0
        else:
            day = int((day.split())[0])
        days.append(day)
    x_array = []
    for i in days:
        n = []
        n.append(i)
        x_array.append(n)
    x = np.array(x_array)
    reg = LinearRegression().fit(x, values)
    new_val = days[-1] + 2
    intercept = reg.intercept_
    slope = reg.coef_
    final_y = slope*days[-1] + intercept
    trendy = []
    for i in days:
        trend = []
        trend.append(slope*i + intercept)
        trendy.append(trend[0][0])
    recentdate = (list([i for i in db.session.query(UserDST.dstDateTime).filter_by(userID=userID, eventID=eventid).all()][-1]))[0]
    predicted_date = recentdate + timedelta(days=2)
    pd = str(predicted_date.day)+'-'+str(predicted_date.month)+'-'+str(predicted_date.year)
    date.append(pd)
    pd1 = "16-12-2021"
    pdy = reg.predict(np.array([[new_val]]))
    pdy_list = []
    for i in range(0, len(date)):
        if i == len(date)-1:
            pdy_list.append(pdy[0])
        else:
            pdy_list.append(None)
    pdy_list = json.dumps(pdy_list)
    return render_template("alldata.html", user=check, labels=date, values=values, pdy=pdy_list)

#done
@app.route('/profile', methods=['GET', 'POST'])
def profile():
    form = Profile()
    if form.validate_on_submit():
        user = Users.query.filter_by(id=current_user.id).first()
        user.firstname = form.fname.data
        user.lastname = form.lname.data
        user.email = form.email.data
        user.about = form.about.data
        db.session.commit()
        print(user.about)
        return redirect(url_for('profile'))
    elif request.method == 'GET':
        form.fname.data = current_user.firstname
        form.lname.data = current_user.lastname
        form.email.data = current_user.email
        form.about.data = current_user.about
    return render_template("editprofile.html", form=form)

#done
def send_rp_email(user):
    token = user.get_token()
    mess = Message('Password Reset Request', sender="timemeapp@gmail.com", recipients=[user.email])
    mess.body = f'''This email has been sent since you want to reset your password.
If you did not request to reset your password, please ignore this email.
{url_for('reset_token', token=token, _external=True)}'''
    mail.send(mess)
#done
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
#done
@app.route('/resetpass/<token>', methods=['GET', 'POST'])
def reset_token(token):
    check = check_user()
    form = ResetPass()
    if current_user.is_authenticated:
        if check == 1:
            return redirect(url_for('index'))
    user = Users.verify_token(token)
    if user is None:
        flash('Invalid token', 'warning')
        return redirect(url_for('reset_request'))
    if form.validate_on_submit():
        hashed_pass = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user.password = hashed_pass
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('resetpass.html', form=form)

current_event = " "
def update_event(type, param):
    global current_event
    current_event = str(type) + " " + str(param)
    return current_event

def return_event():
    return current_event
#choose event before stopwatch
@app.route('/chooseevent', methods=['GET', 'POST'])
def chooseevent():
    check = check_user()
    form = ChooseEvent()
    error = ' '
    form.eventDistance.choices = [i[0] for i in db.session.query(Events.eventDistance).filter(Events.eventDistance!=0)]
    if check == 1:
        if form.validate_on_submit():
            if form.submit.data:
                eventid = db.session.query(Events.eventID).select_from(Events).join(EventTypes).filter(Events.eventDistance==int(form.eventDistance.data), EventTypes.type==str(form.eventType.data)).first()
                if eventid != None:
                    update_event(form.eventType.data, form.eventDistance.data)
                    return_event()
                    return redirect(url_for('stopwatch'))
                elif eventid is None:
                    error = 'There is no such event'
                    return render_template("chooseevent.html", form=form, user=check, error=error)
        return render_template("chooseevent.html", form=form, user=check, error=error)
    if check == 0:
        if form.validate_on_submit():
            if form.submit.data:
                update_event(form.eventType.data, form.eventDistance.data)
                return_event()
                return redirect(url_for('stopwatch'))
        return render_template("chooseevent.html", form=form, user=check, error=error)


starttime = "00:00:00"
def update_starttime():
    global starttime
    starttime = datetime.now()

def return_starttime():
    global starttime
    return starttime

def reset_starttime():
    global starttime
    starttime = "00:00:00"

seconds = -1
def get_current_time():
    global seconds
    seconds += 1
    remaining_seconds = seconds%60
    minutes = seconds//60
    hours = seconds//3600
    stopwatch_format = "{:02}:{:02}:{:02}".format(hours, minutes, remaining_seconds)
    return stopwatch_format

@app.route('/stopwatch_start', methods=['GET', 'POST'])
def stopwatch_start():
    seconds = 0
    return """<h1>
    <meta http-equiv="refresh" content="1" />{}</h1>""".format(get_current_time())

@app.route('/stopwatch_reset', methods=['GET', 'POST'])
def stopwatch_reset():
    global seconds
    seconds = 0
    return """<h1>00:00:00</h1>"""

#done
def addtime(users):
    check = check_user()
    event = return_event().split(" ")
    type = event[0]
    dist = event[1]
    user = users
    check = check_user()
    for i in range(0,len(users)):
        userlist = [j[1] for j in user[i].items()]
        times = userlist[1].split(':')
        name = (str(userlist[0]).split(' '))
        if '' in name:
            name = name.remove('')
        time = int(times[0])*3600 + int(times[1])*60 + int(times[2])
        userSpeed = 0
        userSpeed = getspeed(time, str(dist), userSpeed)
        typeid = int(EventTypes.query.filter_by(type=str(type)).first().id)
        eventid = int(Events.query.filter_by(eventTypeID=typeid, eventDistance=int(dist)).first().eventID)
        userid = [i for i in db.session.query(Users.id).filter(Users.firstname==name[0], Users.lastname==name[1]).first()][0]
        userdst = UserDST(userID=userid, eventID=eventid, userDistance=dist, userTime=time , userSpeed=userSpeed, isAssignment=0)
        db.session.add(userdst)
        db.session.commit()

#done
@app.route('/stopwatch', methods=['GET', 'POST'])
def stopwatch():
    check = check_user()
    event = return_event().split(" ")
    user_query = Users.query.filter(Users.isAdmin!=1)
    form = Stopwatch()
    date = (str(datetime.today()).split(' '))[0]
    ids = [i[0] for i in db.session.query(ClassesUsers.usersID).filter(ClassesUsers.classID==session['current_classid'])]
    names = returnname(ids)
    type = event[0]
    distance = event[1]
    form.users.choices = names
    if form.start.data:
        update_starttime()
        pass
    elif form.store.data:
        starttime = return_starttime()

        if starttime != "00:00:00":
            time = str(datetime.now() - starttime).split('.')[0]
        else:
            time = starttime

        form.users.append_entry(
            {
                "time": time,
                "users": QuerySelectField('Name', query_factory=user_query, validators=[DataRequired()])
            }
        )
        return render_template("stopwatch.html", form=form, starttime=starttime, user=check, date=date, type=type, distance=distance,)
    elif form.reset.data:
        reset_starttime()
    if form.submit.data:
        users = form.users.data
        addtime(users)
    return render_template("stopwatch.html", form=form, date=date, type=type, distance=distance, user=check)

present = []

@app.route('/register', methods=['GET', 'POST'])
def takeregister():
    global present
    form = UserReg()
    if form.addUser.data:
        form.user.append_entry()
        return render_template("admin/register.html", form=form)
    if form.submit.data:
        newreg = Registers(classID=session["current_classid"])
        db.session.add(newreg)
        db.session.commit()
        for i in form.user.data:
            if i['userReg'] is not None:
                present.append(str(i['userReg']))
                name = str(i['userReg']).split(' ')
                fname, lname = name[0], name[1]
                userid = int(Users.query.filter_by(firstname=fname, lastname=lname).first().id)
                regid = int(Registers.query.filter_by(classID=session["current_classid"]).all()[-1].regid)
                newreg = RegPresent(regid=regid, userid=userid, isPresent=1)
                db.session.add(newreg)
        db.session.commit()
        if form.submit.data:
            return redirect(url_for('adash'))
    return render_template("admin/register.html", form=form)
#viewing registers all at once
@app.route('/viewregisters', methods=['GET', 'POST'])
def viewregister():
    check = check_user()
    if check == 1:
        form = ReviewRegisters()
        classregs = db.session.query(Registers.regid, Registers.date).filter_by(classID = session["current_classid"]).all()
        headings = ('Register ID', 'Date')
        if form.validate_on_submit():
            session['regid'] = form.regID.data
            return redirect(url_for('reviewregister'))
        return render_template("admin/viewregister.html", headings=headings, user=check, data=classregs, form=form)
    elif check == 0:
        return redirect(url_for('udash'))
    elif check == 2:
        return redirect(url_for('login'))
#done
#viewing the names in a register
@app.route('/reviewregister', methods=['GET', 'POST'])
def reviewregister():
    check = check_user()
    regid = session['regid']
    headings = ('First Name', 'Last Name')
    inreg = [i[0] for i in db.session.query(RegPresent.userid).filter_by(regid  = regid)]
    firstname = []
    lastname = []
    data = []
    for i in inreg:
        fname = [str(i[0]) for i in db.session.query(Users.firstname).filter_by(id = i)]
        lname = [str(i[0]) for i in db.session.query(Users.lastname).filter_by(id = i)]
        firstname.append(fname)
        lastname.append(lname)
    for i in range(0, len(firstname)):
        data.append([firstname[i], lastname[i]])
    return render_template("admin/reviewregisters.html", user=check, headings=headings, data=data)
