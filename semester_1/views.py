from datetime import datetime

from flask import Blueprint, render_template, session, redirect, url_for, request, Response, flash
from flask_login import login_required, current_user
from sqlalchemy import exc
from werkzeug.security import check_password_hash, generate_password_hash

from semester_1 import User, Thread, Group, Post, db

views = Blueprint('views', __name__)


@views.route('/index', methods=['GET', 'POST'])
@views.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        search = request.form['search']
        reverse = request.form.get('reverse') is not None
        sort_by = request.form['sort_by']
        page = request.args.get('page', 1, type=int)

        threads = Thread.query.filter(Thread.group_id == None)

        if search is not None:
            threads = threads.filter(Thread.name.contains(search))

        if reverse:
            if sort_by == 'age':
                threads = threads.order_by(Thread.created_at.desc())
            elif sort_by == 'last_active':
                threads = threads.order_by(Thread.last_active.desc())
        else:
            if sort_by == 'age':
                threads = threads.order_by(Thread.created_at)
            elif sort_by == 'last_active':
                threads = threads.order_by(Thread.last_active)

        threads = threads.paginate(page, 10, False)

        next_url = url_for('views.index', page=threads.next_num) \
            if threads.has_next else None
        prev_url = url_for('views.index', page=threads.prev_num) \
            if threads.has_prev else None

        return render_template("index.html", threads=threads.items, next_url=next_url,
                               prev_url=prev_url)

    page = request.args.get('page', 1, type=int)
    threads = Thread.query.filter(Thread.group_id == None).paginate(page, 10, False)
    next_url = url_for('views.index', page=threads.next_num) \
        if threads.has_next else None
    prev_url = url_for('views.index', page=threads.prev_num) \
        if threads.has_prev else None
    return render_template("index.html", threads=threads.items, next_url=next_url, prev_url=prev_url)


@views.route('/groups', methods=['GET', 'POST'])
def groups():
    if request.method == 'POST':
        search = request.form['search']
        reverse = request.form.get('reverse') is not None
        sort_by = request.form['sort_by']
        page = request.args.get('page', 1, type=int)

        groups = Group.query

        if search is not None:
            groups = groups.filter(Group.name.contains(search))

        if reverse:
            if sort_by == 'age':
                groups = groups.order_by(Group.created_at.desc())
            elif sort_by == 'last_active':
                groups = groups.order_by(Group.last_active.desc())
        else:
            if sort_by == 'age':
                groups = groups.order_by(Group.created_at)
            elif sort_by == 'last_active':
                groups = groups.order_by(Group.last_active)

        groups = groups.paginate(page, 10, False)
        next_url = url_for('views.groups', page=groups.next_num) \
            if groups.has_next else None
        prev_url = url_for('views.groups', page=groups.prev_num) \
            if groups.has_prev else None
        return render_template("groups.html", groups=groups.items, next_url=next_url,
                               prev_url=prev_url)

    page = request.args.get('page', 1, type=int)
    groups = Group.query.paginate(page, 10, False)
    next_url = url_for('views.groups', page=groups.next_num) \
        if groups.has_next else None
    prev_url = url_for('views.groups', page=groups.prev_num) \
        if groups.has_prev else None
    return render_template("groups.html", groups=groups.items, next_url=next_url, prev_url=prev_url)


@views.route('/create_thread', methods=['GET', 'POST'])
@login_required
def create_thread():
    if request.method == 'POST':
        name = request.form['name']
        about = request.form['about']
        error = None

        if Thread.query.filter_by(name=name).first():
            error = "Thread with that name already exists."
        else:
            thread = Thread(name=name, about=about, creator_id=current_user.id)
            db.session.add(thread)
            db.session.commit()
            return redirect(url_for("views.index"))

        flash(error)

    return render_template('create_thread.html')


