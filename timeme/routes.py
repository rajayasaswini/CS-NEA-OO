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

#session["present"] = []
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
@app.route('/enterdata', methods=['GET', 'POST'])
def enterdata():
    userSpeed = 0
    now = datetime.now()
    check = check_user()
    if check == 0:
        form = UserEnterData()
        assign = 0
        if form.addInterval.data:
            form.userInterval.append_entry()
            return render_template("user/userenterdata.html", form=form)
        if form.validate_on_submit():
            time = int(form.userTimeM.data)*60 + int(form.userTimeS.data)
            userSpeed = getspeed(time, str(form.eventDistance.data), userSpeed)
            dist = str(form.eventDistance.data)
            dist = int(dist)
            typeid = int(EventTypes.query.filter_by(type=str(form.eventType.data)).first().id)
            eventid = int(Events.query.filter_by(eventTypeID=typeid, eventDistance=int(str(form.eventDistance.data))).first().eventID)
            userdst = UserDST(userID=current_user.id, eventID=eventid, userDistance=dist, userTime=time , userSpeed=userSpeed, isAssignment=assign)
            db.session.add(userdst)
            db.session.commit()
            dstid = int(UserDST.query.filter_by(userID=current_user.id).all()[-1].userDSTID)
            intervals(current_user.id, form.userInterval.data, dstid)
        return render_template("user/userenterdata.html", form=form)

    elif check == 1:
        form = AdminEnterData()
        if form.addInterval.data:
            form.userInterval.append_entry()
            return render_template("user/userenterdata.html", form=form)
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
        return render_template("admin/adminenterdata.html", form=form)
    else:
        return redirect(url_for('login'))
