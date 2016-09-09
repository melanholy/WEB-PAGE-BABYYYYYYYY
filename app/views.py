from app import app
from flask import render_template, send_from_directory

@app.after_request
def apply_caching(response):
    print('lalal')
    response.headers['Server'] = ''
    return response

@app.route('/robots.txt')
def robots():
    return send_from_directory(app.static_folder, 'robots.txt')

@app.route('/css/style.css')
def style():
    return send_from_directory('templates', 'style.css')

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html')
