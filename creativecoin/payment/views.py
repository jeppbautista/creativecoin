from flask import Blueprint, redirect, url_for, render_template, request
from flask_login import current_user, login_required

import re
from sqlalchemy.exc import IntegrityError
import traceback

from creativecoin import app, db, models
from creativecoin.email import EmailSender
from creativecoin.helper.coinpayments import CryptoPayments
from creativecoin.helper.utils import generate_txn_id, get_usd, sci_notation, utcnow, get_grain
from creativecoin.payment.forms import Payment


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


@pay.route('/payment', strict_slashes=False, methods=['POST', 'GET'])
@login_required
def payment():
    app.logger.error("INFO - /payment")
    try:
        data = request.form.to_dict()
        paymentform = Payment(request.form)
        app.logger.error("{}".format(str(request.form)))

        data['amount_php'] = sci_notation(float(data['amount_php']),2)
        return render_template('buy/payment.html', data=data, paymentform=paymentform)
    except KeyError as e:
        app.logger.error(traceback.format_exc())
        return redirect(url_for("auth.login"))
    

@pay.route('/verifypayment', strict_slashes=False, methods=['POST', 'GET'])
@login_required
def verifypayment():
    app.logger.error("INFO - /verifypayment")
    paymentform = Payment(request.form)
    app.logger.error("{}".format(str(request.form)))

    if paymentform.validate():
        app.logger.error("INFO - FORM is valid")
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
        app.logger.error("Transaction: {}".format(str(transaction.__dict__)))

        payment = models.Payment(
            txn_id = txn_id,
            user_id = current_user.id,
            reference = paymentform.reference.data,
            category = str(paymentform.payment_category.data).upper(),
            status = "PENDING",
            updated = utcnow()
        )

        app.logger.error("Payment: {}".format(str(payment.__dict__)))

        try:
            db.session.add(transaction)
            db.session.add(payment)
            app.logger.error("INFO - Transaction was created: {}".format(txn_id))

            mail = EmailSender()
            params = {
                "login_link": "http://{root_url}/login".format(root_url = app.config["SERVER_NAME"]),
                "firstname": current_user.firstname
            }
            body = mail.prepare_body(params, path="received-email.html")

            if not mail.send_mail(current_user.email, "We have received your payment", body):
                app.logger.error("ERROR - PAYMENT FAILED!")
                return redirect(url_for("pay.payment_failed"))

            mail.send_mail(app.config["ADMIN_MAIL"], "Payment was sent", "Payment was sent. <br>Transaction number: {txn_id} <br>Email: {email}".format(txn_id=txn_id, email=current_user.email))
            app.logger.error("INFO - PAYMENT RECEIVED")
            db.session.commit()
            return redirect(url_for("pay.payment_received"))

        except IntegrityError as e:
            app.logger.error(traceback.format_exc())
            db.session.rollback()
        except Exception as e:
            app.logger.error(traceback.format_exc())
            db.session.rollback()

        app.logger.error("ERROR - PAYMENT FAILED!")
        return redirect(url_for("pay.payment_failed"))

    return redirect(url_for("auth.login"))


@pay.route('/payment-received', strict_slashes=False, methods=['POST', 'GET'])
def payment_received():
    app.logger.error("INFO - /payment-received")
    return render_template("email/token.html",
        message="Your payment was received by the system. Please wait a few hours for the admin to approve your payment.",
        button="Login",
        href=url_for("auth.login"))


@pay.route('/payment-failed', strict_slashes=False,)
def payment_failed():
    app.logger.error("INFO - /payment-failed")
    return render_template("email/token.html",
        message="Email sending FAILED! Please contact us.",
        button="Contact Us",
        href=url_for("contact_us")) #TODO contact-us


@pay.route("/usd")
def usd():
    return str(get_usd())

@pay.route("/grain")
def grain():
    return str(get_grain())