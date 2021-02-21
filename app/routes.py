import flask
from flask import request
from app import app
from app import db
from app.forms import LoginForm, RegistrationForm, EditProfileForm, EmptyForm, PostForm
from flask_login import current_user, login_user, logout_user, login_required
from app.models import User, Post
from werkzeug.urls import url_parse
from datetime import datetime

@app.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()

@app.route('/', methods=['GET','POST'])
@app.route('/index', methods=['GET','POST'])
@login_required
def index():
    # user = {'username': 'Miguel'}
    form = PostForm()
    if form.validate_on_submit():
        post = Post(body=form.post.data, author=current_user)
        db.session.add(post)
        db.session.commit()
        flask.flash('Your post is now live!')
        return flask.redirect(flask.url_for('index'))

    page = request.args.get('page', 1, type=int)
    posts = current_user.followed_posts().paginate(page, app.config['POSTS_PER_PAGE'], False)
    site_code = flask.render_template('index.html', title='Home Page', form=form, posts=posts.items)
    return site_code


@app.route('/explore')
@login_required
def explore():
    page = request.args.get('page', 1, type=int)
    posts = Post.query.order_by(Post.timestamp.desc()).paginate(page, app.config['POSTS_PER_PAGE'], False)
    return flask.render_template('index.html', title='Explore', posts=posts.items)


@app.route('/login', methods=['GET','POST'])
def login():
    if current_user.is_authenticated:
        return flask.redirect(flask.url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flask.flash('Invalid username or password')
            return flask.redirect(flask.url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = flask.url_for('index')
        return flask.redirect(next_page)
    return flask.render_template('login.html', title='Sign In', form=form)

@app.route('/logout')
def logout():
    logout_user()
    return flask.redirect(flask.url_for('index'))

@app.route('/register', methods=['GET','POST'])
def register():
    if current_user.is_authenticated:
        return flask.redirect(flask.url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flask.flash('Congratulations, you are now a registered user!')
        return flask.redirect(flask.url_for('login'))
    return flask.render_template('register.html', title='Register', form=form)

@app.route('/user/<username>')
@login_required
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    posts = [
        {'author': user, 'body': 'Test post #1'},
        {'author': user, 'body': 'Test post #2'}
    ]
    form = EmptyForm()
    return flask.render_template('user.html', user=user, posts=posts, form=form)

@app.route('/edit_profile', methods=['GET','POST'])
@login_required
def edit_profile():
    form = EditProfileForm(current_user.username)
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.about_me = form.about_me.data
        db.session.commit()
        flask.flash('Your changes have been saved.')
        return flask.redirect(flask.url_for('edit_profile'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.about_me.data = current_user.about_me
    return flask.render_template('edit_profile.html', title='Edit Profile', form=form)

@app.route('/follow/<username>', methods=['POST'])
@login_required
def follow(username):
    form = EmptyForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=username).first()
        if user is None:
            flask.flash('User {} not found.'.format(username))
            return flask.redirect(flask.url_for('index'))
        if user == current_user:
            flask.flash('You cannot follow yourself!')
            return flask.redirect(flask.url_for('user', username=username))
        current_user.follow(user)
        db.session.commit()
        flask.flash('You are following {}!'.format(username))
        return flask.redirect(flask.url_for('user', username=username))
    else:
        return flask.redirect(flask.url_for('index'))

@app.route('/unfollow/<username>', methods=['POST'])
@login_required
def unfollow(username):
    form = EmptyForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=username).first()
        if user is None:
            flask.flash('User {} not found.'.format(username))
            return flask.redirect(flask.url_for('index'))
        if user == current_user:
            flask.flash('You cannot unfollow yourself!')
            return flask.redirect(flask.url_for('user', username=username))
        current_user.unfollow(user)
        db.session.commit()
        flask.flash('You are not following{}.'.format(username))
        return flask.redirect(flask.url_for('user', username=username))
    else:
        return flask.redirect(flask.url_for('index'))
