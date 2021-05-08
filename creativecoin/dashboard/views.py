from flask import Blueprint, redirect, request, url_for, render_template
from flask_login import login_required, current_user
from werkzeug import secure_filename

from sqlalchemy import or_

from creativecoin import app, db, es
from creativecoin.dashboard.forms import Send
from creativecoin.error import ERROR_MESSAGE_LOOKUP
from creativecoin.helper.utils import get_grain, get_usd, sci_notation, generate_referral_id, generate_txn_id, \
    generate_wallet_id
from creativecoin.models import *

import decimal
import requests
import subprocess
import traceback

dash = Blueprint('dash', __name__)


@dash.route("/send_ccn", methods=["GET", "POST"])
def send_ccn():
    """
       ```
       curl -XPOST localhost:5000/create_tx?mode=test -H 'Content-type:application/json' -d '{
           "from_wallet":"ccn-system",
           "to_wallet":"21232f297a57a5a743894a0e4a801fc3",
           "value":150,
           "item_name": "",
           "txn_type" : "",
           "amount_php": 0,
           "amount_usd": 0,
           "amount_ccn": 0
       }'
       ```
       """
    test = request.args.get("mode", "live")
    response = None

    params = {}
    app.logger.error("INFO - /send_ccn")
    send = Send(request.form)

    if send.validate():

        wallet = Wallet.query.filter_by(user_id=current_user.id).first()
        to_wallet = Wallet.query.filter_by(wallet_id=send.to_wallet.data).first()
        from_wallet_id = wallet.wallet_id

        app.logger.error("INFO - Sending... WalletID: {}".format(str(wallet.id)))

        grain = get_grain()
        usd = get_usd()

        amount_usd = grain
        amount_php = grain * usd

        data = {
            "hash": generate_txn_id(str(wallet.id)),
            "from_wallet": from_wallet_id,
            "to_wallet": send.to_wallet.data,
            "value": send.amount.data,
            "item_name": "",
            "txn_type": "SEND",
            "amount_php": amount_php,
            "amount_usd": amount_usd
        }

        try:
            if app.config['ENV'] == "production":

                curl_req = "curl -XPOST https://{}/create_tx -H 'Content-type:application/json' -d '{}'".format(
                    app.config["SERVER_NAME"], str(data).replace("'", '"'))
                response = subprocess.Popen(
                    curl_req,
                    shell=True,
                    stdout=subprocess.PIPE).stdout.read()

                app.logger.error("INFO - {}".format(response.text))

            else:
                response = requests.post(
                    "http://{}/create_tx?mode={}".format(
                        app.config["SERVER_NAME"], test),
                    headers={"Content-type": "application/json"},
                    json=data)

                app.logger.error("INFO - {}".format(response.text))

        except Exception:
            app.logger.error(traceback.format_exc())
            params["error"] = "default_error"
            return redirect(url_for("dash.wallet", **params))

        if response and response.status_code == 200:

            try:
                if send.sourcewallet.data == "0":
                    wallet.mined = wallet.mined - send.amount.data
                elif send.sourcewallet.data == "1":
                    wallet.free_mined = wallet.free_mined - send.amount.data
                elif send.sourcewallet.data == "2":
                    wallet.received = wallet.received - send.amount.data
                else:
                    raise Exception("Invalid source wallet selected")

                db.session.commit()
                app.logger.error("INFO - {} credited from source: {}".format(send.amount.data, wallet.wallet_id))

                transaction_fee = send.amount.data * 0.1
                net_amount = send.amount.data - transaction_fee
                net_amount = decimal.Decimal(net_amount)

                if send.sourcewallet.data == "0":
                    to_wallet.mined = to_wallet.mined + net_amount
                elif send.sourcewallet.data == "1":
                    to_wallet.free_mined = to_wallet.free_mined + net_amount
                elif send.sourcewallet.data == "2":
                    to_wallet.received = to_wallet.received + net_amount
                else:
                    raise Exception("Invalid source wallet selected")

                db.session.commit()
                app.logger.error("INFO - {} debited to source: {}".format(net_amount, to_wallet.wallet_id))
            except Exception:
                app.logger.error(traceback.format_exc())

            params["status"] = "transfer_successful"
            return redirect(url_for("dash.wallet", **params))

    app.logger.error("ERROR - {}".format(send.errors))
    if "amount" in send.errors.keys():
        params["error"] = "send_form_amount"
    elif "to_wallet" in send.errors.keys():
        params["error"] = "send_form_invalid_wallet"
    else:
        params["error"] = "default_error"
    return redirect(url_for("dash.wallet", **params))


@dash.route("/wallet")
@login_required
def wallet():
    err = request.args.get("error", None)
    status = request.args.get("status", None)
    if err:
        err = ERROR_MESSAGE_LOOKUP.get(err, ERROR_MESSAGE_LOOKUP["default_error"])

    walletmodel = Wallet.query.filter_by(user_id=current_user.id).first()
    walletmodel.free_mined = sci_notation(walletmodel.free_mined)
    walletmodel.mined = sci_notation(walletmodel.mined)
    walletmodel.referral = sci_notation(walletmodel.referral)
    walletmodel.total_balance = sci_notation(walletmodel.total_balance)


    wallet_id = walletmodel.wallet_id

    transactions = Transaction.query \
        .filter(or_(wallet_id == Transaction.txn_from, wallet_id == Transaction.txn_to)) \
        .order_by(Transaction.created.desc()).limit(10).all()

    grainprice = get_grain()
    grainprice = round(grainprice, 4)
    # txs = Transaction.query.filter_by()
    now = datetime.datetime.now()

    sendform = Send()

    import pyqrcode
    filepath = "creativecoin/static/image/qr/{}".format(secure_filename(wallet_id))
    qr = pyqrcode.create(wallet_id)
    qr.svg("{}.svg".format(filepath), scale=8)

    return render_template('wallet/wallet.html',
                           wallet=walletmodel,
                           wallet_id=wallet_id,
                           now=now,
                           grainprice=grainprice,
                           generate_ref=generate_referral_id,
                           txn=transactions,
                           sendform=sendform,
                           err=err,
                           status=status,
                           title="Wallet - CreativeCoin")

