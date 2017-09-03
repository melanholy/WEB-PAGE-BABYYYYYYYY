from app import mongo
import bcrypt

class User:
    def __init__(self, username):
        self.username = username

    def validate(self, password):
        user = mongo.app.users.find_one({'username': self.username})
        if not user:
            return False

        stored_hash = user['password']
        return bcrypt.hashpw(bytes(password, 'utf-8'), stored_hash) == stored_hash

    @staticmethod
    def get_by_id(id_):
        user = mongo.app.users.find_one({'username': id_})
        if not user:
            return None

        return User(user['username'])

    @staticmethod
    def register_user(username, password):
        if mongo.app.users.find_one({'username': username}):
            return False

        mongo.app.users.save({
            'username': username,
            'password': bcrypt.hashpw(bytes(password, 'utf-8'), bcrypt.gensalt(10))
        })

        return True