@views.route('/create_group', methods=['GET', 'POST'])
@login_required
def create_group():
    if request.method == 'POST':
        name = request.form['name']
        about = request.form['about']
        error = None

        if Thread.query.filter(Thread.group_id != None, Thread.name == name).first():
            error = "Group with that name already exists."
        else:
            user = User.query.filter_by(id=current_user.id).first()
            group = Group(name=name, about=about, creator_id=user.id)
            group.users.append(user)
            db.session.add(group)
            db.session.commit()
            thread = Thread(name=name, about=about, creator_id=user.id, group_id=group.id)
            db.session.add(thread)
            db.session.commit()
            return redirect(url_for("views.index"))

        flash(error)

    return render_template('create_group.html')


@views.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    if request.method == 'POST':
        email = request.form['email']
        username = request.form['username']
        password = request.form['password']
        titles = request.form['titles']
        error = None

        if not (('@' in email) and ('.' in email)) and email:
            error = 'Invalid email.'
        elif len(password) < 8 and password:
            error = 'Password is too short.'

        if error is None:
            try:
                user = User.query.filter_by(id=current_user.id).first()
                if email:
                    user.email = email
                if username:
                    user.username = username
                if password:
                    user.password = generate_password_hash(password)
                if titles:
                    user.titles = titles
                db.session.commit()
            except exc.SQLAlchemyError:
                error = 'User is already registered.'
            else:
                return redirect(url_for("views.index"))

        flash(error)

    return render_template('profile.html')


@views.route('/thread/<int:thread_id>', methods=['GET', 'POST'])
def thread(thread_id):
    if request.method == 'POST':
        if not current_user.is_authenticated:
            redirect(url_for('auth.login'))
        content = request.form["content"]
        if content:
            post = Post(creator_id=current_user.id, thread_id=thread_id, content=content)
            db.session.add(post)
            db.session.commit()
            thread = Thread.query.filter(Thread.id == post.thread_id).first()
            thread.last_active = datetime.now()
            db.session.commit()
            return redirect(url_for('views.thread', thread_id=thread_id))

    page = request.args.get('page', 1, type=int)
    posts = Post.query.filter(Post.thread_id == thread_id).paginate(page, 10, False)
    replies = posts.total
    thread_obj = Thread.query.filter(Thread.id == thread_id).first()
    next_url = url_for('views.thread', thread_id=thread_id, page=posts.next_num) \
        if posts.has_next else None
    prev_url = url_for('views.thread', thread_id=thread_id, page=posts.prev_num) \
        if posts.has_prev else None
    return render_template('thread.html', thread=thread_obj, replies=replies, posts=posts.items, next_url=next_url, prev_url=prev_url)


@views.route('/group/<int:group_id>', methods=['GET', 'POST'])
def group(group_id):
    if request.method == 'POST':
        if not current_user.is_authenticated:
            redirect(url_for('auth.login'))

        content = request.form["content"]
        group_obj = Group.query.filter(Group.id == group_id).first()
        if current_user not in group_obj.users:
            flash("To reply you should join the group first!")
        elif content:
            post = Post(creator_id=current_user.id, thread_id=group_obj.thread.id, content=content)
            db.session.add(post)
            db.session.commit()
            group_obj.last_active = datetime.now()
            thread = Thread.query.filter(Thread.id == post.thread_id).first()
            thread.last_active = datetime.now()
            db.session.commit()
            return redirect(url_for('views.group', group_id=group_id))

    page = request.args.get('page', 1, type=int)
    group_obj = Group.query.filter(Group.id == group_id).first()
    posts = Post.query.filter(Post.thread_id == group_obj.thread.id).paginate(page, 10, False)
    replies = posts.total
    next_url = url_for('group', group_id=group_id, page=posts.next_num) \
        if posts.has_next else None
    prev_url = url_for('group', group_id=group_id, page=posts.prev_num) \
        if posts.has_prev else None
    return render_template('group.html', group=group_obj, replies=replies, posts=posts.items, next_url=next_url, prev_url=prev_url)


@views.route('/group_join/<int:group_id>', methods=['GET', 'POST'])
def group_join(group_id):
    group = Group.query.filter(Group.id == group_id).first()
    group.users.append(current_user)
    db.session.commit()
    return redirect(url_for('views.group', group_id=group_id))
