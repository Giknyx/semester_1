from flask import (
    Blueprint, flash, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash

from flask_login import login_user, logout_user, current_user
from sqlalchemy import exc
from semester_1 import db
from semester_1.models import User


auth = Blueprint('auth', __name__)


def login_decorator(func):
    def wrapper(*args, **kwargs):
        if current_user.is_authenticated:
            return redirect(url_for('views.index'))
        return func(*args, **kwargs)
    wrapper.__name__ = func.__name__
    return wrapper


@auth.route('/register', methods=('GET', 'POST'))
def register():
    if request.method == 'POST':
        email = request.form['email']
        username = request.form['username']
        password = request.form['password']
        error = None

        if not email or not (('@' in email) and ('.' in email)):
            error = 'Invalid email.'
        elif not username:
            error = 'Username is required.'
        elif not password:
            error = 'Password is required.'
        elif len(password) < 8:
            error = 'Password is too short.'

        if error is None:
            try:
                user = User(email=email, password=generate_password_hash(password), username=username)
                db.session.add(user)
                db.session.commit()
            except exc.SQLAlchemyError:
                error = 'User is already registered.'
            else:
                return redirect(url_for("auth.login"))

        flash(error)

    return render_template('register.html')


@auth.route('/login', methods=('GET', 'POST'))
@login_decorator
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        remember = request.form.get('remember') is not None
        error = None

        user = User.query.filter_by(username=username).first()
        if user is None:
            error = 'Incorrect data.'
        elif not check_password_hash(user.password, password):
            error = 'Incorrect data.'

        if error is None:
            if remember:
                login_user(user, remember=True)
            else:
                login_user(user, remember=False)
            return redirect(url_for('views.index'))

        flash(error)

    return render_template('login.html')


@auth.route('/logout')
def logout():
    session.clear()
    logout_user()
    return redirect(url_for('views.index'))