#done
@app.route('/enterdist', methods=['GET', 'POST'])
def enterdist():
    userSpeed = 0
    now = datetime.now()
    check = check_user()
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
            #time = int(form.userTimeM.data)*60 + int(form.userTimeS.data)
            userSpeed = getspeed(timeinS, str(form.eventDistance.data), userSpeed)
            dist = str(form.eventDistance.data)
            #dist = int(dist)
            typeid = int(EventTypes.query.filter_by(type=str(form.eventType.data)).first().id)
            eventid = int(Events.query.filter_by(eventTypeID=typeid, eventTime=timeinS).first().eventID)
            print(typeid, eventid)
            userdst = UserDST(userID=current_user.id, eventID=eventid, userDistance=dist, userTime=timeinS , userSpeed=userSpeed, isAssignment=assign)
            db.session.add(userdst)
            db.session.commit()
            dstid = int(UserDST.query.filter_by(userID=current_user.id).all()[-1].userDSTID)
            intervals(current_user.id, form.userInterval.data, dstid)
        return render_template("user/userenterdist.html", form=form)
    elif check == 1:
        form = AdminEnterDist()
        if form.addInterval.data:
            form.userInterval.append_entry()
            return render_template("admin/adminenterdata.html", form=form)
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
            userSpeed = 0
            time = form.userTime.data
            times = [int(i) for i in time.split(":")]
            timeinS = times[0]*60 + times[1]
            userSpeed = getspeed(timeinS, str(form.eventDistance.data), userSpeed)
            dist = str(form.eventDistance.data)
            typeid = int(EventTypes.query.filter_by(type=str(form.eventType.data)).first().id)
            eventid = int(Events.query.filter_by(eventTypeID=typeid, eventTime=timeinS).first().eventID)
            userdst = UserDST(userID=current_user.id, eventID=eventid, userDistance=dist, userTime=timeinS , userSpeed=userSpeed, isAssignment=0)
            db.session.add(userdst)
            db.session.commit()
            dstid = int(UserDST.query.filter_by(userID=userid).all()[-1].userDSTID)
            intervals(current_user.id, form.userInterval.data, dstid)
        return render_template("admin/adminenterdata.html", form=form)
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
@app.route('/assignment', methods=['GET', 'POST'])
def submitassignment():
    check = check_user()
    if check == 0:
        assign = []
        form = SelectAssignment()
        headings = ['Event Type', 'Event Distance', 'Due Date']
        assignment = list(db.session.query(EventTypes.type, Events.eventDistance, ScheduledAssignments.returnDate).select_from(EventTypes).join(Events).join(ScheduledAssignments).all())
        form.assignmentname.choices = assignment
        count = 1
        for type, event, assign in assignment:
            schass = [str(count), str(type) + " "  + str(event) + " " + str(assign)]
            schass2 = [i for i in schass]
            schass3 = [i.split() for i in schass]
            schass4 = [schass[1]]
        if form.validate_on_submit():
            session["isAssignment"] = 1
            assignment1 = form.assignmentname.data
            type = assignment[1][0]
            event = assignment[1][1]
            assign = assignment[1][2]
            assignmentlist = [type, str(event), str(assign)]
            session["current_assignment"] = assignmentlist
            typeid = int(EventTypes.query.filter_by(type=assignmentlist[0]).first().id)
            eventid = int(Events.query.filter_by(eventTypeID=typeid, eventDistance=assignmentlist[1]).first().eventID)
            session["current_assignmentid"] = ScheduledAssignments.query.filter_by(classID=session["current_classid"], eventID=eventid, returnDate=str(assignmentlist[2])).first().assignmentID
            return redirect(url_for('enterassignment'))
        return render_template('user/assignments.html', headings=headings, assignments=assignment, form=form)
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
            assign = 1
            details = session["current_assignment"]
            eventtype_list= []
            eventdist_list = []
            temp = (1, details[0])
            eventtype_list.append(temp)
            temp = (1, details[1])
            eventdist_list.append(temp)
            form.eventType.choices = eventtype_list
            form.eventDistance.choices = eventdist_list
        if form.validate_on_submit():
            if session["isAssignment"] == 1:
                assign = 1
                details = session["current_assignment"]
                time = int(form.userTimeM.data)*60 + int(form.userTimeS.data)
                typeid = int(EventTypes.query.filter_by(type=details[0]).first().id)
                eventid = int(Events.query.filter_by(eventTypeID=typeid, eventDistance=details[1]).first().eventID)
                userdst = UserDST(userID=current_user.id, eventID=eventid, userDistance=int(details[1]), userTime=time , userSpeed=0.1, isAssignment=assign)
                print(session["isAssignment"], session["current_assignment"])
            db.session.add(userdst)
            db.session.commit()
            if session["isAssignment"] == 1:
                userdstid = userdst.userDSTID
                assignment = ReturnedAssignment(schassid=session["current_assignmentid"], userdstid=userdstid, isLate=0)
                db.session.add(assignment)
                db.session.commit()
                session["isAssignment"] == 0
                session["current_assignment"] = None
            print(session["isAssignment"], session["current_assignment"])
    return render_template("user/userenterdata.html", form=form)
#not done
dstid = 0
@app.route('/data', methods=['GET', 'POST'])
def data():
    check = check_user()
    if check == 0:
        global dstid
        form = EditData()
        headings = ('ID', 'Date', 'Distance', 'Time', 'Speed')
        userdst = list(db.session.query(UserDST.userDSTID, UserDST.dstDateTime, UserDST.userDistance, UserDST.userTime, UserDST.userSpeed).filter_by(userID=current_user.id).all())
        if form.review.data:
            dstid = form.id.data
            return redirect(url_for('reviewdata'))
        if form.edit.data:
            dstid = form.id.data
            return redirect(url_for('editdata'))
        return render_template("data.html", headings=headings, data=userdst, form=form, user=check)
