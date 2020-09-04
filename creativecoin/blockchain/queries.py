from creativecoin import app, db
from creativecoin.models import User, Wallet

def commit_db():
    db.session.commit()

def rollback():
    db.session.rollback()

def get_all_wallets():
    raw_wallets = Wallet.query\
        .join(User, Wallet.user_id == User.id)\
            .filter(User.emailverified == 1)
    
    return raw_wallets