from uuid import uuid4
from time import time
from datetime import datetime
from flask import current_app, request, url_for
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flaskblog import db, login_manager
from flask_login import UserMixin
from flaskblog.users.utils import send_confirmation_email

CONFIRMATION_EXPIRATION_DELTA = 1800


@login_manager.user_loader
def load_user(user_id):
    return UserModel.query.get(int(user_id))


class UserModel(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    image_file = db.Column(db.String(20), default='default.jpg')
    password = db.Column(db.String(60), nullable=False)
    posts = db.relationship('PostModel', backref='author', lazy=True)
    confirmation = db.relationship(
        "ConfirmationModel", lazy="dynamic", cascade="all, delete-orphan"
    )

    @classmethod
    def find_by_email(cls, email):
        return cls.query.filter_by(email=email).first()

    @property
    def most_recent_confirmation(self) -> "ConfirmationModel":
        return self.confirmation.order_by(db.desc(ConfirmationModel.expires_at)).first()

    def confirm(self):
        link = request.url_root[0:-1] + url_for(
            "users.confirmation", confirmation_id=self.most_recent_confirmation.id
        )
        subject = "Registration confirmation."
        text = f"Please click link to confirm your registration {link}"
        html = f'<html>Please click link to confirm your registration: <a href="{link}">{link}</a></html>'

        return send_confirmation_email(self.email, subject, text, html)

    def get_reset_token(self, expires_sec=1800):
        s = Serializer(current_app.config['SECRET_KEY'], expires_sec)
        return s.dumps({'user_id': self.id}).decode('utf-8')

    @staticmethod
    def verify_reset_token(token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            user_id = s.loads(token)['user_id']
        except:
            return None
        return UserModel.query.get(user_id)

    def __repr__(self):
        return f"UserModel('{self.username}', '{self.email}', '{self.image_file}')"

    def delete_from_db(self):
        db.session.delete(self)
        db.session.commit()


class PostModel(db.Model):
    __tablename__ = 'posts'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.now())
    content = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False
                        )

    def __repr__(self):
        return f"PostModel('{self.title}', '{self.date_posted}')"


class ConfirmationModel(db.Model):
    __tablename__ = 'confirmations'
    id = db.Column(db.String(50), primary_key=True)
    expires_at = db.Column(db.Integer, nullable=False)
    confirmed = db.Column(db.Boolean, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    def __init__(self, user_id, **kwargs):
        super().__init__(**kwargs)
        self.user_id = user_id
        self.id = uuid4().hex
        self.expires_at = int(time()) + CONFIRMATION_EXPIRATION_DELTA
        self.confirmed = False

    @classmethod
    def find_by_id(cls, _id):
        return cls.query.filter_by(id=_id).first()

    @property
    def expired(self) -> bool:
        return time() > self.expires_at

    def force_to_expire(self) -> None:
        if not self.expired:
            self.expires_at = int(time())
            self.save_to_db()

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self):
        db.session.delete(self)
        db.session.commit()
