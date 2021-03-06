
from datetime import datetime
import flask
from flask import render_template, flash, redirect, url_for, request, g, \
    jsonify, current_app
from flask_login import current_user, login_required
from flask_babel import _, get_locale
from guess_language import guess_language
from app import db
from app.main.forms import EditProfileForm, EmptyForm, PostForm
from app.models import User, Post
from app.translate import translate
from app.main import bp
from app.main.forms import SearchForm


@bp.before_app_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()
        g.search_form = SearchForm()
    g.locale = str(get_locale())

@bp.route('/', methods=['GET','POST'])
@bp.route('/index', methods=['GET','POST'])
@login_required
def index():
    # user = {'username': 'Miguel'}
    form = PostForm()
    if form.validate_on_submit():
        language = guess_language(form.post.data)
        if language == 'UNKNOWN' or len(language) >5:
            language = ''
        post = Post(body=form.post.data, author=current_user, language=language)
        db.session.add(post)
        db.session.commit()
        flask.flash(_('Your post is now live!'))
        return flask.redirect(flask.url_for('main.index'))

    page = request.args.get('page', 1, type=int)
    posts = current_user.followed_posts().paginate(page, current_app.config['POSTS_PER_PAGE'], False)
    next_url = flask.url_for('main.index', page=posts.next_num) \
        if posts.has_next else None
    prev_url = flask.url_for('main.index', page=posts.prev_num) \
        if posts.has_prev else None
    site_code = flask.render_template('index.html', title='Home Page', form=form, posts=posts.items, next_url=next_url, prev_url=prev_url)
    return site_code


@bp.route('/explore')
@login_required
def explore():
    page = request.args.get('page', 1, type=int)
    posts = Post.query.order_by(Post.timestamp.desc()).paginate(page, current_app.config['POSTS_PER_PAGE'], False)
    next_url = flask.url_for('main.explore', page=posts.next_num) \
        if posts.has_next else None
    prev_url = flask.url_for('main.explore', page=posts.prev_num) \
        if posts.has_prev else None

    return flask.render_template('index.html', title='Explore', posts=posts.items, next_url=next_url, prev_url=prev_url)


@bp.route('/user/<username>')
@login_required
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    page = request.args.get('page', 1, type=int)
    posts = user.posts.order_by(Post.timestamp.desc()).paginate(page, current_app.config['POSTS_PER_PAGE'], False)
    next_url = flask.url_for('main.user', username=user.username, page=posts.next_num) \
        if posts.has_next else None
    prev_url = flask.url_for('main.user', username=user.username, page=posts.prev_num) \
        if posts.has_prev else None
    form = EmptyForm()
    return flask.render_template('user.html', user=user, posts=posts.items, next_url=next_url, prev_url=prev_url, form=form)


@bp.route('/edit_profile', methods=['GET','POST'])
@login_required
def edit_profile():
    form = EditProfileForm(current_user.username)
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.about_me = form.about_me.data
        db.session.commit()
        flask.flash(_('Your changes have been saved.'))
        return flask.redirect(flask.url_for('main.edit_profile'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.about_me.data = current_user.about_me
    return flask.render_template('edit_profile.html', title='Edit Profile', form=form)

@bp.route('/follow/<username>', methods=['POST'])
@login_required
def follow(username):
    form = EmptyForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=username).first()
        if user is None:
            flask.flash(_('User %{username}s not found.', username=username))
            return flask.redirect(flask.url_for('main.index'))
        if user == current_user:
            flask.flash(_('You cannot follow yourself!'))
            return flask.redirect(flask.url_for('main.user', username=username))
        current_user.follow(user)
        db.session.commit()
        flask.flash(_('You are following %(username)s!', username=username))
        return flask.redirect(flask.url_for('main.user', username=username))
    else:
        return flask.redirect(flask.url_for('main.index'))

@bp.route('/unfollow/<username>', methods=['POST'])
@login_required
def unfollow(username):
    form = EmptyForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=username).first()
        if user is None:
            flask.flash(_('User %{username}s not found.', username=username))
            return flask.redirect(flask.url_for('main.index'))
        if user == current_user:
            flask.flash(_('You cannot unfollow yourself!'))
            return flask.redirect(flask.url_for('main.user', username=username))
        current_user.unfollow(user)
        db.session.commit()
        flask.flash(_('You are not following %(username)s!', username=username))
        return flask.redirect(flask.url_for('main.user', username=username))
    else:
        return flask.redirect(flask.url_for('main.index'))


@bp.route('/translate', methods=['POST'])
@login_required
def translate_text():
    return jsonify({'text': translate(request.form['text'],
        request.form['source_language'],
        request.form['dest_language']
    )})


@bp.route('/search')
@login_required
def search():
    if not g.search_form.validate():
        return redirect(url_for('main.explore'))
    page= request.args.get('page', 1, type=int)
    posts, total = Post.search(g.search_form.q.data, page, current_app.config['POSTS_PER_PAGE'])
    next_url = url_for('main.search', q=g.search_form.q.data, page=page + 1) \
        if total > page * current_app.config['POSTS_PER_PAGE'] else None
    prev_url = url_for('main.search', q=g.search_form.q.data, page=page - 1) \
        if page > 1 else None
    return render_template('search.html', title=_('Search'), posts=posts, next_url=next_url, prev_url=prev_url)


@bp.route('/user/<username>/popup')
@login_required
def user_popup(username):
    user = User.query.filter_by(username=username).first_or_404()
    form = EmptyForm()
    return render_template('user_popup.html', user=user, form = form)
