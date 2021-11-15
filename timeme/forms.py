from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, IntegerField, IntegerField, SelectField
from wtforms.fields.html5 import DateField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError, Optional
import wtforms.validators as validators
from timeme.models import *
from wtforms_sqlalchemy.fields import QuerySelectField


class uRegistrationForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    firstname = StringField('First Name', validators=[DataRequired()])
    lastname = StringField('Last Name', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    bday = DateField('Birth Date', format='%Y-%m-%d')
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')

    def validate_email(self, email):
        user1 = Users.query.filter_by(email=email.data).first()
        if user1:
            raise ValidationError('There is already an account under this email. Use another email or login.')


class aRegistrationForm(FlaskForm):
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    firstname = StringField('First Name', validators=[DataRequired()])
    lastname = StringField('Last Name', validators=[DataRequired()])
    bday = DateField('Birth Date', format='%Y-%m-%d')
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password',
                                     validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')

    def validate_email(self, email):
        admin = Users.query.filter_by(email=email.data).first()
        if admin:
            raise ValidationError('There is already an account under this email. Use another email or login.')


class ClassForm(FlaskForm):
    classcode = StringField('Class Code', validators=[DataRequired(), Length(min=6, max=6)])
    submit = SubmitField('Submit')


class LoginForm(FlaskForm):
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')

class AddClass(FlaskForm):
    classname = StringField('Class Name', validators=[DataRequired()])
    classcode = StringField('Class Code', validators=[DataRequired(), Length(min=6, max=6)])
    submit = SubmitField('Submit')

    def validate_classcode(self, classcode):
        classc = Classes.query.filter_by(classCode=classcode.data).first()
        if classc:
            raise ValidationError('This code has been taken. Choose another code.')

class EnterCode(FlaskForm):
    classcode = StringField('Class Code', validators=[DataRequired()])
    submit = SubmitField('Submit')

    def validate_classcode(self, classcode):
        classc = Classes.query.filter_by(classCode=classcode.data).first()
        if classc:
            print(0)
        else:
            raise ValidationError('There is no class with that code. Please enter a valid code.')

def event_query():
    return Events.query

def eventtype_query():
    return EventTypes.query

def user_query():
    return Users.query

class UserEnterData(FlaskForm):
    eventType = QuerySelectField('Event Type', query_factory=eventtype_query, allow_blank=True)
    eventDistance = QuerySelectField('Event Distance', query_factory=event_query, allow_blank=True)
    userTimeM = IntegerField('Minutes', validators=[validators.InputRequired()])
    userTimeS = IntegerField('Seconds', validators=[validators.InputRequired()])
    submit = SubmitField('Submit')

class AdminEnterData(FlaskForm):
    user = QuerySelectField('Name', query_factory=user_query, allow_blank=True, validators=[DataRequired()])
    eventType = QuerySelectField('Event Type', query_factory=eventtype_query, allow_blank=True,validators=[DataRequired()])
    eventDistance = QuerySelectField('Event Distance', query_factory=event_query, allow_blank=True, validators=[DataRequired()])
    userTimeM = IntegerField('Minutes', validators=[validators.InputRequired()])
    userTimeS = IntegerField('Seconds', validators=[validators.InputRequired()])
    submit = SubmitField('Submit')

class CreateEvent(FlaskForm):
    eventType = QuerySelectField('Event Type', query_factory=eventtype_query, allow_blank=True, validators=[DataRequired()])
    eventDistance = IntegerField('Event Distance', validators=[validators.Optional()])
    eventTimeM = IntegerField('Minutes', validators=[validators.Optional()])
    eventTimeS = IntegerField('Seconds', validators=[validators.Optional()])
    submit = SubmitField('Submit')

    def validate_createE(self, eventDistance, eventTime, eventType):
        eD = eventDistance.data
        eT = str(eventTimeM.data) + str(eventTimeS.data)
        if eD is None and eT is None:
            raise ValidationError("Please enter either the distance or the time")
            print("Please enter either the distance or the time")
        elif eD and eT:
            raise ValidationError("Please choose only the distance or time")
            print("Please choose only the distance or time")
        else:
            eventid = EventTypes.query.filter_by(type=eventType.data).first().id
            if eD is not None:
                event = Events.query.filter_by(eventDistance=eD, eventID=eventid).first()
                if event is not None:
                    raise ValidationError('There is already an event like that.')
                    print('There is already an event like that.')
            elif eT is not None:
                event = Events.query.filter_by(eventTime=eT, eventID=eventid).first()
                if event:
                    raise ValidationError('There is already an event like that.')
                    print('There is already an event like that.')

class CreateEventType(FlaskForm):
    eventType = StringField('Event Type', validators=[DataRequired()])
    submit = SubmitField('Submit')

    def validate_ET(self, event):
        event = EventTypes.query.filter_by(type=eventType.data).first()
        if event or eventType.data.upper() == event.eventType.upper():
            raise ValidationError('This event already exists. Please enter another one.')

class Profile(FlaskForm):
    fname = StringField('First Name')
    lname = StringField('lastname')
    email = StringField('Email')
    about = StringField('About')
    submit = SubmitField('Submit')

class RequestResetPass(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Send Email')

    def validate_email(self, email):
        user1 = Users.query.filter_by(email=email.data).first()
        if user1 is None:
            raise ValidationError('There is no account with this email.')

class ResetPass(FlaskForm):
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Reset Password')

class SetAssignment(FlaskForm):
    dday = DateField('Due Date', format='%Y-%m-%d')
    eventtype = QuerySelectField('Event Type', query_factory=eventtype_query, allow_blank=True, validators=[DataRequired()])
    eventdist = QuerySelectField('Event Distance', query_factory=event_query, allow_blank=True, validators=[DataRequired()])
    submit = SubmitField('Set Assignment')

from flask_login import current_user

def classes_query():
    classes = Classes.query(Classes.className).filter_by(classAdminID=current_user.id).all()
    return classes

class SelectClass(FlaskForm):
    classname = QuerySelectField('Class name', query_factory=classes_query, allow_blank=True, validators=[DataRequired()])
    submit = SubmitField('Go to class dashboard')
