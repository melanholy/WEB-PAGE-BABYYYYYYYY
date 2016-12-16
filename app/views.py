import datetime
import time
import os
import io
import re
import json
import app
from functools import wraps, update_wrapper
from app.models import User
from app.forms import LoginForm, RegisterForm, FeedbackForm, EditFeedbackForm, \
                      CommentForm, DeleteFeedbackForm
from flask import render_template, send_from_directory, redirect, request, \
                  flash, send_file, make_response
from flask_login import login_required, login_user, logout_user, current_user
from wand.image import Image
from wand.drawing import Drawing, Color
from bson.objectid import ObjectId
from jinja2 import escape

HACK_DETECTED_MSG = 'Ваша попытка взлома зарегистрирована и направлена куда надо.'
BLOCKED_USERS = {}
LAST_FEEDBACK = {}
IP_RE = re.compile(r'^(\d{1,3}\.){3}\d{1,3}$')
B_TAG = re.compile(r'&lt;b&gt;(.+?)&lt;/b&gt;')
I_TAG = re.compile(r'&lt;i&gt;(.+?)&lt;/i&gt;')
IMG_TAG = re.compile(r'&lt;img src=&#34;(.+?)&#34;&gt;')
BR_TAG = re.compile(r'&lt;br&gt;')
SS_RE = re.compile(r'^\d{1,5}x\d{1,5}$')

def get_time_str(timestamp):
    if 'tz' in request.cookies:
        timezone = int(request.cookies['tz'])
        return datetime.datetime.fromtimestamp(
            timestamp - timezone * 60
        ).strftime('%Y-%m-%d %H:%M:%S')
    return datetime.datetime.fromtimestamp(
        timestamp
    ).strftime('%Y-%m-%d %H:%M:%S') + ' UTC'

@app.app.after_request
def after_request(response):
    response.headers['Server'] = 'supa dupa servah'

    if 'tz' in request.cookies and not request.cookies['tz'].lstrip("-").isdigit() or \
       'ss' in request.cookies and not SS_RE.match(request.cookies['ss']):
        return make_response(HACK_DETECTED_MSG)

    if request.path != '/stats' and request.path in app.url_map:
        register_request()

    return response

def register_request():
    if BLOCKED_USERS.get(request.remote_addr) and \
       time.time() - BLOCKED_USERS[request.remote_addr] < 120:
        return
    if BLOCKED_USERS.get(request.remote_addr):
        del BLOCKED_USERS[request.remote_addr]

    recent_hits_count = app.mongo.db.hits.count({
        'time': {'$gt': time.time() - 10},
        'address': request.remote_addr
    })
    if recent_hits_count > 10:
        BLOCKED_USERS[request.remote_addr] = time.time()
        return

    app.mongo.db.hits.insert_one({
        'time': int(time.time()),
        'address': request.remote_addr,
        'path': request.path,
        'ss': request.cookies.get('ss'),
        'ua': request.user_agent.string
    })

    last_record = app.mongo.db.visits.find_one(
        {'address': request.remote_addr},
        sort=[('$natural', -1)]
    )
    if not last_record or time.time() - last_record['time'] > 1800:
        app.mongo.db.visits.insert_one({
            'address': request.remote_addr,
            'time': int(time.time())
        })

@app.app.route('/robots.txt')
def robots():
    return send_from_directory(app.app.static_folder, 'robots.txt')

@app.app.route('/404')
def not_found():
    return render_template('404.html', title='Четыреста четыре'), 404

@app.app.errorhandler(404)
def error404(error):
    return redirect('/404')

@app.app.errorhandler(400)
@app.app.errorhandler(403)
@app.app.errorhandler(405)
def handle_error(error):
    return HACK_DETECTED_MSG, error.code

@app.app.route('/')
def index():
    return render_template('index.html', title='Обо мне')

@app.app.route('/login', methods=['POST', 'GET'])
def login():
    form = LoginForm(request.form)
    if request.method == 'POST' and form.validate():
        user = User(form.username.data)
        if user.validate(form.password.data):
            login_user(user)
            if 'next' in request.args and request.args['next'] in app.url_map:
                return redirect(request.args['next'])
            return redirect('/')
        flash('Неверный логин или пароль.')

    return render_template('login.html', title='Вход', form=form)

