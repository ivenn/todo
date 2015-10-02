from flask.ext.wtf import Form
from wtforms import StringField, SubmitField, PasswordField, DateField
from wtforms.validators import DataRequired, Length, Email, Optional, ValidationError
from werkzeug.datastructures import MultiDict

from ..models import User

def validate_name(form, field):
    if not User.is_username_valid(field.data):
        raise ValidationError("Username is not valid, \
                              it should contains only letters and numbers")
    if User.is_user_exists(field.data):
        raise ValidationError("Username is not unique")

def validate_subscriber(form, field):
    if not User.is_user_exists(field.data):
        raise ValidationError("No such user")

def validate_email(form, field):
    if User.is_email_exists(field.data):
        raise ValidationError("Email is not unique")

def validate_login_name(form, field):
    if not User.is_user_exists(field.data):
        raise ValidationError("There are no user with such username")


class RegistrationForm(Form):
    name = StringField('Enter your name', validators=[DataRequired(), Length(3, 32), validate_name])
    password = PasswordField('Enter your password', validators=[DataRequired(), Length(3, 32)])
    email = StringField('Enter your email', validators=[DataRequired(), Email(), validate_email])
    submit = SubmitField('Register')


class LoginForm(Form):
    name = StringField('Username', validators=[DataRequired(), validate_login_name])
    password = PasswordField('Password', validators=[DataRequired(),])
    submit = SubmitField('Login')


class TaskListForm(Form):
    name = StringField('Task list name', validators=[DataRequired(),])
    description = StringField('Task list description', validators=[Optional()])
    submit = SubmitField('Add task list')


class SubscribeForm(Form):
    subscriber = StringField('User to subscribe', validators=[DataRequired(), validate_subscriber])
    submit = SubmitField('Subscribe')


class TaskForm(Form):
    name = StringField('Task name', validators=[DataRequired(),])
    description = StringField('Task description', validators=[Optional()])
    #due_date = DateField('Due Date', format='%m/%d/%Y', validators=(Optional(),))
    submit = SubmitField('Add task')

