from flask import Blueprint, jsonify, redirect, request, render_template, url_for
from flask_login import login_required, current_user

from collections import OrderedDict
import json

from creativecoin.admin import queries
from creativecoin.helper import utils
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
    page = int(request.form.get('page', 1))
    filter_str = str(request.form.get('filterStr', "PENDING"))

    if current_user.is_admin and payment_id:
        if queries.update_payment_status(payment_id, choice):

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
                'reference': raw_payment.Payment.reference
            }
        )
        for raw_payment in raw_payments.items
    ]
