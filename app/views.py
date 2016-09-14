from app import app, mongo
from app.models import User
from app.forms import LoginForm, RegisterForm, FeedbackForm, EditFeedbackForm
from flask import render_template, send_from_directory, redirect, url_for, request, \
                  flash
from flask_login import login_required, login_user, logout_user, current_user
import datetime

SITE_PAGES = {'index', 'stuff', 'images', 'contacts', 'skills'}

@app.after_request
def after_request(response):
    if not request.path.startswith('/static'):
        if current_user is User:
            user = current_user.username
        
        mongo.db.requests.save({
            'time': datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
            'address': request.remote_addr,
            'path': request.path
        })
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
    return render_template('404.html', title='Четыреста четыре'), 404

@app.route('/')
@app.route('/index')
def index():
    if request.path == '/':
        return redirect('/index')
    return render_template('index.html', title='Обо мне',)

@app.route('/login', methods=['POST', 'GET'])
def login():
    form = LoginForm(request.form)
    if request.method == 'POST' and form.validate():
        user = User(form.username.data)
        if user.validate(form.password.data):
            login_user(user)
            return request.args.get('next') or redirect('/')
        flash('Неверный логин или пароль.')

    return render_template('login.html', title='Вход', form=form)

@app.route('/register', methods=['POST', 'GET'])
def register():
    form = RegisterForm(request.form)
    if request.method == 'POST' and form.validate():
        if User.register_user(form.username.data, form.password.data):
            return redirect('/login')
        flash('Пользователь с таким именем уже зарегистрирован.')

    return render_template('register.html', title='Регистрация', form=form)

@app.route('/leave_feedback/<page>', methods=['POST', 'GET'])
@login_required
def leave_feedback(page):
    if page not in SITE_PAGES:
        return render_template('404.html', title='Четыреста четыре'), 404
    form = FeedbackForm(request.form)
    if request.method == 'POST' and form.validate():
        mongo.db.feedback.save({
            'page': page,
            'from': current_user.username,
            'text': form.text.data,
            'date': datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
            'age': form.age.data
        })
        return redirect('/feedback/' + page)

    return render_template('leave_feedback.html', title='Оставить отзыв', form=form)

@app.route('/feedback/<page>')
def feedback(page):
    if page not in SITE_PAGES:
        return render_template('404.html', title='Четыреста четыре'), 404
    feedback = [x for x in mongo.db.feedback.find({'page': page}, sort=[('$natural', -1)])]
    return render_template('feedback.html', title='Отзывы', feedback=feedback)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect('/')

@app.route('/user', methods=['POST', 'GET'])
@login_required
def user():
    form = EditFeedbackForm()
    feedback = mongo.db.feedback.find({'from': current_user.username})
    return render_template('user.html', title='Настройки', feedback=feedback, form=form)

@app.route('/stuff')
def stuff():
    requests = mongo.db.requests.find()
    return render_template('stuff.html', title='Штуки', requests=requests)
