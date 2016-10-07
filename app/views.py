import datetime
import time
import os
import io
import re
import json
from functools import wraps, update_wrapper
from app import app, mongo
from app.models import User
from app.forms import LoginForm, RegisterForm, FeedbackForm, EditFeedbackForm
from flask import render_template, send_from_directory, redirect, request, \
                  flash, send_file, make_response
from flask_login import login_required, login_user, logout_user, current_user
from wand.image import Image
from wand.drawing import Drawing, Color
from bson.objectid import ObjectId
from jinja2 import escape

HACK_DETECTED_MSG = 'Ваша попытка взлома зарегистрирована и направлена куда надо.'
BLOCKED_USERS = {}
IP_RE = re.compile(r'^(\d{1,3}\.){3}\d{1,3}$')
B_TAG = re.compile(r'&lt;b&gt;(.+?)&lt;/b&gt;')
I_TAG = re.compile(r'&lt;i&gt;(.+?)&lt;/i&gt;')
IMG_TAG = re.compile(r'&lt;img src=&#34;(.+?)&#34;&gt;')
BR_TAG = re.compile(r'&lt;br&gt;')

@app.after_request
def after_request(response):
    response.headers['Server'] = 'supa dupa servah'
    return response

@app.route('/visit', methods=['POST'])
def visit():
    if 'ss' not in request.form or 'path' not in request.form \
        or 'ua' not in request.form:
        return HACK_DETECTED_MSG
    if not request.form['path'][1:] in [x.endpoint for x in app.url_map.iter_rules()]:
        return HACK_DETECTED_MSG
    if BLOCKED_USERS.get(request.remote_addr) and \
       time.time() - BLOCKED_USERS[request.remote_addr] < 120:
        return 'ok'
    if BLOCKED_USERS.get(request.remote_addr):
        del BLOCKED_USERS[request.remote_addr]

    recent_hits_count = mongo.db.hits.find({
        'time': {'$gt': time.time() - 10},
        'address': request.remote_addr
    }).count()
    if recent_hits_count > 10:
        BLOCKED_USERS[request.remote_addr] = time.time()
        return 'ok'

    mongo.db.hits.save({
        'time': int(time.time()),
        'address': request.remote_addr,
        'path': request.form['path'],
        'ss': request.form['ss'],
        'ua': request.form['ua']
    })

    last_record = mongo.db.visits.find_one(
        {'address': request.remote_addr},
        sort=[('$natural', -1)]
    )
    if not last_record or time.time() - last_record['time'] > 1800:
        mongo.db.visits.save({
            'address': request.remote_addr,
            'time': int(time.time())
        })
    return 'ok'

@app.route('/robots.txt')
def robots():
    return send_from_directory(app.static_folder, 'robots.txt')

@app.route('/404')
def not_found():
    return render_template('404.html', title='Четыреста четыре'), 404

@app.errorhandler(404)
def page_not_found(error):
    return redirect('/404')

@app.errorhandler(400)
@app.errorhandler(403)
@app.errorhandler(405)
def error(error):
    return HACK_DETECTED_MSG, error.code

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
            flash('Теперь вы можете войти с указанными данными.')
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

def unescape_allowed_tags(text):
    text = IMG_TAG.sub(r'<img src="\1" style="max-width: 360px;">', text)
    text = B_TAG.sub(r'<b>\1</b>', text)
    text = BR_TAG.sub(r'<br>', text)
    text = I_TAG.sub(r'<i>\1</i>', text)
    return text

@app.route('/feedback')
def feedback():
    records = [x for x in mongo.db.feedback.find()]
    for record in records:
        record['text'] = unescape_allowed_tags(str(escape(record['text'])))
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
    if request.method == 'POST' and form.validate():
        record = mongo.db.feedback.find_one({'_id': ObjectId(form.id_.data)})
        if record and record['from'] == current_user.username:
            mongo.db.feedback.update(
                {'_id': ObjectId(form.id_.data)},
                {'$set': {'text': form.text.data}}
            )
        else:
            return HACK_DETECTED_MSG
    cursor = mongo.db.feedback.find({'from': current_user.username})
    return render_template('user.html', title='Настройки', feedback=cursor, form=form)

