import io
import re
from datetime import datetime
from functools import wraps

from app import app, auth, BLOCKED_USERS, PAGE_TEMPLATE
from app.actions import register_request, get_visit_info
from sanic import response
from sanic.exceptions import NotFound, ServerError
from wand.image import Image
from wand.drawing import Drawing, Color

HACK_DETECTED_MSG = 'Ваша попытка взлома зарегистрирована и направлена куда надо.'
SS_RE = re.compile(r'^\d{1,5}x\d{1,5}$')
SITE_MAP = {
    '/', '/login', '/404', '/register', '/feedback', '/leave_feedback', '/user',
    '/gallery', '/gallery/<img_id:int>', '/stuff'
}

def render(title, status=200):
    page = PAGE_TEMPLATE.format(title, '')
    return response.html(page, status=status)

def nocache():
    def decorator(view):
        @wraps(view)
        async def decorated_function(request, *args, **kwargs):
            resp = await view(request, *args, **kwargs)

            resp.headers['Last-Modified'] = datetime.now()
            resp.headers['Cache-Control'] = (
                'no-store, no-cache, must-revalidate, ' +
                'post-check=0, pre-check=0, max-age=0'
            )
            resp.headers['Pragma'] = 'no-cache'
            resp.headers['Expires'] = '-1'

            return resp

        return decorated_function

    return decorator

@app.middleware('response')
async def after_request(request, resp):
    resp.headers['Server'] = 'supa dupa servah'

    if 'tz' in request.cookies and not request.cookies['tz'].lstrip("-").isdigit() or \
       'ss' in request.cookies and not SS_RE.match(request.cookies['ss']):
        raise ServerError("", status_code=400)

    if request.uri_template in SITE_MAP:
        await register_request(request)

@app.exception(NotFound)
async def not_found_handler(request, exception):
    return response.redirect(app.url_for('not_found'))

@app.exception(ServerError)
async def handle_error(request, exception):
    return response.text(HACK_DETECTED_MSG, status=418)

@app.route('/')
async def index(request):
    return render('Обо мне')

@app.route('/404')
async def not_found(request):
    return render('Четыреста четыре', 404)

@app.route('/login')
async def login(request):
    return render('Вход')

@app.route('/register')
async def register(request):
    return render('Регистрация')

@app.route('/leave_feedback')
@auth.login_required
async def leave_feedback(request):
    return render('Оставить отзыв')

@app.route('/feedback')
async def feedback(request):
    return render('Отзывы')

@app.route('/logout')
@auth.login_required
async def logout(request):
    auth.logout_user(request)

    return response.redirect(app.url_for('index'))

@app.route('/user')
@auth.login_required
async def user_page(request):
    return render('Настройки')

@app.route('/stuff')
async def stuff(request):
    return render('Штуки')

@app.route('/gallery/<img_id:int>')
@app.route('/gallery')
async def gallery(request, img_id=None):
    return render('Картиночки')

@app.route('/stats')
@nocache()
async def stats(request):
    if not 'path' in request.args:
        raise ServerError("", status_code=400)

    if request.ip not in BLOCKED_USERS:
        info_lines = await get_visit_info(request)
    else:
        info_lines = ['ДОНАКРУЧИВАЛСЯ']

    data = io.BytesIO()
    with Image(width=300, height=34) as img:
        with Drawing() as draw:
            draw.font_size = 12
            draw.font = 'UbuntuMono-R.ttf'
            draw.fill_color = Color('rgb(230, 230, 230)')
            for i, line in enumerate(info_lines):
                draw.text(0, 10 + 11 * i, line)
            draw(img)
        with img.convert('png') as converted:
            converted.save(data)
    data.seek(0)

    return response.stream(data, content_type='image/png')
