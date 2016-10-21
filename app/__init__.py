from flask import Flask
from flask_login import LoginManager
from flask_pymongo import PyMongo
from flask_wtf import CsrfProtect

app = Flask(__name__, static_folder='static')
app.config.from_object('config')

login_manager = LoginManager(app)
login_manager.login_view = '/login'
login_manager.login_message = 'Пожалуйста, войдите для доступа к этой странице.'

mongo = PyMongo(app)

CsrfProtect(app)

from app.models import User

@login_manager.user_loader
def load_user(user_id):
    return User.get_by_id(user_id)

from app import views

url_map = [x.rule for x in app.url_map.iter_rules()]
