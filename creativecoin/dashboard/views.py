from flask import Blueprint, redirect, request, url_for, render_template
from flask_login import login_required, current_user

from datetime import datetime

from creativecoin import app
from creativecoin.dashboard import helpers
from creativecoin.helper import utils
from creativecoin.models import *


dash = Blueprint('dash', __name__)

@dash.route("/wallet")
@login_required
def wallet():
    walletmodel = Wallet.query.filter_by(user_id=current_user.id).first()
    walletmodel.free_mined = utils.sci_notation(walletmodel.free_mined)
    walletmodel.mined = utils.sci_notation(walletmodel.mined)

    grainprice = helpers.get_grain_value()
    grainprice = round(grainprice, 4)
    # txs = Transaction.query.filter_by()

    now = datetime.now()


    return render_template('dashboard/wallet.html', wallet=walletmodel, now=now, grainprice=grainprice)
