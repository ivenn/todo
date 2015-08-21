from flask.ext.wtf import Form
from wtforms import StringField, SubmitField
from wtforms.validators import Required, Length, Email, ValidationError
from models import User

def validate_name(form, field):
    if not User.is_user_unique(field.data):
        raise ValidationError("Username is not unique")


class RegistrationForm(Form):
    name = StringField('Enter your name', validators=[Required(), Length(3, 32), validate_name])
    password = StringField('Enter your password', validators=[Required(), Length(3, 32)])
    email = StringField('Enter your email', validators=[Required(), Email()])
    submit = SubmitField('Submit')


class LoginForm(Form):
    name = StringField('Username', validators=[Required(),])
    password = StringField('Password', validators=[Required(),])
    submit = SubmitField('Submit')


class TaskForm(Form):
    text = StringField('Task description', validators=[Required(),])
    submit = SubmitField('Add')