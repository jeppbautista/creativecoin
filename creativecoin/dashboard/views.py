from datetime import datetime

from flask import Blueprint, redirect, request, url_for, render_template
from flask_login import login_required, current_user

from creativecoin import app
from creativecoin.helper import utils
from creativecoin.models import *


dash = Blueprint('dash', __name__)

@dash.route("/wallet")
@login_required
def wallet():
    wallet = Wallet.query.filter_by(user_id=current_user.id).first()
    wallet.free_mined = utils.sci_notation(wallet.free_mined)
    wallet.mined = utils.sci_notation(wallet.mined)

    # txs = Transaction.query.filter_by()

    now = datetime.now()

    return render_template('dashboard/wallet.html', wallet=wallet, now=now)
