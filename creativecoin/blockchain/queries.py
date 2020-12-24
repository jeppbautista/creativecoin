from creativecoin import app, db
from creativecoin.models import User, Wallet

def commit_db():
    db.session.commit()

def rollback():
    db.session.rollback()

def get_all_wallets():
    raw_wallets = Wallet.query\
        .join(User, Wallet.user_id == User.id)\
            .filter(User.emailverified == 1)\
                .filter(Wallet.free_mined > 0)
    
    return raw_wallets


def get_all_blocks():
    return {
        "query": {
            "match_all": {}
        },
        "sort": [
            {
                "timestamp": {"order": "desc"}
            }
        ]
    }


def get_block(curr_hash):
    return {
        "query": {
            "match":{
                "hash": curr_hash
            }
        }
    }


def get_all_tx(block):
    return {
        "query": {
            "match": {
                "block": block
            }
        }
    }


def get_all_txs():
    return {
        "query": {
            "match_all": {
            }
        },
        "sort": [
            {
                "timestamp": {"order": "desc"}
            }
        ]
    }
