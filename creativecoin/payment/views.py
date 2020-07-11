from flask import Blueprint, redirect, url_for, render_template, request
from flask_login import login_required

from creativecoin import app, db, models
from creativecoin.helper.coinpayments import CryptoPayments
from creativecoin.helper.utils import get_usd, sci_notation

pay = Blueprint('pay', __name__)

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
    data = request.form.to_dict()
    data['amount_php'] = sci_notation(float(data['amount_php']),2)
    return render_template('buy/payment.html', data=data)



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


@pay.route('/verifypayment', strict_slashes=False, methods=['POST', 'GET'])
@login_required
def verifypayment():
    return str(request.form.to_dict())


