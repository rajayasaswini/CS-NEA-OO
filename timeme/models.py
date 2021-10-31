from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from sqlalchemy.sql import text
from sqlalchemy import *
from sqlalchemy.orm import relationship, backref
from timeme import db, login_man
from flask_login import UserMixin
import datetime

@login_man.user_loader
def getuser(user_id):
    return Users.query.get(int(user_id))

class Users(db.Model, UserMixin):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(4096),nullable=False, unique=True)
    password = db.Column(db.String(255), nullable=False)
    firstname = db.Column(db.String(255), nullable=True)
    lastname = db.Column(db.String(255), nullable=True)
    about = db.Column(db.String(4096),nullable=True)
    photo = db.Column(db.String(20), default='default.jpg')
    isAdmin = db.Column(db.Integer, nullable=False)

    #def __repr__(self):
    #    return '{} {}'.format(str(self.firstname), str(self.lastname))

class Classes(db.Model):
    __tablename__ = "classes"
    classID = db.Column(db.Integer, primary_key=True)
    className = db.Column(db.String, nullable=False)
    classCode = db.Column(db.String(6),nullable=False)
    classAdminID = db.Column(db.Integer, db.ForeignKey("users.id"))
    classes_admin = db.relationship('Users', lazy=True, foreign_keys=[classAdminID])

    def __repr__(self):
        return f"['{self.classID}', '{self.classCode}', '{self.classAdminID}']"

class ClassesUsers(db.Model):
    __tablename__="classusers"
    cuid = db.Column(db.Integer, primary_key=True)
    classID = db.Column(db.Integer, db.ForeignKey("classes.classID"))
    usersID = db.Column(db.Integer, db.ForeignKey("users.id"))
    class_r = db.relationship('Classes', lazy=True, foreign_keys=[classID])
    user_r = db.relationship('Users', lazy=True, foreign_keys=[usersID])

class EventTypes(db.Model):
    __tablename__="eventtypes"
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(100), nullable=False)

    def __repr__(self):
        return '{}'.format(str(self.type))


class Events(db.Model):
    __tablename__ = "events"
    eventID = db.Column(db.Integer, primary_key=True, nullable=False)
    eventTypeID = db.Column(db.Integer,db.ForeignKey("eventtypes.id"), nullable=False)
    eventDistance = db.Column(db.Integer, nullable=True)
    eventTime = db.Column(db.Integer, nullable=True)
    eventT_r = db.relationship('EventTypes', lazy=True, foreign_keys=[eventTypeID])


    def __repr__(self):
        return '{}'.format(str(self.eventDistance))

class Logs(db.Model):
    __tablename__ = "logs"
    userID = db.Column(db.Integer, db.ForeignKey("users.id"))
    logID = db.Column(db.Integer, primary_key=True, nullable=False)
    logContent = db.Column(db.String)
    logDateTime = db.Column(db.DateTime, nullable=False)
    log_user = db.relationship('Users', lazy=True, foreign_keys=[userID])


class Photos(db.Model):
    __tablename__ = "postphotos"
    userID = db.Column(db.Integer, db.ForeignKey("users.id"))
    postID = db.Column(db.Integer, db.ForeignKey("posts.postID"))
    postPhotoID = db.Column(db.Integer, primary_key=True, nullable=False)
    postPhoto = db.Column(db.String(20), default='default.jpg')
    postDateTime = db.Column(db.DateTime, nullable=False)
    photos_user = db.relationship('Users', lazy=True, foreign_keys=[userID])
    photo_post = db.relationship('Posts', lazy=True, foreign_keys=[postID])



class Posts(db.Model):
    __tablename__ = "posts"
    userID = db.Column(db.Integer, db.ForeignKey("users.id"))
    postID = db.Column(db.Integer, primary_key=True)
    postContent = db.Column(db.String(255))
    isPosted = db.Column(db.Integer)
    postDateTime = db.Column(db.DateTime, nullable=False)
    user_post = db.relationship('Users', lazy=True, foreign_keys=[userID])


class ScheduledAssignments(db.Model):
    __tablename__ = "scheduledassignments"
    assignmentID = db.Column(db.Integer, primary_key=True)
    eventID = db.Column(db.Integer, db.ForeignKey("events.eventID"))
    scheduledDateTime = db.Column(db.DateTime, nullable=False)
    returnDateTime = db.Column(db.DateTime, nullable=False)
    schass_event = db.relationship('Events', lazy=True, foreign_keys=[eventID])

class ReturnedAssignment(db.Model):
    __tablename__ = "returnedassignments"
    rassid = db.Column(db.Integer, primary_key=True)
    userdstid = db.Column(db.Integer, db.ForeignKey("userdst.userDSTID"))
    isLate = db.Column(db.Integer)
    rass_dst = db.relationship('UserDST', lazy=True, foreign_keys=[userdstid])

class UserDST(db.Model):
    __tablename__ = "userdst"
    userID = db.Column(db.Integer, db.ForeignKey("users.id"))
    eventID = db.Column(db.Integer, db.ForeignKey("events.eventID"))
    userDSTID = db.Column(db.Integer, primary_key=True)
    dstDateTime = db.Column(db.DateTime, nullable=False, default=datetime.datetime.utcnow)
    userDistance = db.Column(db.Integer, nullable=False)
    userTime = db.Column(db.Integer, nullable=False)
    userSpeed = db.Column(db.Integer, nullable=False)
    isAssignment = db.Column(db.Integer, nullable=False)
    dst_user = db.relationship('Users', lazy=True, foreign_keys=[userID])
    dst_event = db.relationship('Events', lazy=True, foreign_keys=[eventID])

class Register(db.Model):
    __tablename__ = "register"
    registerid = db.Column(db.Integer, primary_key=True)
    userid = db.Column(db.Integer, db.ForeignKey("classusers.cuid"))
    datetime = db.Column(db.DateTime, nullable=False)
    isPresent = db.Column(db.Integer)
    user_reg = db.relationship('ClassesUsers', lazy=True, foreign_keys=[userid])

class Intervals(db.Model):
    __tablename__ = "interval"
    intervalid = db.Column(db.Integer, primary_key=True)
    userdstid = db.Column(db.Integer, db.ForeignKey("userdst.userDSTID"))
    dist = db.Column(db.Integer, nullable=False)
    time = db.Column(db.Integer, nullable=False)
    dst_interval = db.relationship('UserDST', lazy=True, foreign_keys=[userdstid])
