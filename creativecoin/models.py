from flask_login import UserMixin
from passlib.hash import pbkdf2_sha256 as hasher
from sqlalchemy.sql import func

from creativecoin import app, db, login_manager

import datetime


class User(UserMixin, db.Model):

    __tablename__ = "user"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(128), unique=True, nullable=False)
    firstname = db.Column(db.String(128))
    lastname = db.Column(db.String(128))
    password_hash = db.Column(db.String(256), nullable=False)
    phonenumber = db.Column(db.String(20))
    referrer = db.Column(db.Integer, default=1)
    created = db.Column(db.TIMESTAMP(timezone=True), server_default=func.current_timestamp())

    emailverified = db.Column(db.Boolean(), default=False)
    is_admin = db.Column(db.Boolean(), default=False)

    payments = db.relationship('Payment', backref='user', lazy=True, uselist=True)
    wallet = db.relationship('Wallet', backref='user', lazy=True, uselist=False)

    def __repr__(self):
        return "<User {}>".format(self.email)

    def toJSON(self):
        return self.__dict__

    @property
    def password(self):
        raise AttributeError("password not readable")

    @password.setter
    def password(self, password):
        self.password_hash = hasher.encrypt(password, rounds=2000, salt=str.encode(app.secret_key))

    def validate_password(self, password):
        return hasher.verify(password, self.password_hash)

    def is_active(self):
        return True

    def is_anonymouse(self):
        return False

    def is_authenticated(self):
        return False

    def get_id(self):
        return self.id


class Wallet(db.Model):

    __tablename__ = "wallet"
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'))
    wallet_id = db.Column(db.String(255), unique=True)

    created = db.Column(db.TIMESTAMP(timezone=True), server_default=func.current_timestamp())
    free_mined = db.Column(db.DECIMAL(precision=30, scale=10), default=0)
    mined = db.Column(db.DECIMAL(precision=30, scale=10), default=0)
    received = db.Column(db.DECIMAL(precision=30, scale=10), default=0)
    referral = db.Column(db.DECIMAL(precision=30, scale=10), default=0)
    total_balance = db.Column(db.DECIMAL(precision=30, scale=10), default=0)

    def __repr__(self):
        return "<Wallet {} of User {}>".format(self.id, self.user_id)


class Transaction(db.Model):

    __tablename__ = "transaction"

    txn_id = db.Column(db.String(256), primary_key=True, nullable=False)
    amount_php = db.Column(db.DECIMAL(precision=20, scale=10), default=-1)
    amount_usd = db.Column(db.DECIMAL(precision=20, scale=10), default=-1)
    amount_ccn = db.Column(db.DECIMAL(precision=20, scale=10), default=-1)
    created = db.Column(db.TIMESTAMP(timezone=True), server_default=func.current_timestamp())
    item_name = db.Column(db.String(128))
    quantity = db.Column(db.Integer, default=-1)
    received_confirmations = db.Column(db.Integer, default=0)
    status = db.Column(db.String(128))
    txn_from = db.Column(db.String(256))
    txn_to = db.Column(db.String(256))
    txn_type = db.Column(db.String(128)) # [PAYMENT, MINE, SEND, RECEIVE]
    updated  = db.Column(db.TIMESTAMP(timezone=True), nullable=True)

    is_verified = db.Column(db.Boolean(), default=False)
    is_transferred = db.Column(db.Boolean(), default=False)

    def compute_confirmation(self):
        return ((datetime.datetime.now() - self.created).days + 1) * 48


class Payment(db.Model):

    __tablename__ = "payment"

    id = db.Column(db.Integer, primary_key=True)
    txn_id = db.Column(db.String(256), db.ForeignKey('transaction.txn_id', ondelete='CASCADE'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'))
    
    category = db.Column(db.String(128), default='NA')
    created = db.Column(db.TIMESTAMP(timezone=True), server_default=func.current_timestamp())
    reference = db.Column(db.String(256), unique=True)
    status = db.Column(db.String(128), default='PENDING')
    updated = db.Column(db.TIMESTAMP(timezone=True), nullable=True)
