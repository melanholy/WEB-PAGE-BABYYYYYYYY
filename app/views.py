from app import app, mongo
from app.models import User
from app.forms import LoginForm, RegisterForm, FeedbackForm, EditFeedbackForm
from flask import render_template, send_from_directory, redirect, url_for, request
from flask_login import login_required, login_user, logout_user, current_user
import datetime

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
    print(current_user)
    print(dir(current_user))
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

@app.route('/leave_feedback', methods=['POST', 'GET'])
@login_required
def leave_feedback():
    form = FeedbackForm(request.form)
    if request.method == 'POST' and form.validate():
        mongo.db.feedback.save({
            'from': current_user.username,
            'text': form.text.data,
            'date': datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
            'age': form.age.data
        })
        return redirect('/feedback')

    return render_template('leave_feedback.html', form=form)

@app.route('/feedback')
def feedback():
    feedback = reversed([x for x in mongo.db.feedback.find()])
    return render_template('feedback.html', feedback=feedback)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect('/')

@app.route('/user')
@login_required
def user():
    form = EditFeedbackForm()
    print(repr(form.text))
    feedback = mongo.db.feedback.find({'from': current_user.username})
    return render_template('user.html', feedback=feedback, form=form)
