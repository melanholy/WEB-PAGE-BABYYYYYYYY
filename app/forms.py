from app import app
from flask import session
from wtforms import Form, StringField, PasswordField, IntegerField, \
                    HiddenField, validators
from wtforms.csrf.session import SessionCSRF
from wtforms.widgets import HTMLString, html_params
from html import escape
from wtforms.compat import text_type

FIELD_REQUIRED_MSG = 'Обязательное поле'

class TextArea(object):
    """
    Renders a multi-line text area.

    `rows` and `cols` ought to be passed as keyword args when rendering.
    """
    def __call__(self, field, **kwargs):
        data = kwargs.get('data', '')
        if data:
            del kwargs['data']
        kwargs.setdefault('id', field.id)
        return HTMLString('<textarea %s>%s</textarea>' % (
            html_params(name=field.name, **kwargs),
            escape(text_type(data), quote=False)
        ))

class LoginForm(Form):
    class Meta:
        csrf = True
        csrf_class = SessionCSRF
        csrf_secret = app.config['CSRF_SECRET_KEY']

        @property
        def csrf_context(self):
            return session

    username = StringField('Username', [
        validators.Length(min=1, max=25),
        validators.DataRequired(message=FIELD_REQUIRED_MSG)
    ])
    password = PasswordField('Password', [
        validators.DataRequired(message=FIELD_REQUIRED_MSG)
    ])

class RegisterForm(Form):
    class Meta:
        csrf = True
        csrf_class = SessionCSRF
        csrf_secret = app.config['CSRF_SECRET_KEY']

        @property
        def csrf_context(self):
            return session

    username = StringField('Username', [
        validators.Length(min=1, max=25),
        validators.DataRequired(message=FIELD_REQUIRED_MSG)
    ])
    password = PasswordField('Password', [
        validators.DataRequired(message=FIELD_REQUIRED_MSG),
        validators.EqualTo('confirm', message='Пароли должны совпадать')
    ])
    confirm = PasswordField('Repeat Password', [
        validators.DataRequired(message=FIELD_REQUIRED_MSG)
    ])

class FeedbackForm(Form):
    class Meta:
        csrf = True
        csrf_class = SessionCSRF
        csrf_secret = app.config['CSRF_SECRET_KEY']

        @property
        def csrf_context(self):
            return session

    age = IntegerField('Age', [
        validators.DataRequired(message=FIELD_REQUIRED_MSG),
        validators.NumberRange(min=1, max=999)
    ])
    text = StringField(
        'Text',
        [validators.DataRequired(message=FIELD_REQUIRED_MSG)],
        widget=TextArea()
    )

class EditFeedbackForm(Form):
    class Meta:
        csrf = True
        csrf_class = SessionCSRF
        csrf_secret = app.config['CSRF_SECRET_KEY']

        @property
        def csrf_context(self):
            return session

    id_ = HiddenField('Id')
    text = StringField(
        'Text',
        [validators.DataRequired(message=FIELD_REQUIRED_MSG)],
        widget=TextArea()
    )
