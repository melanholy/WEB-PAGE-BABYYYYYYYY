from flask import Flask, url_for
from flask_sslify import SSLify

app = Flask(__name__, static_folder='static')
app.config.from_object('config')
app.add_url_rule('/favicon.ico', redirect_to=url_for('static', filename='favicon.ico'))

sslify = SSLify(app)

from app import views
