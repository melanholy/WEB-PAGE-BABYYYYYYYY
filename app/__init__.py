
from flask import Flask
from flask_sslify import SSLify
from flask_login import LoginManager
from flask_pymongo import PyMongo

app = Flask(__name__, static_folder='static')
app.config.from_object('config')

login_manager = LoginManager(app)
login_manager.login_view = '/login'

mongo = PyMongo(app)

sslify = SSLify(app)

from app.models import User

@login_manager.user_loader
def load_user(user_id):
    return User.get_by_id(user_id)

from app import views
