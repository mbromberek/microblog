from app import app
import flask

@app.route('/')
@app.route('/index')
def index():
    user = {'username': 'Miguel'}
    posts = [
        {
            'author':{'username':'John'},
            'body':'Beautiful day in Portland!'
        },
        {
            'author':{'username':'Susan'},
            'body': 'The Avengers movie was so cool!'
        }
    ]
    site_code = flask.render_template('index.html', title='Home', user=user, posts=posts)
    return site_code
