from flask import Blueprint, redirect, url_for, render_template, request
from flask_login import current_user, login_required

import re
from sqlalchemy.exc import IntegrityError
import traceback

from creativecoin import app, db, models
from creativecoin.email import EmailSender
from creativecoin.helper.coinpayments import CryptoPayments
from creativecoin.helper.utils import generate_txn_id, get_usd, sci_notation, utcnow, get_grain, generate_wallet_id
from creativecoin.payment.forms import Payment


pay = Blueprint('pay', __name__)

MAP_CCN = {
    "BRONZE": 25,
    "SILVER": 50,
    "GOLD": 100
}

@pay.route('/buy')
def buy():
    """
    Renders the Buy page: https://creativecoin.net/buy
    """
    app.logger.error("INFO - /buy")
    app.logger.error("INFO - User: {}".format(current_user))
    usd_val = get_usd()
    return render_template('buy/buy.html', usd=usd_val, title="Buy - CreativeCoin")


@pay.route('/payment', strict_slashes=False, methods=['POST', 'GET'])
@login_required
def payment():
    """
    Checks if the user is email verified then renders the Payment page else redirects to the Buy page.
    """
    app.logger.error("INFO - /payment")
    app.logger.error("INFO - User: {}".format(current_user))

    if current_user.emailverified != 1:
        return redirect(url_for("pay.buy"))
    try:
        data = request.form.to_dict()
        paymentform = Payment(request.form)
        # app.logger.error("{}".format(str(request.form)))

        data['amount_php'] = sci_notation(float(data['amount_php']),2)
        return render_template('buy/payment.html', data=data, paymentform=paymentform, title="Payment - CreativeCoin")
    except KeyError as e:
        app.logger.error(traceback.format_exc())
        return redirect(url_for("auth.login"))


@pay.route('/verifypayment', strict_slashes=False, methods=['POST', 'GET'])
@login_required
def verifypayment():
    """
    Verifies the payment, adds it to the database and sends an email to confirm the payment.
    """
    app.logger.error("INFO - /verifypayment")
    app.logger.error("INFO - User: {}".format(current_user))
    paymentform = Payment(request.form)
    # app.logger.error("{}".format(str(request.form)))

    if paymentform.validate():
        app.logger.error("INFO - FORM is valid")
        txn_id = generate_txn_id(current_user.id)

        _itemname = re.search('\((.*)\)', paymentform.item_name.data).group(1).upper()
        quantity = MAP_CCN[_itemname]*int(paymentform.quantity.data)
        raw_amount_ccn = float(float(paymentform.amount_usd.data) / get_grain())
        amount_ccn = raw_amount_ccn + float((raw_amount_ccn * 0.5))

        transaction = models.Transaction(
            txn_id=txn_id,
            txn_from=generate_wallet_id(str(current_user.id)),
            txn_to="CCN-ADMIN",
            txn_type="PAYMENT",
            item_name=paymentform.item_name.data,
            quantity=quantity,
            amount_php=paymentform.amount_php.data,
            amount_usd=paymentform.amount_usd.data,
            amount_ccn=amount_ccn,
            status="PENDING",
            received_confirmations=0,

            is_verified = False,
            is_transferred = False
        )
        app.logger.error("INFO - TRANSACTION: {}".format(str(transaction.__dict__)))

        payment = models.Payment(
            txn_id = txn_id,
            user_id = current_user.id,
            reference = paymentform.reference.data,
            category = str(paymentform.payment_category.data).upper(),
            status = "PENDING",
            updated = utcnow()
        )

        app.logger.error("INFO - PAYMENT: {}".format(str(payment.__dict__)))

        try:
            app.logger.error("INFO - CREATING TRANSACTION... Txn_id: {}".format(txn_id))
            db.session.add(transaction)
            db.session.commit()
            db.session.add(payment)
            db.session.commit()
            app.logger.error("INFO - TRANSACTION CREATED! Txn_id: {}".format(txn_id))

            app.logger.error("INFO - Sending email... user_id: {}".format(current_user.id))
            mail = EmailSender()
            params = {
                "login_link": "http://{root_url}/login".format(root_url = app.config["SERVER_NAME"]),
                "firstname": current_user.firstname
            }
            body = mail.prepare_body(params, path="received-email.html")

            if not mail.send_mail(current_user.email, "We have received your payment", body):
                app.logger.error("ERROR - EMAIL SENDING FAILED! TRANSACTION: {}".format(str(transaction.__dict__)))
                return redirect(url_for("pay.payment_failed"))

            mail.send_mail(app.config["ADMIN_MAIL"], "Payment was sent", "Payment was sent. <br>Transaction number: {txn_id} <br>Email: {email}".format(txn_id=txn_id, email=current_user.email))
            app.logger.error("INFO - EMAIL SENDING SUCCESS! TRANSACTION: {}".format(str(transaction.__dict__)))

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
    """
    Renders the payment received page
    """
    app.logger.error("INFO - /payment-received")
    return render_template("email/token.html",
        message="Your payment was received by the system. Please wait a few hours for the admin to approve your payment.",
        button="Go to wallet",
        href=url_for("dash.wallet"),
        title="Payment received - CreativeCoin")


@pay.route('/payment-failed', strict_slashes=False,)
def payment_failed():
    """
    Renders the payment failed page
    """
    app.logger.error("INFO - /payment-failed")
    return render_template("email/token.html",
        message="Payment FAILED! Please contact us.",
        button="Contact Us",
        href=url_for("contact_us"),
        title="Payment failed - CreativeCoin") #TODO contact-us


@pay.route("/usd")
def usd():
    return str(get_usd())

@pay.route("/grain")
def grain():
    return str(get_grain())