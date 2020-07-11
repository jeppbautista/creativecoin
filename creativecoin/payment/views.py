from flask import Blueprint, redirect, url_for, render_template, request
from flask_login import current_user, login_required

import re
from sqlalchemy.exc import IntegrityError

from creativecoin import app, db, models
from creativecoin.payment.forms import Payment
from creativecoin.helper.coinpayments import CryptoPayments
from creativecoin.helper.utils import generate_txn_id, get_usd, sci_notation, utcnow

pay = Blueprint('pay', __name__)

MAP_CCN = {
    "BRONZE": 100,
    "SILVER": 200,
    "GOLD": 300
}

@pay.route('/buy')
@login_required
def buy():
    usd_val = get_usd()
    return render_template('buy/buy.html', usd=usd_val)


@pay.route('/ipn', strict_slashes=False, methods=['POST'])
def ipn():
    data = {
        key: value for key,value in  request.form.to_dict().items() if key in cols
    }
    
    with open('/home/cisateducation/public_html/creativecoin.net/creativecoin/test.txt', 'w+') as f:
        f.write(str(data))
         
    return ""

@pay.route('/payment', strict_slashes=False, methods=['POST', 'GET'])
@login_required
def payment():
    try:
        data = request.form.to_dict()
        paymentform = Payment(request.form)
        data['amount_php'] = sci_notation(float(data['amount_php']),2)
        return render_template('buy/payment.html', data=data, paymentform=paymentform)
    except KeyError:
        return redirect(url_for("auth.login"))
    


@pay.route('/verifypayment', strict_slashes=False, methods=['POST', 'GET'])
@login_required
def verifypayment():
    # CREATE Transaction
    # CREATE Payment
    paymentform = Payment(request.form)
    if paymentform.validate():
        txn_id =  generate_txn_id(current_user.id)

        _itemname = re.search('\((.*)\)', paymentform.item_name.data).group(1).upper()
        quantity = MAP_CCN[_itemname]*int(paymentform.quantity.data)

        transaction = models.Transaction(
            txn_id = txn_id,
            user_id = current_user.id,
            txn_from = "{} {}".format(current_user.firstname, current_user.lastname),
            txn_to = "ADMIN",
            txn_type = "PAYMENT",
            item_name = paymentform.item_name.data,
            quantity = quantity,
            amount_php = paymentform.amount_php.data,
            amount_usd = paymentform.amount_usd.data,
            status = "PENDING",
            received_confirmations = 0,

            is_verified = False,
            is_transferred = False
        )

        payment = models.Payment(
            txn_id = txn_id,
            user_id = current_user.id,
            reference = paymentform.reference.data,
            category = str(paymentform.payment_category.data).upper(),
            status = "PENDING",
            updated = utcnow()
        )

        try:
            db.session.add(transaction)
            db.session.commit()
            db.session.add(payment)
            db.session.commit()
        except IntegrityError as e:
            app.logger.error(str(e.__cause__))
            db.session.rollback()
        except Exception as e:
            app.logger.error(e)
            db.session.rollback()

        return "FOOBAR"

    return str(request.form.to_dict())



# @pay.route('/payment', strict_slashes=False, methods=['POST','GET'])
# @login_required
# def payment():
#     coinpayments = CryptoPayments(app.config['COINPAYMENTS_PUBLIC_KEY'], app.config['COINPAYMENTS_PRIVATE_KEY'], 'https://creativecoin.net/ipn')
#     cols = ['item_name', 'buyer_email', 'currency1', 'currency2', 'amount', 'success_url']
#     data = {}

#     data = {
#         key: value for key,value in  request.form.to_dict().items() if key in cols
#     }
#     data['amount'] = float(data['amount'])
#     tx = coinpayments.createTransaction(data)

#     if tx == "NA":
#         return render_html('buy/unable-to-process-payment.html')

#     transaction = models.Transaction(
#         txn_id = tx.txn_id,
#         email = data['buyer_email'],
#         item_name = data['item_name'],
#         quantity = 1,
#         amount1 = -1,
#         amount2 = -1,
#         is_verified = False,
#         is_transferred = False,
#         status = "",
#         received_amount = 0,
#         received_confirmations = 0
#     )
#     db.session.add(transaction)
#     db.session.commit()
    
#     return render_template('buy/payment.html', tx = tx, details = data)



