from creativecoin import app, db
from creativecoin.models import Wallet

def commit_db():
    db.session.commit()

def rollback():
    db.session.rollback()

def get_all_wallets():
    return Wallet.query