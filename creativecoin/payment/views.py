from flask import Blueprint, redirect, url_for, render_template, request
from flask_login import current_user, login_required

import re
from sqlalchemy.exc import IntegrityError
import traceback

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
    except KeyError as e:
        app.logger.error(traceback.format_exc())
        return redirect(url_for("auth.login"))
    

@pay.route('/verifypayment', strict_slashes=False, methods=['POST', 'GET'])
@login_required
def verifypayment():
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
            db.session.add(payment)
            db.session.commit()
            app.logger.info("Transaction is created: {}".format(txn_id))

            mail = EmailSender()
            params = {"firstname": current_user.firstname}
            body = mail.prepare_body(params, path="verify-email.html") #TODO payment received 

            if not mail.send_mail(current_user.email, "We have received your payment", body):
                return render_template("email/token.html",
                message="Email sending FAILED! Please contact us.",
                button="Contact Us",
                href=url_for("")) #TODO contact-us

            mail.send_mail(app.config["ADMIN_MAIL"], "Payment was sent", "Payment was sent. <br>Transaction number: {txn_id} <br>Email: {email}".format(txn_id=txn_id, email=current_user.email))
 
            return render_template("email/token.html",
                message="Your payment is now received by the system. Please wait a few hours for the admin to approve your payment.",
                button="Login",
                href=url_for("auth.login"))
            #TODO send email to admin

        except IntegrityError as e:
            app.logger.error(traceback.format_exc())
            db.session.rollback()
        except Exception as e:
            app.logger.error(traceback.format_exc())
            db.session.rollback()

        
        return "FOOBAR"

    return str(request.form.to_dict())


