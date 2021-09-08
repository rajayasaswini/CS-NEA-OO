from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, IntegerField, TimeField, SelectField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from timeme.models import *

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

#class AdminEnterData(FlaskForm):
#    userName = SelectField("User Name", validators=[DataRequired()], choice=Users.query.filter_by(id=ClassesUsers.query.filter_by(classID=classID).UserID))
#    eventID = IntegerField('Event ID', validators=[DataRequired()])
#    userDistance = IntegerField('User Distance', validators=[DataRequired()])
#    userTime = TimeField('User Time', validators=[DataRequired()])

class UserEnterData(FlaskForm):
    eventName = SelectField("Event Name", validators=[DataRequired()], choices=['500m sprint', '200m sprint'])
    userDistance = IntegerField('User Distance', validators=[DataRequired()])
    userTime = StringField('User Time', validators=[DataRequired()])
    submit = SubmitField('Submit')
#get user time in minutes and seconds
#in routes, use the data to get speed
#add usertime as time in the database
