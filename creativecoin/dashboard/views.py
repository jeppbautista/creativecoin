from flask import Blueprint, redirect, request, url_for, render_template
from flask_login import login_required, current_user

from datetime import datetime
from sqlalchemy import or_

from creativecoin import app
from creativecoin.dashboard import helpers
from creativecoin.helper.utils import get_grain, sci_notation, generate_referral_id, generate_wallet_id
from creativecoin.models import *


dash = Blueprint('dash', __name__)

@dash.route("/wallet")
@login_required
def wallet():
    walletmodel = Wallet.query.filter_by(user_id=current_user.id).first()
    walletmodel.free_mined = sci_notation(walletmodel.free_mined)
    walletmodel.mined = sci_notation(walletmodel.mined)
    walletmodel.referral = sci_notation(walletmodel.referral)

    wallet_id = generate_wallet_id(walletmodel.id)

    transactions = Transaction.query\
        .filter(or_(wallet_id==Transaction.txn_from, wallet_id==Transaction.txn_to))\
            .order_by(Transaction.created.desc()).limit(10).all()

    grainprice = get_grain()
    grainprice = round(grainprice, 4)
    # txs = Transaction.query.filter_by()
    now = datetime.now()

    import qrcode

    import base64
    from io import BytesIO

    qr = qrcode.QRCode(version=1, border=3)

    qr.add_data(wallet_id)
    qr.make(fit=True)

    img = qr.make_image(fill='black', back_color='white')
    buffered = BytesIO()
    img.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")

    return render_template('wallet/wallet.html', 
            wallet=walletmodel, 
            wallet_id=wallet_id,
            now=now, 
            grainprice=grainprice, 
            generate_ref=generate_referral_id, 
            txn=transactions,
            img_str=img_str,
            title="Wallet - CreativeCoin")
