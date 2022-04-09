from flask_wtf import FlaskForm
from flask_login import current_user
from wtforms import StringField, PasswordField, SubmitField, BooleanField, IntegerField, IntegerField, SelectField, FieldList, FormField, Form
from wtforms.fields.html5 import DateField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError, Optional
import wtforms.validators as validators
from timeme.models import *
from wtforms_sqlalchemy.fields import QuerySelectField

#form for registering a user
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
#form for registering an admin
class aRegistrationForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    firstname = StringField('First Name', validators=[DataRequired()])
    lastname = StringField('Last Name', validators=[DataRequired()])
    bday = DateField('Birth Date', format='%Y-%m-%d')
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')

    def validate_email(self, email):
        admin = Users.query.filter_by(email=email.data).first()
        if admin:
            raise ValidationError('There is already an account under this email. Use another email or login.')
#form for everyone to login
class LoginForm(FlaskForm):
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')
#form for an admin/teacher to create a class
class AddClass(FlaskForm):
    classname = StringField('Class Name', validators=[DataRequired()])
    classcode = StringField('Class Code', validators=[DataRequired(), Length(min=6, max=6)])
    submit = SubmitField('Submit')

    def validate_classcode(self, classcode):
        classc = Classes.query.filter_by(classCode=classcode.data).first()
        if classc:
            raise ValidationError('This code has been taken. Choose another code.')
#form for an student/user to enter their class code
class EnterCode(FlaskForm):
    classcode = StringField('Class Code', validators=[DataRequired()])
    submit = SubmitField('Submit')

    def validate_classcode(self, classcode):
        classc = Classes.query.filter_by(classCode=classcode.data).first()
        if classc:
            print(0)
        else:
            raise ValidationError('There is no class with that code. Please enter a valid code.')
#function to query an event type
def eventtype_query():
    return EventTypes.query
#function to query the names of students
def user_query():
    return Users.query.filter(Users.isAdmin!=1)
#form that serves as a field set for multiple forms
class Intervals(Form):
    intervalDist = IntegerField('Distance from start', validators=[validators.Optional()])
    intervalM = IntegerField('Time', validators=[validators.Optional()])
    intervalS = IntegerField('Time', validators=[validators.Optional()])
#query for all distances
eventdist = [i[0] for i in db.session.query(Events.eventDistance).filter(Events.eventTime==0).all()]
#query for all times
eventtime = [i[0] for i in db.session.query(Events.eventTime).filter(Events.eventDistance==0).all()]
#form for students to enter data for a distance-based event
class UserEnterData(FlaskForm):
    eventType = QuerySelectField('Event Type', query_factory=eventtype_query, validators=[DataRequired()])
    eventDistance = SelectField('Event Distance', choices=eventdist, validators=[DataRequired()])
    userTimeM = IntegerField('Minutes', validators=[validators.InputRequired()])
    userTimeS = IntegerField('Seconds', validators=[validators.InputRequired()])
    submit = SubmitField('Submit')
    userInterval = FieldList(FormField(Intervals), label="Intervals")
    addInterval = SubmitField(label='Add Interval')
#form for students to enter data for time-based event
class UserEnterDist(FlaskForm):
    eventType = QuerySelectField('Event Type', query_factory=eventtype_query, validators=[DataRequired()])
    userTime = SelectField('Minutes', choices=[], validators=[validators.InputRequired()])
    eventDistance = IntegerField('Event Distance', validators=[DataRequired()])
    submit = SubmitField('Submit')
    userInterval = FieldList(FormField(Intervals), label="Intervals")
    addInterval = SubmitField(label='Add Interval')
#form for teachers to enter data for a distance-based event
class AdminEnterData(FlaskForm):
    user = SelectField('Name', choices=[], validators=[DataRequired()])
    eventType = QuerySelectField('Event Type', query_factory=eventtype_query, validators=[DataRequired()])
    eventDistance = SelectField('Event Distance', choices=[], validators=[DataRequired()])
    userTimeM = IntegerField('Minutes', validators=[validators.InputRequired()])
    userTimeS = IntegerField('Seconds', validators=[validators.InputRequired()])
    submit = SubmitField('Submit')
    userInterval = FieldList(FormField(Intervals), label="Intervals")
    addInterval = SubmitField(label='Add Interval')
#form for teacher to edit data
class AdminEditData(FlaskForm):
    user = SelectField('Name', choices=[], validators=[DataRequired()])
    eventType = SelectField('Event Type', choices=[], validators=[DataRequired()])
    eventDistance = SelectField('Event Distance', choices=[], validators=[DataRequired()])
    eventTime = SelectField('Event Time', choices=[], validators=[DataRequired()])
    userTimeM = IntegerField('Minutes', validators=[validators.InputRequired()])
    userTimeS = IntegerField('Seconds', validators=[validators.InputRequired()])
    userDistance = IntegerField('Distance', validators=[validators.InputRequired()])
    submit = SubmitField('Submit')
#form for teachers to enter data for time-based event
class AdminEnterDist(FlaskForm):
    user = SelectField('Name', choices=[], validators=[DataRequired()])
    eventType = QuerySelectField('Event Type', query_factory=eventtype_query, validators=[DataRequired()])
    userTime = SelectField('Minutes', choices=[], validators=[validators.InputRequired()])
    eventDistance = IntegerField('Event Distance', validators=[DataRequired()])
    submit = SubmitField('Submit')
    userInterval = FieldList(FormField(Intervals), label="Intervals")
    addInterval = SubmitField(label='Add Interval')
#form for filtering through students
class ChooseStudent(FlaskForm):
    user = SelectField('Name', choices=[], validators=[DataRequired()])
    submit = SubmitField('Submit')