#only done for user
@app.route('/editdata', methods=['GET', 'POST'])
def editdata():
    check = check_user()
    if check == 0:
        global dstid
        form = SubmitAssignment()
        eventtype = []
        eventdist = []
        id = dstid
        eventID = db.session.query(UserDST.eventID).filter_by(userDSTID=id).first()
        eventdetails = list(db.session.query(Events.eventTypeID, Events.eventDistance).first())
        #print(eventdetails)
        eventtype = db.session.query(EventTypes.type).filter_by(id=eventdetails[0]).first()
        type = [str(i) for i in eventtype]
        distance = [str(eventdetails[1])]
        #print(eventtype[0])
        form.eventType.choices = type
        form.eventDistance.choices = distance
        time = list(db.session.query(UserDST.userTime).filter_by(userDSTID=dstid).first())[0]
        timeM = time//60
        timeS = time - timeM*60
        #dstdetails = db.session.query(UserDST.eventID, UserDST.userDistance, UserDST.userTime, UserDST.userSpeed).filter(UserDST.userDSTID==1).first()
        dstdetails = UserDST.query.filter(UserDST.userDSTID==dstid)
        if form.validate_on_submit():
            typeid = int(EventTypes.query.filter_by(type=str(form.eventType.data)).first().id)
            eventid = int(Events.query.filter_by(eventTypeID=typeid, eventDistance=int(str(form.eventDistance.data))).first().eventID)
            #dstdetails.eventID = eventID
            #dstdetails.userDistance = int(str(form.userDistance.data))
            updatedtime = form.userTimeM.data*60 + form.userTimeS.data
            #dstdetails.userTime = updatedtime
            speed = 0
            speed = getspeed(updatedtime, form.eventDistance.data, speed)
            #dstdetails.userSpeed = speed
            dstdetails.update({
                "eventID": eventid,
                "userDistance": int(str(form.eventDistance.data)),
                "userTime": updatedtime,
                "userSpeed": speed
            })
            db.session.commit()
        return render_template("user/usereditdata.html", form=form, timeM=timeM, timeS=timeS)

@app.route('/reviewdata', methods=['GET', 'POST'])
def reviewdata():
    global dstid
    check = check_user()
    if check == 0:
        print(dstid)
        labels = [i[0] for i in db.session.query(Intervals.time).filter_by(userdstid=11).all()]
        values = [i[0] for i in db.session.query(Intervals.dist).filter_by(userdstid=11).all()]
        values2 = [2,2,2,2,2,2,2,2,2,2]
        speeds = []
        for i in range(0,len(labels)):
            speed = 0
            speed = getspeed(labels[i], values[i], speed)
            speeds.append(speed)
        return render_template("reviewdata.html", user=check, labels=labels, values=values, speed=speeds)
    elif check == 1:
        return render_template("reviewdata.html", user=check)
event = ' '
@app.route('/chooseeventdata', methods=['GET', 'POST'])
def chooseeventdata():
    global event
    check = check_user()
    if check == 0:
        form = UserCheckEventData()
        if form.validate_on_submit():
            event = str(form.eventtype.data) + ' ' + str(form.eventdist.data)
            return redirect(url_for('alldata'))
        return render_template("datachooseevent.html", user=check, form=form)
    elif check == 1:
        return render_template("datachooseevent.html", user=check)

@app.route('/alldata', methods=['GET', 'POST'])
def alldata():
    global event
    check = check_user()
    if check == 0:
        eventdetails = event.split(' ')
        typeid = (list(db.session.query(EventTypes.id).filter_by(type=str(eventdetails[0])).first()))[0]
        eventid = int(Events.query.filter_by(eventTypeID=typeid, eventDistance=str(eventdetails[1])).first().eventID)
        time = [i[0] for i in db.session.query(UserDST.userTime).filter_by(userID=current_user.id, eventID=eventid).all()]
        firstdate = [i for i in db.session.query(UserDST.dstDateTime).filter_by(userID=current_user.id, eventID=eventid).first()]
        days = []
        date = [str(i[0].day)+'-'+str(i[0].month)+'-'+str(i[0].year) for i in db.session.query(UserDST.dstDateTime).filter_by(userID=current_user.id, eventID=eventid).all()]
        dates = [i for i in db.session.query(UserDST.dstDateTime).filter_by(userID=current_user.id, eventID=eventid).all()]
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
        reg = LinearRegression().fit(x, time)
        new_val = days[-1] + 2
        intercept = reg.intercept_
        slope = reg.coef_
        final_y = slope*days[-1] + intercept
        trendy = []
        for i in days:
            trend = []
            trend.append(slope*i + intercept)
            trendy.append(trend[0][0])
        recentdate = (list([i for i in db.session.query(UserDST.dstDateTime).filter_by(userID=current_user.id, eventID=eventid).all()][-1]))[0]
        predicted_date = recentdate + timedelta(days=2)
        pd = str(predicted_date.day)+'-'+str(predicted_date.month)+'-'+str(predicted_date.year)
        date.append(pd)
        print(pd)
        pd1 = "16-12-2021"
        pdy = reg.predict(np.array([[new_val]]))
        pdy_list = []
        for i in range(0, len(date)):
            if i == len(date)-1:
                pdy_list.append(pdy[0])
            else:
                pdy_list.append(None)
        pdy_list = json.dumps(pdy_list)
        return render_template("alldata.html", user=check, labels=date, values=time, values2=trendy, pdy=pdy_list)
    elif check == 1:
        return render_template("alldata.html", user=check)