@app.app.route('/register', methods=['POST', 'GET'])
def register():
    form = RegisterForm(request.form)
    if request.method == 'POST' and form.validate():
        if User.register_user(form.username.data, form.password.data):
            flash('Теперь вы можете войти с указанными данными.')
            return redirect('/login')
        flash('Пользователь с таким именем уже зарегистрирован.')

    return render_template('register.html', title='Регистрация', form=form)

@app.app.route('/leave_feedback', methods=['POST', 'GET'])
@login_required
def leave_feedback():
    form = FeedbackForm(request.form)
    if request.method == 'POST' and form.validate():
        if time.time() - LAST_FEEDBACK.get(current_user.username, 0) > 43200:
            LAST_FEEDBACK[current_user.username] = time.time()
            app.mongo.db.feedback.insert_one({
                'from': current_user.username,
                'text': form.text.data,
                'date': int(time.time()),
                'age': form.age.data
            })
            return redirect('/feedback')
        flash('Разрешается отправлять отзывы только один раз в 12 часов.')

    return render_template('leave_feedback.html', title='Оставить отзыв', form=form)

def unescape_allowed_tags(text):
    text = IMG_TAG.sub(r'''<div class="col-sm-6 col-md-4" style="float: none; padding: 0;">
                               <img src="\1" class="img-responsive">
                           </div>''', text)
    text = B_TAG.sub(r'<strong>\1</strong>', text)
    text = BR_TAG.sub(r'<br>', text)
    text = I_TAG.sub(r'<em>\1</em>', text)
    return text

@app.app.route('/feedback')
def feedback():
    records = [x for x in app.mongo.db.feedback.find()]
    for record in records:
        record['text'] = unescape_allowed_tags(str(escape(record['text'])))
        if 'date' in record and isinstance(record['date'], int):
            record['date'] = get_time_str(record['date'])
    return render_template('feedback.html', title='Отзывы', feedback=records)

@app.app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect('/')

@app.app.route('/user', methods=['POST', 'GET'])
@login_required
def user_page():
    edit_form = EditFeedbackForm()
    del_form = DeleteFeedbackForm()
    if request.method == 'POST' and 'edit_id' in request.form and edit_form.validate():
        id_ = ObjectId(edit_form.edit_id.data)
        record = app.mongo.db.feedback.find_one({'_id': id_})
        if record and record['from'] == current_user.username:
            app.mongo.db.feedback.update(
                {'_id': id_},
                {'$set': {'text': edit_form.edit_text.data}}
            )
        else:
            return HACK_DETECTED_MSG
    elif request.method == 'POST' and 'del_id' in request.form and del_form.validate():
        id_ = ObjectId(del_form.del_id.data)
        record = app.mongo.db.feedback.find_one({'_id': id_})
        if record and record['from'] == current_user.username:
            app.mongo.db.feedback.delete_one({'_id': id_})
        else:
            return HACK_DETECTED_MSG
    records = [x for x in app.mongo.db.feedback.find({'from': current_user.username})]
    for record in records:
        if 'date' in record and isinstance(record['date'], int):
            record['date'] = get_time_str(record['date'])
    return render_template(
        'user.html', title='Настройки', feedback=records,
        edit_form=edit_form, del_form=del_form
    )

@app.app.route('/stuff')
def stuff():
    if 'filter' in request.args:
        if not IP_RE.match(request.args['filter']):
            return HACK_DETECTED_MSG
        requests = [x for x in app.mongo.db.hits.find({'address': request.args['filter']})]
    else:
        requests = [x for x in app.mongo.db.hits.find()]
    for req in requests:
        req['time'] = get_time_str(req['time'])
    return render_template('stuff.html', title='Штуки', requests=requests)

@app.app.route('/images/<image>')
def get_image(image):
    path = os.path.abspath('app/images/' + image)
    if not os.path.isfile(path) or (not path.endswith('.png') and not path.endswith('.jpg')):
        return HACK_DETECTED_MSG
    return send_file(path, mimetype='image/jpeg')

@app.app.route('/gallery/<img_id>')
@app.app.route('/gallery')
def gallery(img_id=None):
    if img_id and not img_id.isdigit():
        return HACK_DETECTED_MSG

    min_images = ['/images/' + x for x in os.listdir('app/images') if x.startswith('min')]
    images = ['/images/' + x for x in os.listdir('app/images') if not x.startswith('min')]
    if img_id and int(img_id) >= len(images):
        return HACK_DETECTED_MSG
    form = CommentForm()
    return render_template(
        'gallery.html', title='Картиночки',
        images=sorted(images), min_images=sorted(min_images), form=form
    )

