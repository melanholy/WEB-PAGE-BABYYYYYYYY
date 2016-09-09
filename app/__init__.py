from flask import Flask
from flask_sslify import SSLify

app = Flask(__name__, static_folder='static')
app.config.from_object('config')

sslify = SSLify(app)

from app import views
