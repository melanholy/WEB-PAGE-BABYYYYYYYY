import datetime
import time
import os
from app import app, mongo
from app.models import User
from app.forms import LoginForm, RegisterForm, FeedbackForm, EditFeedbackForm
from flask import render_template, send_from_directory, redirect, request, \
                  flash, send_file, jsonify
from flask_login import login_required, login_user, logout_user, current_user

SITE_PAGES = {'index', 'stuff', 'images', 'contacts', 'skills'}

def render_with_visits(*args, **kwargs):
    now = datetime.datetime.now()
    beginning_of_day = datetime.datetime.combine(now.date(), datetime.time(0))
    passed_today = (now - beginning_of_day).seconds
    visits_today = mongo.db.requests.find({
        'address': request.remote_addr,
        'time': {'$gt': time.time() - passed_today}
    }).count()
    visits_total = mongo.db.requests.find().count()
    last_visit = mongo.db.requests.find_one({
        'address': request.remote_addr,
        'path': request.path,
    }, sort=[('$natural', -1)])
    if last_visit:
        last_visit = datetime.datetime.fromtimestamp(
            last_visit['time']
        ).strftime('%Y-%m-%d %H:%M:%S') + ' UTC'
    else:
        last_visit = 'не было'
    return render_template(
        *args, **kwargs,
        visits_today=visits_today,
        last_visit=last_visit,
        visits_total=visits_total,
        time=time.time()
    )

@app.after_request
def after_request(response):
    mongo.db.requests.save({
        'time': int(time.time()),
        'address': request.remote_addr,
        'path': request.path
    })

    response.headers['Server'] = 'SUPA-DUPA-SERVAH'
    return response

@app.route('/robots.txt')
def robots():
    return send_from_directory(app.static_folder, 'robots.txt')

@app.errorhandler(404)
def page_not_found(error):
    return render_with_visits('404.html', title='Четыреста четыре'), 404

@app.route('/')
@app.route('/index')
def index():
    if request.path == '/':
        return redirect('/index')
    return render_with_visits('index.html', title='Обо мне',)

@app.route('/login', methods=['POST', 'GET'])
def login():
    form = LoginForm(request.form)
    if request.method == 'POST' and form.validate():
        user = User(form.username.data)
        if user.validate(form.password.data):
            login_user(user)
            return request.args.get('next') or redirect('/')
        flash('Неверный логин или пароль.')

    return render_with_visits('login.html', title='Вход', form=form)

@app.route('/register', methods=['POST', 'GET'])
def register():
    form = RegisterForm(request.form)
    if request.method == 'POST' and form.validate():
        if User.register_user(form.username.data, form.password.data):
            return redirect('/login')
        flash('Пользователь с таким именем уже зарегистрирован.')

    return render_with_visits('register.html', title='Регистрация', form=form)

@app.route('/leave_feedback/<page>', methods=['POST', 'GET'])
@login_required
def leave_feedback(page):
    if page not in SITE_PAGES:
        return render_with_visits('404.html', title='Четыреста четыре'), 404
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

    return render_with_visits('leave_feedback.html', title='Оставить отзыв', form=form)

@app.route('/feedback/<page>')
def feedback(page):
    if page not in SITE_PAGES:
        return render_with_visits('404.html', title='Четыреста четыре'), 404
    records = [x for x in mongo.db.feedback.find({'page': page}, sort=[('$natural', -1)])]
    return render_with_visits('feedback.html', title='Отзывы', feedback=records)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect('/')

@app.route('/user', methods=['POST', 'GET'])
@login_required
def user_page():
    form = EditFeedbackForm()
    cursor = mongo.db.feedback.find({'from': current_user.username})
    return render_with_visits('user.html', title='Настройки', feedback=cursor, form=form)

@app.route('/stuff')
def stuff():
    requests = [x for x in mongo.db.requests.find()]
    for req in requests:
        req['time'] = datetime.datetime.fromtimestamp(
            req['time']
        ).strftime('%Y-%m-%d %H:%M:%S') + ' UTC'
    return render_with_visits('stuff.html', title='Штуки', requests=requests)

@app.route('/images/<image>')
def image(image):
    path = os.path.abspath('app/images/' + image)
    if not os.path.isfile(path):
        return render_with_visits('404.html', title='Четыреста четыре'), 404
    return send_file(path, mimetype='image/jpeg')

@app.route('/gallery/<img_id>')
@app.route('/gallery')
def gallery(img_id = None):
    min_images = sorted(['/images/' + x for x in os.listdir('app/images') if x.startswith('min')])
    images = sorted(['/images/' + x for x in os.listdir('app/images') if not x.startswith('min')])
    print(images)
    form = EditFeedbackForm()
    return render_with_visits(
        'gallery.html', title='Картиночки',
        images=images, min_images=min_images, form=form
    )

@app.route('/comments')
def load_comments():
    if not 'filename' in request.args:
        return 'атата'
    picture = request.args['filename']
    comments = mongo.db.comments.find_one({'filename': picture})
    if not comments:
        return jsonify([])

    return jsonify(comments['comments'])

@app.route('/comment', methods=['POST'])
def comment():
    form = EditFeedbackForm()
    if current_user.is_authenticated and form.validate_on_submit():
        if not mongo.db.comments.find_one({'filename': form.id_.data}):
            path = os.path.abspath('app/images/' + form.id_.data)
            if not os.path.isfile(path):
                return 'атата'
            else:
                mongo.db.comments.save({'filename': form.id_.data, 'comments': []})
        cur_time = datetime.datetime.fromtimestamp(
            time.time()
        ).strftime('%Y-%m-%d %H:%M:%S') + ' UTC'
        mongo.db.comments.update(
            {'filename': form.id_.data},
            {'$push': {'comments': {'date': cur_time, 'text': form.text.data, 'author': current_user.username}}}
        )
        return 'ok'
    return 'атата'
