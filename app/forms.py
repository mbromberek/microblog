import flask_wtf
import wtforms
from wtforms.validators import DataRequired

class LoginForm(flask_wtf.FlaskForm):
    username = wtforms.StringField('Username', validators=[DataRequired()])
    password = wtforms.PasswordField('Password', validators=[DataRequired()])
    remember_me = wtforms.BooleanField('Remember Me')
    submit = wtforms.SubmitField('Sign In')
