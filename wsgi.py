from app import app

if __name__ == '__main__':
    app.config['SESSION_COOKIE_SECURE'] = True
    app.run()
