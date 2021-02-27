import flask
from flask import render_template, redirect, url_for, flash, request, g, jsonify
# from app import app
from flask_login import current_user, login_user, logout_user, login_required
from werkzeug.urls import url_parse
from datetime import datetime
from flask_babel import _, get_locale
from guess_language import guess_language
from app import db
from app.translate import translate
from app.auth import bp
from app.auth.email import send_password_reset_email
from app.auth.forms import LoginForm, RegistrationForm, ResetPasswordRequestForm, ResetPasswordForm
from app.models import User, Post


@bp.route('/login', methods=['GET','POST'])
def login():
    if current_user.is_authenticated:
        return flask.redirect(flask.url_for('main.index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flask.flash(_('Invalid username or password'))
            return flask.redirect(flask.url_for('auth.login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = flask.url_for('main.index')
        return flask.redirect(next_page)
    return flask.render_template('auth/login.html', title='Sign In', form=form)


@bp.route('/logout')
def logout():
    logout_user()
    return flask.redirect(flask.url_for('main.index'))


@bp.route('/register', methods=['GET','POST'])
def register():
    if current_user.is_authenticated:
        return flask.redirect(flask.url_for('main.index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flask.flash(_('Congratulations, you are now a registered user!'))
        return flask.redirect(flask.url_for('auth.login'))
    return flask.render_template('auth/register.html', title='Register', form=form)


@bp.route('/reset_password_request', methods=['GET','POST'])
def reset_password_request():
    if current_user.is_authenticated:
        return flask.redirect(flask.url_for('main.index'))
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            send_password_reset_email(user)
        flask.flash(_('Check your email for the instructions to reset your password'))
        return flask.redirect(flask.url_for('auth.login'))
    return flask.render_template('auth/reset_password_request.html', title='Reset Password', form=form)


@bp.route('/reset_password/<token>', methods=['GET','POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return flask.redirect(flask.url_for('main.index'))
    user = User.verify_reset_password_token(token)
    if not user:
        return flask.redirect(flask.url_for('main.index'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        db.session.commit()
        flask.flash(_('Your password has been reset.'))
        return flask.redirect(flask.url_for('auth.login'))
    return flask.render_template('auth/reset_password.html', form=form)
