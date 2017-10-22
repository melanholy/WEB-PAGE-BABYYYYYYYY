import asyncio
import uvloop
from sanic import Sanic
from sanic_auth import Auth
from motor.motor_asyncio import AsyncIOMotorClient

asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
mongo = AsyncIOMotorClient('mongodb://localhost:27017')

app = Sanic(__name__)
app.config.from_pyfile('app/config.py')
app.static('/static', 'app/static')
auth = Auth(app)

with open('./app/index.html') as f:
    PAGE_TEMPLATE = f.read()
BLOCKED_USERS = {}
LAST_FEEDBACK = {}

from app import views
