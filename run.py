from app import app
from OpenSSL import SSL

if __name__ == '__main__':
    context = ('izalith_me.crt', 'izalith_me.key')
    app.run(debug=True, port=443, host='0.0.0.0', ssl_context=context)
