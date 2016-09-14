from app import mongo
from flask_login import UserMixin
import bcrypt

class User(UserMixin):
    def __init__(self, username):
        self.username = username
    def get_id(self):
        return self.username

    def validate(self, password):
        user = mongo.db.users.find_one({'username': self.username})
        if not user:
            return False

        stored_hash = user['password']
        return bcrypt.hashpw(password, stored_hash) == stored_hash

    @staticmethod
    def get_by_id(id_):
        user = mongo.db.users.find_one({'username': id_})
        if not user:
            return None
        return User(user['username'])

    @staticmethod
    def register_user(username, password):
        if mongo.db.users.find_one({'username': username}):
            return False

        mongo.db.users.save({
            'username': username,
            'password': bcrypt.hashpw(password, bcrypt.gensalt(10))
        })
        return True
