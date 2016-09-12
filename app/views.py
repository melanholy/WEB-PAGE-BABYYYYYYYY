from app import app
from app.models import User
from app.forms import LoginForm, RegisterForm
from flask import render_template, send_from_directory, redirect, url_for, request
from flask_login import login_required, login_user, logout_user

@app.after_request
def hide_server(response):
    response.headers['Server'] = ''
    return response

@app.route('/robots.txt')
def robots():
    return send_from_directory(app.static_folder, 'robots.txt')

@app.route('/css/style.css')
def style():
    return send_from_directory('templates', 'style.css')

@app.route('/favicon.ico')
def favicon():
    return redirect(url_for('static', filename='favicon.ico'))

@app.errorhandler(404)
def page_not_found(error):
    return render_template('404.html'), 404

@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html')

@app.route('/login', methods=['POST', 'GET'])
def login():
    form = LoginForm(request.form)
    if request.method == 'POST' and form.validate():
        user = User(form.username.data)
        if user.validate(form.password.data):
            login_user(user)
            return request.args.get('next') or redirect('/')

    return render_template('login.html', form=form)

@app.route('/register', methods=['POST', 'GET'])
def register():
    form = RegisterForm(request.form)
    if request.method == 'POST' and form.validate():
        if User.register_user(form.username.data, form.password.data):
            return redirect('/login')

    return render_template('register.html', form=form)

@app.route('/feedback')
@login_required
def feedback():
    return 'lala'

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect('/')
