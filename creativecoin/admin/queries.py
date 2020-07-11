from creativecoin import db
from creativecoin.models import Payment, Transaction, User, Wallet

from datetime import datetime

ROW_PER_PAGE = 3


def commit_db():
    db.session.commit()


def rollback():
    db.session.rollback()


def retrieve_payments(page, filter_str):
    raw_payments = Payment.query\
        .join(User, Payment.user_id == User.id)\
        .join(Transaction, Payment.txn_id == Transaction.txn_id)\
        .add_columns(User.email, User.firstname, User.lastname, User.phonenumber, Transaction.amount_php, Transaction.amount_usd)\
        .filter(Payment.status==filter_str)\
        .order_by(Payment.created.desc())\
        .paginate(page, ROW_PER_PAGE, False)

    return  raw_payments


def update_payment_status(payment_id, status):
    try:
        payment = Payment.query\
        .filter(Payment.id == payment_id)\
            .first()

        payment.status = status
        payment.updated = datetime.now()
    except Exception as e:
        print(e)
        return False

    return True


def update_transaction_status(payment_id, status):
    try:
        payment = Payment.query\
        .filter(Payment.id == payment_id)\
            .first()
    
        transaction = Transaction.query\
            .filter(Transaction.txn_id == payment.txn_id)\
                .first()

        transaction.status = status
        transaction.received_confirmations = 1 if status == "ACCEPTED" else 0
        transaction.updated = datetime.now()
        transaction.is_verified = True if status=="ACCEPTED" else False
    except Exception as e:
        print(e)
        return False
    
    return True


def update_transaction_transferred(payment_id, is_trans):
    try:
        payment = Payment.query\
            .filter(Payment.id == payment_id)\
                .first()
        
        transaction = Transaction.query\
            .filter(Transaction.txn_id == payment.txn_id)\
                .first()

        transaction.is_transferred = is_trans
    except Exception as e:
        print(e)
        return False

    return True


def update_wallet_free_mined(payment_id, selected_user, choice):
    try:
        payment = Payment.query\
            .filter(Payment.id == payment_id)\
                .first()
        
        transaction = Transaction.query\
            .filter(Transaction.txn_id == payment.txn_id)\
                .first()

        user = User.query\
            .filter(User.email == selected_user)\
                .first()

        wallet = Wallet.query\
            .filter(Wallet.user_id == user.id)\
                .first()

        wallet.free_mined = wallet.free_mined + transaction.quantity

    except Exception as e:
        print(e)
        return False

    return True