def get_comments(picture):
    record = app.mongo.db.comments.find_one({'filename': picture})
    if not record:
        return '[]'

    comments = record['comments']
    for com in comments:
        com['text'] = escape(com['text'])
        com['author'] = escape(com['author'])
        if isinstance(com['date'], int):
            com['date'] = get_time_str(com['date'])

    return json.dumps(comments)

@app.app.route('/comments')
def load_comments():
    if not 'filename' in request.args:
        return HACK_DETECTED_MSG
    picture = request.args['filename']
    return get_comments(picture)

@app.app.route('/comment', methods=['POST'])
@login_required
def comment():
    form = CommentForm()
    if form.validate_on_submit():
        if not app.mongo.db.comments.find_one({'filename': form.id_.data}):
            path = os.path.abspath('app/images/' + form.id_.data)
            if not os.path.isfile(path) or (not path.endswith('.png') and \
               not path.endswith('.jpg')):
                return HACK_DETECTED_MSG
            else:
                app.mongo.db.comments.insert_one({'filename': form.id_.data, 'comments': []})
        app.mongo.db.comments.update(
            {'filename': form.id_.data},
            {'$push': {'comments': {
                'date': int(time.time()),
                'text': form.text.data,
                'author': current_user.username
            }}}
        )
        if '<img' in form.text.data or '<script' in form.text.data:
            return HACK_DETECTED_MSG
        return get_comments(form.id_.data)
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

def get_visit_info_str():
    now = datetime.datetime.now()
    beginning_of_day = datetime.datetime.combine(now.date(), datetime.time(0))
    passed_today = (now - beginning_of_day).seconds

    visits_today = str(app.mongo.db.visits.count({
        'time': {'$gt': time.time() - passed_today}
    }))
    visits_total = str(app.mongo.db.visits.count())

    hits_today = str(app.mongo.db.hits.count({
        'time': {'$gt': time.time() - passed_today}
    }))
    hits_total = str(app.mongo.db.hits.count())
    last_hits = [x for x in app.mongo.db.hits.find({
        'address': request.remote_addr,
        'path': request.args['path']
    }, sort=[('$natural', -1)], limit=2)]
    if len(last_hits) > 1:
        last_hit = get_time_str(last_hits[1]['time'])
    else:
        last_hit = 'не было'

    visits = 'Всего посещений:  {} | Сегодня: {}'.format(
        visits_total + ' '*(4 - len(visits_total)),
        visits_today
    )
    hits = 'Всего просмотров: {} | Сегодня: {}'.format(
        hits_total + ' '*(4 - len(hits_total)),
        hits_today
    )
    last_hit = 'Последнее посещение страницы: {}'.format(last_hit)

    return visits, hits, last_hit

@app.app.route('/stats')
@nocache
def stats():
    if not 'path' in request.args:
        return HACK_DETECTED_MSG

    if request.remote_addr not in BLOCKED_USERS:
        text = '\n'.join(get_visit_info_str())
    else:
        text = 'ДОНАКРУЧИВАЛСЯ'

    data = io.BytesIO()
    with Image(width=300, height=34) as img:
        with Drawing() as draw:
            draw.font_size = 12
            draw.font = 'UbuntuMono-R.ttf'
            draw.fill_color = Color('rgb(230, 230, 230)')
            for index, line in enumerate(text.split('\n')):
                draw.text(0, 10 + 11 * index, line)
            draw(img)
        with img.convert('png') as converted:
            converted.save(data)

    data.seek(0)
    return send_file(data, mimetype='image/png')

@app.app.route('/like', methods=['GET', 'POST'])
def like():
    print(request.form)
    if request.method == 'POST' and 'filename' in request.form:
        record = app.mongo.db.likes.find_one({ 'filename': request.form['filename'] })
        if not record:
            app.mongo.db.likes.insert_one({
                'filename': request.form['filename'],
                'count': 0
            })
            count = 0
        else:
            count = record['count']
        count += 1
        app.mongo.db.likes.update(
            { 'filename': request.form['filename'] },
            { '$set': { 'count': count } }
        )

        return str(count)
    elif request.method == 'GET' and 'filename' in request.args:
        record = app.mongo.db.likes.find_one({ 'filename': request.args['filename'] })
        if not record:
            count = 0
        else:
            count = record['count']

        return str(count)
