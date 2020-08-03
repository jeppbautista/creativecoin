from creativecoin import db
from creativecoin.models import User, Wallet


def add(model):
    db.session.add(model)


def commit_db():
    db.session.commit()


def rollback():
    db.session.rollback()

def get_user(**kv):
    user = User.query.filter_by(**kv).first_or_404()
    return user

def get_wallet(**kv):
    wallet = Wallet.query.filter_by(**kv).first_or_404()
    return wallet
    