#not done
@app.route('/profile', methods=['GET', 'POST'])
def profile():
    check = check_user()
    if check == 0:
        form = Profile()
        image_file = url_for('static', filename='pics/' + current_user.photo)
        if form.submit.data:
            #print(0)
            #current_user.firstname = form.fname.data
            #current_user.lastname = form.lname.data
            #current_user.email = form.email.data
            #current_user.about = form.about.data
            #db.session.commit()
            #print(form.fname.data, form.lname.data, form.email.data, form.about.data)
            id = current_user.id
            user = Users.query.filter(Users.id==id)
            print(user)
            user.update({
                "firstname": form.fname.data,
                "lastname": form.lname.data,
                "email": form.email.data,
                "about": form.about.data
            })
            db.session.commit()
        #elif request.method == 'GET':
        #    form.fname.data = current_user.firstname
        #    form.lname.data = current_user.lastname
        #    form.email.data = current_user.email
        #    form.about.data = current_user.about
        return render_template("profile.html", image_file=image_file, user=check, form=form)
    return render_template("profile.html")
#done
def send_rp_email(user):
    token = user.get_token()
    mess = Message('Password Reset Request', sender="raja8450@dubaicollege.org", recipients=[user.email])
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
#not done
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
        user = Users.query.filter(Users.id == current_user.id)
        user.update({
            "password": hashed_pass
        })
        db.session.commit()
        flash(f'Login now','success')
        return redirect(url_for('login'))
    return render_template('resetpass.html', form=form)

current_event = " "
def update_event(type, dist):
    global current_event
    current_event = str(type) + " " + str(dist)

def return_event():
    return current_event
#!!!
@app.route('/chooseevent', methods=['GET', 'POST'])
def chooseevent():
    check = check_user()
    if check == 1:
        form = ChooseEvent()
        if form.validate_on_submit():
            if form.submit.data:
                update_event(form.eventType.data, form.eventDistance.data)
                #if len(session["present"]) >= 0:
                return redirect(url_for('timer'))
                #elif len(session["present"]) == 0:
                    #return redirect(url_for('timer'))
        return render_template("admin/chooseevent.html", form=form)
    else:
        return redirect(url_for('login'))

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
    timer_format = "{:02}:{:02}:{:02}".format(hours, minutes, remaining_seconds)
    return timer_format

@app.route('/timer_start', methods=['GET', 'POST'])
def timer_start():
    seconds = 0
    return """<h1>
    <meta http-equiv="refresh" content="1" />{}</h1>""".format(get_current_time())

@app.route('/timer_reset', methods=['GET', 'POST'])
def timer_reset():
    global seconds
    seconds = 0
    return """<h1>00:00:00</h1>"""

