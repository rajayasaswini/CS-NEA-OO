from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, IntegerField, TimeField, SelectField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from timeme.models import *
from wtforms_sqlalchemy.fields import QuerySelectField


class uRegistrationForm(FlaskForm):
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    firstname = StringField('First Name', validators=[DataRequired()])
    lastname = StringField('Last Name', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password',
                                     validators=[DataRequired(), EqualTo('password')])
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
    userTime = StringField('User Time', validators=[DataRequired()])
    submit = SubmitField('Submit')

class AdminEnterData(FlaskForm):
    user = QuerySelectField('Name', query_factory=user_query, allow_blank=True, validators=[DataRequired()])
    eventType = QuerySelectField('Event Type', query_factory=eventtype_query, allow_blank=True,validators=[DataRequired()])
    eventDistance = QuerySelectField('Event Distance', query_factory=event_query, allow_blank=True, validators=[DataRequired()])
    userTime = StringField('User Time', validators=[DataRequired()])
    submit = SubmitField('Submit')

class CreateEvent(FlaskForm):
    eventType = QuerySelectField('Event Type', query_factory=eventtype_query, allow_blank=True, validators=[DataRequired()])
    eventDistance = IntegerField('Event Distance')
    eventTime = TimeField('Event Time')
    submit = SubmitField('Submit')

    def validate_form(self, eventDistance, eventTime):
        if eventDistance.data == None and eventTime.data == None:
            raise ValidationError("Please enter either the event distance or the event time")
        elif eventDistance.data != None and eventTime.data != None:
            raise ValidationError("Please choose only an event distance or time")
        else:
            eventid = EventTypes.query.filter_by(type=eventType.data).first().id
            eventD = Events.query.filter_by(eventDistance=eventDistance.data, eventID=eventid).first()
            eventT = Events.query.filter_by(eventTime=eventTime.data, eventID=eventid).first()
            if eventD is None:
                print(1)
            elif eventT is None:
                print(1)
            else:
                raise ValidationError('There is already an event like that.')


#    def validate_event(self, eventType, eventDistance, eventTime):
#        eventid = EventTypes.query.filter_by(type=eventType.data).first().id
#        event = Events.query.filter_by(eventDistance=eventDistance.data, eventID=eventid).first()
#        if event is None:
#            print(' ')
#        else:
#            raise ValidationError('There is already an event like that.')

class CreateEventType(FlaskForm):
    eventType = StringField('Event Type', validators=[DataRequired()])
    submit = SubmitField('Submit')

    def validate_ET(self, event):
        event = EventTypes.query.filter_by(type=eventType.data).first()
        if event or eventType.data.upper() == event.eventType.upper():
            raise ValidationError('This event already exists. Please enter another one.')

#get user time in minutes and seconds
#in routes, use the data to get speed
#add usertime as time in the database
