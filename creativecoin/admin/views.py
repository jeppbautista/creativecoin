from flask import Blueprint, jsonify, redirect, request, render_template, url_for
from flask_login import login_required, current_user

from collections import OrderedDict
import json
import traceback

from creativecoin import app
from creativecoin.admin import queries
from creativecoin.email import EmailSender
from creativecoin.helper import utils
from creativecoin.helper import queries as q
from creativecoin.models import Payment, User

adm = Blueprint('adm', __name__)

@adm.route('/admin-panel')
@login_required
def index():
    if current_user.is_admin:
        return render_template('admin/index.html')
    else:
        return redirect(url_for('auth.login'))


@adm.route('/admin-payment',  methods=['GET', 'POST'])
@login_required
def admin_payment():
    if current_user.is_admin:
        page = int(request.form.get('page', 1))
        filter_str = str(request.form.get('filter', "PENDING"))

        raw_payments = queries.retrieve_payments(page, filter_str)
        payments = _payments(raw_payments)

        return render_template('admin/payment.html', payments=json.dumps(payments), page=page, has_next=raw_payments.has_next, has_prev=raw_payments.has_prev, filter_str=filter_str)
    else:
        return redirect(url_for('auth.login'))


@adm.route('/admin-payment-process/<string:choice>', methods=['GET', 'POST'])
@login_required
def admin_payment_process(choice):
    payment_id = request.form.get('paymentID', None)
    selected_user = request.form.get('email', None)

    mail = EmailSender()

    page = int(request.form.get('page', 1))
    filter_str = str(request.form.get('filterStr', "PENDING"))

    if current_user.is_admin and payment_id and selected_user:

        firstname = queries.get_user(email = selected_user).firstname
        txn_id = queries.get_payment(id = payment_id).txn_id

        app.logger.info("ADMIN ACTION: Payment {choice}: {txn_id}".format(choice=choice, txn_id=txn_id))

        if queries.update_payment_status(payment_id, choice) and \
            queries.update_transaction_status(payment_id, choice):

            if choice == "ACCEPTED":
                if queries.update_wallet_free_mined(payment_id, selected_user, choice) and \
                    queries.update_transaction_transferred(payment_id, True):
                    queries.commit_db()

                    params = {
                        "login_link": "http://{root_url}/login".format(root_url = app.config["SERVER_NAME"]),
                        "firstname": firstname,
                        "txn_id": txn_id
                    }
                    body = mail.prepare_body(params, path="accepted-email.html")
                    if not mail.send_mail(selected_user, "Your payment was accepted", body):
                        app.logger.info("ADMIN ACTION: Email sending FAILED")
                        return "EMAIL SENDING FAILED"

                    app.logger.info("ADMIN ACTION: DONE")

                else:
                    queries.rollback()
            else:
                queries.update_transaction_transferred(payment_id, False)
                queries.commit_db()

                params = {
                    "contact_link": "http://{root_url}/get-in-touch".format(root_url = app.config["SERVER_NAME"]),
                    "firstname": firstname,
                    "txn_id": txn_id
                }
                body = mail.prepare_body(params, path="denied-email.html")
                if not mail.send_mail(selected_user, "Your payment was denied", body):
                    app.logger.info("ADMIN ACTION: Email sending FAILED")
                    return "EMAIL SENDING FAILED"
                
                app.logger.info("ADMIN ACTION: DONE")

            raw_payments = queries.retrieve_payments(page, filter_str)
            payments = _payments(raw_payments)

            return json.dumps(
                {
                    'payments': payments,
                    'has_next': raw_payments.has_next,
                    'has_prev': raw_payments.has_prev
                }
            )
    else:
        return redirect(url_for('auth.login'))


@adm.route('/admin-retrieve-payments', methods=['GET', 'POST'])
@login_required
def admin_retrieve_payments():
    if current_user.is_admin:
        page = int(request.form.get('page', 1))
        filter_str = str(request.form.get('filterStr', "PENDING"))

        raw_payments = queries.retrieve_payments(page, filter_str)
        payments = _payments(raw_payments)

        return json.dumps(
            {
                'payments': payments,
                'has_next': raw_payments.has_next,
                'has_prev': raw_payments.has_prev
            }
        )
    else:
        return redirect(url_for('auth.login'))

    return redirect(url_for('auth.login'))


def _payments(raw_payments):
    return [
        OrderedDict(
            {
                'id': raw_payment.Payment.id,
                'email': raw_payment.email,
                'firstname': raw_payment.firstname,
                'lastname': raw_payment.lastname,
                'phonenumber': raw_payment.phonenumber,
                'category': raw_payment.Payment.category,
                'created': utils.serialize_datetime(raw_payment.Payment.created),
                'reference': raw_payment.Payment.reference,
                'amount_php': float(str(raw_payment.amount_php)),
                'amount_usd': float(str(raw_payment.amount_usd))
            }
        )
        for raw_payment in raw_payments.items
    ]
