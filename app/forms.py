from app import app
from flask import session
from wtforms import Form, StringField, PasswordField, validators
from wtforms.csrf.session import SessionCSRF

class LoginForm(Form):
    class Meta:
        csrf = True
        csrf_class = SessionCSRF
        csrf_secret = app.config['CSRF_SECRET_KEY']

        @property
        def csrf_context(self):
            return session

    username = StringField('Username', [validators.Length(min=4, max=25)])
    password = PasswordField('Password', [
        validators.DataRequired()
    ])

class RegisterForm(Form):
    class Meta:
        csrf = True
        csrf_class = SessionCSRF
        csrf_secret = app.config['CSRF_SECRET_KEY']

        @property
        def csrf_context(self):
            return session

    username = StringField('Username', [validators.Length(min=4, max=25)])
    password = PasswordField('Password', [
        validators.DataRequired(),
        validators.EqualTo('confirm', message='Passwords must match')
    ])
    confirm = PasswordField('Repeat Password')
