from app import app
import flask

@app.route('/')
@app.route('/index')
def index():
    user = {'username': 'Miguel'}
    site_code = flask.render_template('index.html', title='Home', user=user)
    return site_code
