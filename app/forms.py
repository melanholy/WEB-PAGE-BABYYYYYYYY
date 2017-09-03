from html import escape
from sanic_wtf import SanicForm
from wtforms.widgets import HTMLString, html_params
from wtforms.compat import text_type
from wtforms import StringField, PasswordField, IntegerField, \
                    HiddenField, validators, ValidationError

FIELD_REQUIRED_MSG = 'Не было заполнено бязательное поле'
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

class LoginForm(SanicForm):
    Meta = NoIdAttributeMeta
    username = StringField('Username', [
        validators.Length(min=1, max=25, message='Максимальная длина имени - 25 символов.'),
        validators.DataRequired(message=FIELD_REQUIRED_MSG)
    ])
    password = PasswordField('Password', [
        validators.DataRequired(message=FIELD_REQUIRED_MSG)
    ])

class RegisterForm(SanicForm):
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

class FeedbackForm(SanicForm):
    Meta = NoIdAttributeMeta
    age = IntegerField('Age', [
        validators.DataRequired(message=FIELD_REQUIRED_MSG),
        validators.NumberRange(min=1, max=999, message='Вы не можете быть старше 999 лет.')
    ])
    text = MY_TEXTAREA

class EditFeedbackForm(SanicForm):
    Meta = NoIdAttributeMeta
    edit_id = HiddenField('Id', [
        validators.DataRequired(message=FIELD_REQUIRED_MSG)
    ])
    edit_text = MY_TEXTAREA

class CommentForm(SanicForm):
    Meta = NoIdAttributeMeta
    id_ = HiddenField('Id', [
        validators.DataRequired(message=FIELD_REQUIRED_MSG)
    ])
    text = MY_TEXTAREA

class DeleteFeedbackForm(SanicForm):
    Meta = NoIdAttributeMeta
    del_id = HiddenField('Id', [
        validators.DataRequired(message=FIELD_REQUIRED_MSG)
    ])
