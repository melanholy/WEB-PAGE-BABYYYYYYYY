import os
import time
from html import escape

from app import app, mongo, auth, LAST_FEEDBACK
from app.models import User
from app.forms import LoginForm, RegisterForm, FeedbackForm, EditFeedbackForm, \
                      CommentForm, DeleteFeedbackForm
from app.actions import get_time_str, unescape_allowed_tags
from sanic import response
from sanic.exceptions import ServerError
from bson.objectid import ObjectId

@app.route('/api/likes/<filename>')
@auth.login_required
async def like(request, filename):
    #TODO json
    return str(await mongo.app.likes.count({'filename': request.args['filename']}))

@app.route('/api/add_like', methods=['POST'])
@auth.login_required(user_keyword='current_user')
async def like(request, current_user):
    #TODO json
    if 'filename' in request.form:
        picture = request.form['filename']
        data = {
            'filename': picture,
            'user': current_user.username
        }
        record = await mongo.app.likes.find_one(data)
        if not record:
            await mongo.app.likes.insert_one(data)
        else:
            await mongo.app.likes.delete_one(data)

        return str(await mongo.app.likes.count({'filename': picture}))

    raise ServerError("", status_code=400)

async def get_comments(picture, timezone):
    record = await mongo.app.comments.find_one({'filename': picture})
    if not record:
        return []

    comments = record['comments']
    for com in comments:
        com['text'] = escape(com['text'])
        com['author'] = escape(com['author'])
        if isinstance(com['date'], int):
            com['date'] = get_time_str(timezone, com['date'])

    return comments

@app.route('/api/comments/<filename>')
async def load_comments(request, filename):
    return response.json(await get_comments(filename, request.cookies.get('tz')))

@app.route('/api/comment', methods=['POST'])
@auth.login_required(user_keyword='current_user')
async def comment(request, current_user):
    #TODO
    form = CommentForm(request)
    if form.validate():
        if not await mongo.app.comments.find_one({'filename': form.id_.data}):
            path = os.path.abspath('app/images/' + form.id_.data)
            if not os.path.isfile(path) or (not path.endswith('.png') and not path.endswith('.jpg')):
                raise ServerError("", status_code=400)
            else:
                await mongo.app.comments.insert_one({'filename': form.id_.data, 'comments': []})
        await mongo.app.comments.update(
            {'filename': form.id_.data},
            {'$push': {'comments': {
                'date': int(time.time()),
                'text': form.text.data,
                'author': current_user.username
            }}}
        )

        if '<img' in form.text.data or '<script' in form.text.data:
            raise ServerError("", status_code=400)

        return response.json(await get_comments(form.id_.data, request.cookies.get('tz')))

    raise ServerError("", status_code=400)

@app.route('/api/leave_feedback', methods=['POST'])
@auth.login_required(user_keyword='current_user')
async def leave_feedback(request, current_user):
    #TODO
    form = FeedbackForm(request)
    if form.validate():
        if time.time() - LAST_FEEDBACK.get(current_user.username, 0) > 43200:
            LAST_FEEDBACK[current_user.username] = time.time()
            await mongo.app.feedback.insert_one({
                'from': current_user.username,
                'text': form.text.data,
                'date': int(time.time()),
                'age': form.age.data
            })

            return response.redirect(app.url_for('feedback'))

        flash('Разрешается отправлять отзывы только один раз в 12 часов.')

@app.route('/api/register', methods=['POST'])
async def register(request):
    #TODO
    form = RegisterForm(request)
    if form.validate():
        if User.register_user(form.username.data, form.password.data):
            flash('Теперь вы можете войти с указанными данными.')
            return response.redirect(app.url_for('login'))
        flash('Пользователь с таким именем уже зарегистрирован.')

@app.route('/api/login', methods=['POST'])
async def login(request):
    #TODO
    form = LoginForm(request)
    if form.validate():
        user = User(form.username.data)
        if user.validate(form.password.data):
            auth.login_user(request, user)
            if 'next' in request.args and request.args['next'] in app.url_map:
                return response.redirect(request.args['next'])

            return response.redirect(app.url_for('index'))
        flash('Неверный логин или пароль.')

@app.route('/api/feedback')
async def feedback(request):
    #TODO может можно обойтись без x for x in y
    if 'from' in request.args:
        records = [x for x in await mongo.app.feedback.find()]
    else:
        records = [x for x in await mongo.app.feedback.find({'from': request.args['from']})]

    for record in records:
        if 'from' not in request.args:
            record['text'] = unescape_allowed_tags(escape(record['text']))
        if 'date' in record and isinstance(record['date'], int):
            record['date'] = get_time_str(request.cookies.get('tz'), record['date'])

    return response.json(records)

@app.route('/api/edit_feedback', methods=['POST'])
@auth.login_required(user_keyword='current_user')
async def edit_feedback(request, current_user):
    #TODO
    edit_form = EditFeedbackForm(request)
    if request.method == 'POST' and 'edit_id' in request.form and edit_form.validate():
        id_ = ObjectId(edit_form.edit_id.data)
        record = await mongo.app.feedback.find_one({'_id': id_})
        if record and record['from'] == current_user.username:
            await mongo.app.feedback.update(
                {'_id': id_},
                {'$set': {'text': edit_form.edit_text.data}}
            )
        else:
            raise ServerError("", status_code=400)

@app.route('/api/user/del_feedback', methods=['POST'])
@auth.login_required(user_keyword='current_user')
async def del_feedback(request, current_user):
    #TODO
    del_form = DeleteFeedbackForm(request)
    if del_form.validate():
        id_ = ObjectId(del_form.del_id.data)
        record = await mongo.app.feedback.find_one({'_id': id_})
        if record and record['from'] == current_user.username:
            await mongo.app.feedback.delete_one({'_id': id_})
        else:
            raise ServerError("", status_code=400)

@app.route('/stuff')
async def stuff(request):
    #TODO x for x in y
    requests = [x for x in await mongo.app.hits.find({'address': request.ip})]
    for req in requests:
        req['time'] = get_time_str(request.cookies.get('tz'), req['time'])

    return response.json(requests)

@app.route('/api/gallery/<img_id:int>')
@app.route('/api/gallery')
async def gallery(request, img_id=None):
    images = ['/images/' + x for x in os.listdir('app/images') if not x.startswith('min')]

    if img_id and img_id >= len(images):
        raise ServerError("", status_code=400)

    min_images = ['/images/' + x for x in os.listdir('app/images') if x.startswith('min')]

    return response.json({'images': images, 'min_images': min_images})
