from flask.ext.wtf import Form
from wtforms import StringField, SubmitField, PasswordField
from wtforms.validators import Required, Length, Email, ValidationError

from ..models import User

def validate_name(form, field):
    if not User.is_username_valid(field.data):
        raise ValidationError("Username is not valid, \
                              it should contains only letters and numbers")
    if User.is_user_exists(field.data):
        raise ValidationError("Username is not unique")

def validate_email(form, field):
    if User.is_email_exists(field.data):
        raise ValidationError("Email is not unique")

def validate_login_name(form, field):
    if not User.is_user_exists(field.data):
        raise ValidationError("There are no user with such username")


class RegistrationForm(Form):
    name = StringField('Enter your name', validators=[Required(), Length(3, 32), validate_name])
    password = PasswordField('Enter your password', validators=[Required(), Length(3, 32)])
    email = StringField('Enter your email', validators=[Required(), Email(), validate_email])
    submit = SubmitField('Register')


class LoginForm(Form):
    name = StringField('Username', validators=[Required(), validate_login_name])
    password = PasswordField('Password', validators=[Required(),])
    submit = SubmitField('Login')


class TaskForm(Form):
    text = StringField('Task description', validators=[Required(),])
    submit = SubmitField('Add')