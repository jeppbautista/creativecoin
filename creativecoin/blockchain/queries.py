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


def get_all_tx_from_block(block):
    return {
        "query": {
            "match": {
                "block": block
            }
        }
    }


def get_all_tx_from_wallet(wallet):
    return {
        "query": {
            "bool": {
                "should": [
                    {
                        "term": {
                            "from_wallet": wallet
                        }
                    },
                    {
                        "term": {
                            "to_wallet": wallet
                        }
                    }
                ]
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


def get_total_trans_aggs_tx_from_wallet(wallet):
    return {
        "query": {
            "bool": {
                "should": [
                    {
                        "term": {
                            "from_wallet": wallet
                        }
                    },
                    {
                        "term": {
                            "to_wallet": wallet
                        }
                    }
                ]
            }
        },
        "aggs": {
            "total_transaction": {
                "value_count": {
                    "field": "value"
                }
            }
        }
    }
    

def get_total_rec_aggs_tx_from_wallet(wallet):
    return {
        "aggs": {
            "total_received_filter": {
                "filter": {
                    "term": {
                        "to_wallet": wallet
                    }
                },
                "aggs": {
                    "total_received": {
                        "sum": {
                            "field": "value"
                        }
                    }
                }
            }
        }
    }

def get_total_sent_aggs_tx_from_wallet(wallet):
    return {
        "aggs": {
            "total_sent_filter": {
                "filter": {
                    "term": {
                        "from_wallet": wallet
                    }
                },
                "aggs": {
                    "total_sent": {
                        "sum": {
                            "field": "value"
                        }
                    }
                }
            }
        }
    }
