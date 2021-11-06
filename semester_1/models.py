from datetime import datetime
from hashlib import md5

from flask_login import UserMixin

from semester_1 import db


association_user_group_table = db.Table('user_group',
                                        db.Column('user_id', db.ForeignKey('users.id'), primary_key=True),
                                        db.Column('group_id', db.ForeignKey('groups.id'), primary_key=True)
                                        )


class User(db.Model, UserMixin):
    __tablename__ = "users"

    id = db.Column(db.Integer, unique=True, autoincrement=True, nullable=False, primary_key=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now())

    email = db.Column(db.String(100), nullable=False, unique=True)
    password = db.Column(db.TEXT, nullable=False)
    username = db.Column(db.String(100), nullable=False, unique=True)

    picture = db.Column(db.LargeBinary, nullable=True)
    titles = db.Column(db.TEXT, nullable=True)

    groups = db.relationship("Group",
                             secondary=association_user_group_table,
                             back_populates="users"
                             )
    posts = db.relationship("Post", backref="user", lazy=True)
    created_groups = db.relationship("Group", backref="creator", lazy=True)
    created_threads = db.relationship("Thread", backref="creator", lazy=True)

    def avatar(self, size):
        digest = md5(self.email.lower().encode('utf-8')).hexdigest()
        return 'https://www.gravatar.com/avatar/{}?d=identicon&s={}'.format(
            digest, size)

    def __repr__(self):
        return "<User(id='%s', username='%s', email='%s')>" % (self.id, self.username, self.email)


class Post(db.Model):
    __tablename__ = "posts"

    id = db.Column(db.Integer, unique=True, autoincrement=True, nullable=False, primary_key=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now())
    creator_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    content = db.Column(db.TEXT, nullable=False)
    thread_id = db.Column(db.Integer, db.ForeignKey('threads.id'), nullable=False)

    def __repr__(self):
        return "<Post(id='%s', created_at='%s', created_by='%s', content='%s')>" %\
               (self.id, self.created_at, self.creator_id, self.content)


class Thread(db.Model):
    __tablename__ = "threads"

    id = db.Column(db.Integer, unique=True, autoincrement=True, nullable=False, primary_key=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now())
    creator_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    last_active = db.Column(db.DateTime, nullable=False, default=datetime.now())

    name = db.Column(db.String(100), nullable=False, unique=True)
    about = db.Column(db.TEXT, nullable=False)
    group_id = db.Column(db.Integer, db.ForeignKey('groups.id'), nullable=True)

    posts = db.relationship("Post", backref="thread", lazy=True)

    def __repr__(self):
        return "<Thread(id='%s', name='%s', about='%s')>" %\
               (self.id, self.name, self.about)


class Group(db.Model):
    __tablename__ = "groups"

    id = db.Column(db.Integer, unique=True, autoincrement=True, nullable=False, primary_key=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now())
    creator_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    last_active = db.Column(db.DateTime, nullable=False, default=datetime.now())

    name = db.Column(db.String(100), nullable=False, unique=True)
    about = db.Column(db.TEXT, nullable=False)
    open_group = db.Column(db.BOOLEAN, nullable=False, default=True)

    users = db.relationship("User",
                            secondary=association_user_group_table,
                            back_populates="groups"
                            )
    thread = db.relationship("Thread", backref="group", lazy=True, uselist=False)

    def __repr__(self):
        return "<Group(id='%s', name='%s', about='%s')>" %\
               (self.id, self.name, self.about)
