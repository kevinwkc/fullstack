from flask.ext.wtf import Form
from wtforms import StringField, SubmitField, PasswordField
from wtforms.validators import Required

class LoginForm(Form):
    username = StringField('username', validators=[Required()])
    password = Password('password', validators=[Required()])
    submit = SubmitField('Submit')
    
class SignupForm(LoginForm):
    password2== Password('password', validators=[Required()])