#form for students to submit an assignment
class SubmitAssignment(FlaskForm):
    eventType = SelectField('Event Type', choices=[], validators=[DataRequired()])
    eventDistance = SelectField('Event Distance', choices=[], validators=[DataRequired()])
    eventTime = SelectField('Event Time', choices=[], validators=[DataRequired()])
    userTimeM = IntegerField('Minutes', validators=[validators.InputRequired()])
    userTimeS = IntegerField('Seconds', validators=[validators.InputRequired()])
    userDistance = IntegerField('Distance', validators=[validators.InputRequired()])
    submit = SubmitField('Submit')
    userInterval = FieldList(FormField(Intervals), label="Intervals")
    addInterval = SubmitField(label='Add Interval')
#form for teachers to create an event
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
#form for teachers to create an event type
class CreateEventType(FlaskForm):
    eventType = StringField('Event Type', validators=[DataRequired()])
    submit = SubmitField('Submit')

    def validate_ET(self, event):
        event = EventTypes.query.filter_by(type=eventType.data).first()
        if event or eventType.data.upper() == event.eventType.upper():
            raise ValidationError('This event already exists. Please enter another one.')
#form for editing a profile
class Profile(FlaskForm):
    fname = StringField('First Name', validators=[DataRequired()])
    lname = StringField('Last Name', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired()])
    about = StringField('About')
    submit = SubmitField('Submit')
#form to enter an email to send a 'forgot password' email
class RequestResetPass(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Send Email')

    def validate_email(self, email):
        user1 = Users.query.filter_by(email=email.data).first()
        if user1 is None:
            raise ValidationError('There is no account with this email.')
#form to create a new password
class ResetPass(FlaskForm):
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Reset Password')
#form for teachers to set distance-based assignments
class SetDistAssignment(FlaskForm):
    eventType = QuerySelectField('Event Type', query_factory=eventtype_query, validators=[DataRequired()])
    eventDistance = SelectField('Event Distance', choices=[], validators=[DataRequired()])
    dday = DateField('Due Date', format='%Y-%m-%d')
    submit = SubmitField('Submit')
#form for teachers to set time-based assignments
class SetTimedAssignment(FlaskForm):
    eventType = QuerySelectField('Event Type', query_factory=eventtype_query, validators=[DataRequired()])
    eventTime = SelectField('Event Distance', choices=[], validators=[DataRequired()])
    dday = DateField('Due Date', format='%Y-%m-%d')
    submit = SubmitField('Submit')

from flask_login import current_user
#form for querying classes that belong to a teacher
def classes_query():
    return Classes.query.filter_by(classAdminID=current_user.id).all()
#form for selecting a class to visit
class SelectClass(FlaskForm):
    classname = QuerySelectField('Class name', query_factory=classes_query, allow_blank=True, validators=[DataRequired()])
    submit = SubmitField('Go to class dashboard')
#form for selecting an assignment to submit
class SelectAssignment(FlaskForm):
    assignmentID = IntegerField('Assignment Name', validators=[DataRequired()])
    submit = SubmitField('Enter data')
#form to submit a DST ID to review or edit
class ChooseDSTID(FlaskForm):
    id = IntegerField('ID', validators=[DataRequired()])
    review = SubmitField('Review')
    edit = SubmitField('Edit')
#form for a teacher to review an assignment
class ReviewAssignment(FlaskForm):
    id = IntegerField('ID', validators=[DataRequired()])
    user = SelectField('Name', choices=[], validators=[DataRequired()])
    submit = SubmitField('Check')
#form for a user to check the data for an event
class CheckEventData(FlaskForm):
    eventtype = QuerySelectField('Event Type', query_factory=eventtype_query, allow_blank=True, validators=[DataRequired()])
    eventdist = SelectField('Event Distance', choices=[])
    eventtime = SelectField('Event Time', choices=[])
    submit = SubmitField('Check')
#form that serves as a field list for UserReg
class AddUser(Form):
    userReg = QuerySelectField('Time', query_factory=user_query, allow_blank=True, validators=[validators.Optional()])
#form to register students
class UserReg(FlaskForm):
    submit = SubmitField('Submit')
    user = FieldList(FormField(AddUser), label="Name")
    addUser = SubmitField(label='Add User')
#form to review a register
class ReviewRegisters(FlaskForm):
    regID = IntegerField('Register ID', validators=[DataRequired()])
    submit = SubmitField('Review')
#form that serves as a field list for UserEmail
class AddEmail(Form):
    userEmail = StringField('Email', validators=[validators.Optional()])
#form for inviting students to a class
class UserEmail(FlaskForm):
    submit = SubmitField('Submit')
    user = FieldList(FormField(AddEmail), label="Email")
    addUser = SubmitField(label='Add User')
#form to choose an event for a timer
class ChooseEvent(FlaskForm):
    eventType = QuerySelectField('Event Type', query_factory=eventtype_query, allow_blank=True, validators=[DataRequired()])
    eventDistance = SelectField('Event Distance', choices=[], validators=[DataRequired()])
    submit = SubmitField('Continue')
#form that serves as a field list for Timer
class ChooseUser(Form):
    users = QuerySelectField('Name', query_factory=user_query)
    time = StringField('Time', validators=[validators.InputRequired()])
#form that allows teachers and students to time themselves
class Stopwatch(FlaskForm):
    start = SubmitField('Start')
    reset = SubmitField('Reset')
    store = SubmitField('Store')

    users = FieldList(FormField(ChooseUser), label='Users')
    submit = SubmitField('Submit')
