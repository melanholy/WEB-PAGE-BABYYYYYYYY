from app import app
from OpenSSL import SSL
import sys

if __name__ == '__main__':
    if len(sys.argv) == 1:
        context = ('izalith_me.crt', 'izalith_me.key')
        app.run(debug=True, port=443, host='0.0.0.0', ssl_context=context)
    else:
        app.run(debug=True, port=443, host='0.0.0.0')
    app.add_url_rule('/favicon.ico', redirect_to=url_for('static', filename='favicon.ico'))
