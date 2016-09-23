from flask import Flask
from flask_login import LoginManager
from flask_pymongo import PyMongo
from flask_compress import Compress
from flask_wtf import CsrfProtect
import logging
from logging.handlers import RotatingFileHandler

app = Flask(__name__, static_folder='static')
app.config.from_object('config')

handler = RotatingFileHandler('foo.log', maxBytes=10000, backupCount=1)
handler.setLevel(logging.INFO)
app.logger.addHandler(handler)

login_manager = LoginManager(app)
login_manager.login_view = '/login'
login_manager.login_message = 'Пожалуйста, войдите для доступа к этой странице.'

mongo = PyMongo(app)

CsrfProtect(app)

Compress(app)

from app.models import User

@login_manager.user_loader
def load_user(user_id):
    return User.get_by_id(user_id)

from app import views
