import time
import re
import datetime

from app import mongo, BLOCKED_USERS

B_TAG = re.compile(r'&lt;b&gt;(.+?)&lt;/b&gt;')
I_TAG = re.compile(r'&lt;i&gt;(.+?)&lt;/i&gt;')
IMG_TAG = re.compile(r'&lt;img src=&#34;(.+?)&#34;&gt;')
BR_TAG = re.compile(r'&lt;br&gt;')

def unescape_allowed_tags(text):
    text = IMG_TAG.sub(r'''<div class="col-sm-6 col-md-4" style="float: none; padding: 0;">
                               <img src="\1" class="img-responsive">
                           </div>''', text)
    text = B_TAG.sub(r'<strong>\1</strong>', text)
    text = BR_TAG.sub(r'<br>', text)
    text = I_TAG.sub(r'<em>\1</em>', text)

    return text

def get_time_str(timezone, timestamp):
    if timezone:
        shift = int(timezone) * 60
    else:
        shift = 0

    return datetime.datetime.fromtimestamp(
        timestamp - shift
    ).strftime('%Y-%m-%d %H:%M:%S') + '' if shift else ' UTC'

async def register_request(request):
    if BLOCKED_USERS.get(request.ip) and time.time() - BLOCKED_USERS[request.ip] < 600:
        return
    if BLOCKED_USERS.get(request.ip):
        del BLOCKED_USERS[request.ip]

    recent_hits_count = await mongo.app.hits.count({
        'time': {'$gt': time.time() - 20},
        'address': request.ip
    })
    if recent_hits_count > 60:
        BLOCKED_USERS[request.ip] = time.time()
        return

    await mongo.app.hits.insert_one({
        'time': int(time.time()),
        'address': request.ip,
        'path': request.path,
        'ss': request.cookies.get('ss'),
        'ua': request.user_agent.string
    })

    last_record = await mongo.app.visits.find_one(
        {'address': request.ip},
        sort=[('$natural', -1)]
    )
    if not last_record or time.time() - last_record['time'] > 1800:
        await mongo.app.visits.insert_one({
            'address': request.ip,
            'time': int(time.time())
        })

async def get_visit_info(request):
    beginning_of_day = datetime.datetime.combine(
        datetime.datetime.now(),
        datetime.datetime.time(0)
    ).timestamp()

    visits_today = str(await mongo.app.visits.count({
        'time': {'$gt': beginning_of_day}
    }))
    visits_total = str(await mongo.app.visits.count())

    hits_today = str(await mongo.app.hits.count({
        'time': {'$gt': beginning_of_day}
    }))
    hits_total = str(await mongo.app.hits.count())
    last_hits = [x for x in await mongo.app.hits.find({
        'address': request.ip,
        'path': request.path
    }, sort=[('$natural', -1)], limit=2)]

    if len(last_hits) > 1:
        last_hit = get_time_str(request.cookies.get('tz'), last_hits[1]['time'])
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

    return [visits, hits, last_hit]