#!!!
def addtime(users):
    event = return_event().split(" ")
    type = event[0]
    dist = event[1]
    print(dist)
    user = users
    check = check_user()
    for i in range(0,len(users)):
        userlist = [j[1] for j in user[i].items()]
        times = userlist[0].split(':')
        name = userlist[1]
        print(name)
        time = int(times[0])*3600 + int(times[1])*60 + int(times[2])
        userSpeed = 0
        userSpeed = getspeed(time, str(dist), userSpeed)
        typeid = int(EventTypes.query.filter_by(type=str(type)).first().id)
        eventid = int(Events.query.filter_by(eventTypeID=typeid, eventDistance=int(dist)).first().eventID)
        if check == 0:
            userdst = UserDST(userID=current_user.id, eventID=eventid, userDistance=dist, userTime=time , userSpeed=userSpeed, isAssignment=0)
            db.session.add(userdst)
        elif check == 1:
            #userid = int(Users.query.filter_by(firstname=fname, lastname=lname).first().id)
            userdst = UserDST(userID=3, eventID=eventid, userDistance=dist, userTime=time , userSpeed=userSpeed, isAssignment=0)
            db.session.add(userdst)
        db.session.commit()


    #time = int(form.userTimeM.data)*60 + int(form.userTimeS.data)
    #userSpeed = getspeed(time, str(form.eventDistance.data), userSpeed)
    #dist = str(form.eventDistance.data)
    #dist = int(dist)
    #typeid = int(EventTypes.query.filter_by(type=str(form.eventType.data)).first().id)
    #eventid = int(Events.query.filter_by(eventTypeID=typeid, eventDistance=int(str(form.eventDistance.data))).first().eventID)
    #userdst = UserDST(userID=current_user.id, eventID=eventid, userDistance=dist, userTime=time , userSpeed=userSpeed, isAssignment=assign)
    #db.session.add(userdst)
    #db.session.commit()

    #print(type, dist)
    #users = get_user_data()

    #for name, id in users['Users Present for Today'].items():
    #    for user_dict in users:
    #        if name == user_dict["users"].firstname + ' ' + user_dict["users"].lastname:
    #            time = user_dict["time"].split(":")
    #            time = int(time[0])*3600 + int(time[1])*60 + int(time[2])
    #            time = time if time > 1 else 1
    #            userSpeed = getspeed(time, str(users["eventDistance"]), userSpeed)
    #            dist = str(users["eventDistance"])
    #            dist = int(dist)
    #            typeid = int(EventTypes.query.filter_by(type=str(users["eventType"])).first().id)
    #            eventid = int(Events.query.filter_by(eventTypeID=typeid, eventDistance=int(str(users["eventDistance"]))).first().eventID)
    #            userdst = UserDST(userID=id, eventID=eventid, userDistance=dist, userTime=time, userSpeed=userSpeed, isAssignment=0)
    #            db.session.add(userdst)
    #db.session.commit()

@app.route('/timer', methods=['GET', 'POST'])
def timer():
    check = check_user()
    event = return_event().split(" ")
    if check == 1:
        form = Timer()
        date = (str(datetime.today()).split(' '))[0]
        type = event[0]
        distance = event[1]
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
                    "users": QuerySelectField('Name', query_factory=user_query, allow_blank=True, validators=[DataRequired()])
                }
            )
            return render_template("admin/timer.html", form=form, starttime=starttime, user=check)
        elif form.reset.data:
            reset_starttime()

        if form.submit.data:
            flash(f'Data submitted','success')
            users = form.users.data
            addtime(users)
        return render_template("admin/timer.html", form=form, date=date, type=type, distance=distance, user=check)
    if check == 0:
        form = Timer()
        date = (str(datetime.today()).split(' '))[0]
        type = event[0]
        distance = event[1]
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
                    "users": QuerySelectField('Name', query_factory=user_query, allow_blank=True, validators=[DataRequired()])
                }
            )
            return render_template("admin/timer.html", form=form, starttime=starttime, user=check)
        elif form.reset.data:
            reset_starttime()

        if form.submit.data:
            flash(f'Data submitted','success')
            users = form.users.data
            addtime(users)
        return render_template("admin/timer.html", form=form, date=date, type=type, distance=distance, user=check)


#@app.route('/regtimer', methods=['GET', 'POST'])
#def regtimer():
#    global present
#    check = check_user()
#    if check == 1:
#        form = RegTimer()
#        print(present)
#        if form.start.data:
#            update_starttime()
#            pass
#        elif form.store.data:
#            starttime = return_starttime()
#
#            if starttime != "00:00:00":
#                time = str(datetime.now() - starttime).split('.')[0]
#            else:
#                time = starttime
#            #form.users.choices = present
#            #reg = present
#            reg = ["Bob", "Linda"]
#            form.users.append_entry(
#                {
#                    "time": time,
#                    "users": SelectField('Name', choices=reg, validators=[DataRequired()])
#                }
#            )
#            return render_template("admin/timer.html", form=form, starttime=starttime)
#        elif form.reset.data:
#            reset_starttime()
#
#        if form.submit.data:
#            users = form.users.data
#            addtime(users)
#            session["present"] = []
#            return redirect(url_for('adash'))
#        return render_template("admin/timer.html", form=form)

present = []

#!!!
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
        print(present)
        return redirect(url_for('chooseevent'))
    return render_template("admin/register.html", form=form)
