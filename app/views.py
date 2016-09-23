import datetime
import time
import os
import io
from app import app, mongo
from app.models import User
from app.forms import LoginForm, RegisterForm, FeedbackForm, EditFeedbackForm
from functools import wraps, update_wrapper
from flask import render_template, send_from_directory, redirect, request, \
                  flash, send_file, jsonify, make_response
from flask_login import login_required, login_user, logout_user, current_user
from wand.image import Image
from wand.drawing import Drawing, Color

SITE_PAGES = {'index', 'stuff', 'images', 'contacts', 'skills'}

@app.after_request
def after_request(response):
    if request.method == 'GET' and not request.path.startswith('/static') and \
       not request.path.startswith('/images') and not request.path == '/stats':
        mongo.db.hits.save({
            'time': int(time.time()),
            'address': request.remote_addr,
            'path': request.path
        })
        last_record = mongo.db.visits.find_one({'address': request.remote_addr}, sort=[('$natural', -1)])
        if not last_record or time.time() - last_record['time'] > 1800:
            mongo.db.visits.save({
                'address': request.remote_addr,
                'time': int(time.time())
            })

    response.headers['Server'] = 'supa dupa servah'
    return response

@app.route('/robots.txt')
def robots():
    return send_from_directory(app.static_folder, 'robots.txt')

@app.errorhandler(404)
def page_not_found(error):
    return render_template('404.html', title='Четыреста четыре'), 404

@app.route('/')
@app.route('/index')
def index():
    if request.path == '/':
        return redirect('/index')
    return render_template('index.html', title='Обо мне')

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

    return render_template('leave_feedback.html', title='Оставить отзыв', form=form)

@app.route('/feedback')
def feedback():
    records = [x for x in mongo.db.feedback.find()]
    return render_template('feedback.html', title='Отзывы', feedback=records)

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
    return render_template('user.html', title='Настройки', feedback=cursor, form=form)

@app.route('/stuff')
def stuff():
    requests = [x for x in mongo.db.hits.find()]
    for req in requests:
        req['time'] = datetime.datetime.fromtimestamp(
            req['time']
        ).strftime('%Y-%m-%d %H:%M:%S') + ' UTC'
    return render_template('stuff.html', title='Штуки', requests=requests)

@app.route('/images/<image>')
def image(image):
    path = os.path.abspath('app/images/' + image)
    if not os.path.isfile(path):
        return render_template('404.html', title='Четыреста четыре'), 404
    return send_file(path, mimetype='image/jpeg')

@app.route('/gallery/<img_id>')
@app.route('/gallery')
def gallery(img_id = None):
    min_images = sorted(['/images/' + x for x in os.listdir('app/images') if x.startswith('min')])
    images = sorted(['/images/' + x for x in os.listdir('app/images') if not x.startswith('min')])
    form = EditFeedbackForm()
    return render_template(
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

def nocache(view):
    @wraps(view)
    def no_cache(*args, **kwargs):
        response = make_response(view(*args, **kwargs))
        response.headers['Last-Modified'] = datetime.datetime.now()
        response.headers['Cache-Control'] = (
            'no-store, no-cache, must-revalidate, ' +
            'post-check=0, pre-check=0, max-age=0'
        )
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '-1'
        return response
        
    return update_wrapper(no_cache, view)

@app.route('/stats')
@nocache
def stats():
    def multiline_text(draw, xy, text, fill, font, spacing=4):
        lines = text.split('\n')
        line_spacing = draw.textsize('A', font=font)[1] + spacing
        left, top = xy
        for idx, line in enumerate(lines):
            mask = font.getmask(line)
            ink, _ = draw._getink((144, 144, 144))
            draw.draw.draw_bitmap((left, top), mask, ink)
            top += line_spacing
            left = xy[0]

    if not request.args.get('path'):
        return 'атата'

    now = datetime.datetime.now()
    beginning_of_day = datetime.datetime.combine(now.date(), datetime.time(0))
    passed_today = (now - beginning_of_day).seconds

    visits_today = str(mongo.db.visits.find({
        'time': {'$gt': time.time() - passed_today}
    }).count())
    visits_total = str(mongo.db.visits.find().count())

    hits_today = str(mongo.db.hits.find({
        'time': {'$gt': time.time() - passed_today}
    }).count())
    hits_total = str(mongo.db.hits.find().count())
    last_hits = [x for x in mongo.db.hits.find({
        'address': request.remote_addr,
        'path': request.args['path']
    }, sort=[('$natural', -1)], limit=2)]
    if len(last_hits) > 1:
        last_hit = datetime.datetime.fromtimestamp(
            last_hits[1]['time']
        ).strftime('%Y-%m-%d %H:%M:%S') + ' UTC'
    else:
        last_hit = 'не было'

    visits = 'Всего посещений:  {} | Сегодня: {}'.format(
        visits_total + ' '*(5 - len(visits_total)),
        visits_today
    )
    hits = 'Всего просмотров: {} | Сегодня: {}'.format(
        hits_total + ' '*(5 - len(hits_total)),
        hits_today
    )
    last_hit = 'Последнее посещение этой страницы: {}'.format(last_hit)

    data = io.BytesIO()
    with Image(width=320, height=34) as img:
        with Drawing() as draw:
            draw.font_size = 10
            draw.fill_color = Color('#999')
            draw.text(0, 10, '\n'.join([visits, hits, last_hit]))
            draw(img)
        with img.convert('png') as converted:
            converted.save(data)

    data.seek(0)
    return send_file(data, mimetype='image/png')

@app.route('/contacts')
def contacts():
    return render_template('contacts.html', title='Контакты')
