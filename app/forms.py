from html import escape
from flask_wtf import Form
from wtforms.widgets import HTMLString, html_params
from wtforms.compat import text_type
from wtforms import StringField, PasswordField, IntegerField, \
                    HiddenField, validators, ValidationError

FIELD_REQUIRED_MSG = 'Обязательное поле'
AUTO = object()

def check_bad_symbols(form, field):
    for char in field.data:
        code = ord(char)
        if code != 1025 and (code > 256 and code < 1040 or code > 1105):
            raise ValidationError('Нельзя использовать особые символы.')

class NoIdAttributeMeta(object):
    def bind_field(self, form, unbound_field, options):
        unbound_field.kwargs.setdefault('id', AUTO)
        return super().bind_field(form, unbound_field, options)

    def render_field(self, field, render_kw):
        if field.id is AUTO:
            field.id = False
        return super().render_field(field, render_kw)

class TextArea(object):
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
    Meta = NoIdAttributeMeta
    username = StringField('Username', [
        validators.Length(min=1, max=25, message='Максимальная длина имени - 25 символов.'),
        validators.DataRequired(message=FIELD_REQUIRED_MSG)
    ])
    password = PasswordField('Password', [
        validators.DataRequired(message=FIELD_REQUIRED_MSG)
    ])

class RegisterForm(Form):
    Meta = NoIdAttributeMeta
    username = StringField('Username', [
        validators.Length(min=1, max=25, message='Максимальная длина имени - 25 символов.'),
        validators.DataRequired(message=FIELD_REQUIRED_MSG),
        check_bad_symbols
    ])
    password = PasswordField('Password', [
        validators.DataRequired(message=FIELD_REQUIRED_MSG),
        validators.EqualTo('confirm', message='Пароли должны совпадать')
    ])
    confirm = PasswordField('Repeat Password', [
        validators.DataRequired(message=FIELD_REQUIRED_MSG)
    ])

MY_TEXTAREA = StringField(
    'Text',
    [
        validators.DataRequired(message=FIELD_REQUIRED_MSG),
        check_bad_symbols,
        validators.Length(min=1, max=1024, message='Максимальная длина - 1024 символа.')
    ],
    widget=TextArea()
)

class FeedbackForm(Form):
    Meta = NoIdAttributeMeta
    age = IntegerField('Age', [
        validators.DataRequired(message=FIELD_REQUIRED_MSG),
        validators.NumberRange(min=1, max=999, message='Вы не можете быть старше 999 лет.')
    ])
    text = MY_TEXTAREA

class EditFeedbackForm(Form):
    Meta = NoIdAttributeMeta
    id_ = HiddenField('Id')
    text = MY_TEXTAREA

class CommentForm(Form):
    Meta = NoIdAttributeMeta
    id_ = HiddenField('Id')
    text = MY_TEXTAREA

class DeleteFeedbackForm(Form):
    Meta = NoIdAttributeMeta
    id_ = HiddenField('Id')