@app.route('/stuff')
def stuff():
    if 'filter' in request.args:
        if not IP_RE.match(request.args['filter']):
            return HACK_DETECTED_MSG
        requests = [x for x in mongo.db.hits.find({'address': request.args['filter']})]
    else:
        requests = [x for x in mongo.db.hits.find()]
    for req in requests:
        req['time'] = datetime.datetime.fromtimestamp(
            req['time']
        ).strftime('%Y-%m-%d %H:%M:%S') + ' UTC'
    return render_template('stuff.html', title='Штуки', requests=requests)

@app.route('/images/<image>')
def get_image(image):
    path = os.path.abspath('app/images/' + image)
    if not os.path.isfile(path) or (not path.endswith('.png') and not path.endswith('.jpg')):
        return HACK_DETECTED_MSG
    return send_file(path, mimetype='image/jpeg')

@app.route('/gallery/<img_id>')
@app.route('/gallery')
def gallery(img_id=None):
    if img_id and not img_id.isdigit():
        return HACK_DETECTED_MSG
    min_images = sorted(['/images/' + x for x in os.listdir('app/images') if x.startswith('min')])
    images = sorted(['/images/' + x for x in os.listdir('app/images') if not x.startswith('min')])
    if img_id and int(img_id) >= len(images):
        return HACK_DETECTED_MSG
    form = EditFeedbackForm()
    return render_template(
        'gallery.html', title='Картиночки',
        images=images, min_images=min_images, form=form
    )

@app.route('/comments')
def load_comments():
    if not 'filename' in request.args:
        return HACK_DETECTED_MSG
    picture = request.args['filename']
    record = mongo.db.comments.find_one({'filename': picture})

    if not record:
        return '[]'

    comments = record['comments']
    for com in comments:
        com['text'] = escape(com['text'])
        com['author'] = escape(com['author'])

    return json.dumps(comments)

@app.route('/comment', methods=['POST'])
@login_required
def comment():
    form = EditFeedbackForm()
    if form.validate_on_submit():
        if not mongo.db.comments.find_one({'filename': form.id_.data}):
            path = os.path.abspath('app/images/' + form.id_.data)
            if not os.path.isfile(path) or (not path.endswith('.png') and \
               not path.endswith('.jpg')):
                return HACK_DETECTED_MSG
            else:
                mongo.db.comments.save({'filename': form.id_.data, 'comments': []})
        cur_time = datetime.datetime.fromtimestamp(
            time.time()
        ).strftime('%Y-%m-%d %H:%M:%S') + ' UTC'
        mongo.db.comments.update(
            {'filename': form.id_.data},
            {'$push': {'comments': {
                'date': cur_time,
                'text': form.text.data,
                'author': current_user.username
            }}}
        )
        if '<img' in form.text.data or '<script' in form.text.data:
            return HACK_DETECTED_MSG
        return 'ok'
    return HACK_DETECTED_MSG

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
    if not 'path' in request.args or not 'tz' in request.args:
        return HACK_DETECTED_MSG
    if not request.args['tz'].lstrip("-").isdigit():
        return HACK_DETECTED_MSG
    timezone = int(request.args['tz'])

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
            last_hits[1]['time'] - timezone * 60
        ).strftime('%Y-%m-%d %H:%M:%S')
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
    last_hit = 'Последнее посещение страницы: {}'.format(last_hit)

    width = 270
    height = 34
    if request.remote_addr not in BLOCKED_USERS:
        text = '\n'.join([visits, hits, last_hit])
    else:
        text = 'ДОНАКРУЧИВАЛСЯ'

    data = io.BytesIO()
    with Image(width=width, height=height) as img:
        with Drawing() as draw:
            draw.font_size = 10
            draw.fill_color = Color('rgb(220, 220, 220)')
            draw.text(0, 10, text)
            draw(img)
        with img.convert('png') as converted:
            converted.save(data)

    data.seek(0)
    return send_file(data, mimetype='image/png')

@app.route('/contacts')
def contacts():
    return render_template('contacts.html', title='Контакты')
