import flask
from app import app
from app.forms import LoginForm

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

@app.route('/login', methods=['GET','POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        flask.flash('Login requested for user {}, remember_me={}'.format(form.username.data, form.remember_me.data))
        return flask.redirect('/index')
    return flask.render_template('login.html', title='Sign In', form=form)
