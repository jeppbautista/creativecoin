import requests
import hashlib
from flask import Blueprint, redirect, render_template, request, url_for
from flask_login import login_required, current_user
from werkzeug import secure_filename

from creativecoin.blockchain.block import Block
from creativecoin.blockchain.mine import start_mine
from creativecoin.blockchain import queries
from creativecoin.blockchain.sync import sync, sync_block, sync_tx, sync_txs, sync_tx_from_wallet, sync_tx_aggs
from creativecoin.blockchain.tx import Tx
from creativecoin.blockchain import validate
from creativecoin.helper import utils
from creativecoin.models import Transaction

from creativecoin import app, db, es

import datetime
import decimal
import os
import time
import traceback
import subprocess

node = Blueprint("node", __name__)

@node.route("/ccn/explorer")
def explorer():
    test = request.args.get("mode", "live")
    txs = sync_txs(test)[:10]
    node_blocks = sync(test)[:10]
    return render_template("blockchain/explorer.html", 
        blocks=node_blocks, 
        txs=txs, 
        truncate=utils.truncate_string, serialize_dt=utils.serialize_datetime)


@node.route("/ccn/blocks")
def blocks():
    test = request.args.get("mode", "live")
    node_blocks = sync(test)
    return render_template("blockchain/blocks.html", blocks=node_blocks, serialize_dt=utils.serialize_datetime)


@node.route("/ccn/block/<block_id>")
def block(block_id):
    test = request.args.get("mode", "live")
    node_block = sync_block(block_id, test)
    transaction = sync_tx(block_id, test)
    return render_template("blockchain/block.html",
        block=node_block, 
        tx=transaction, 
        truncate=utils.truncate_string,
        serialize_dt=utils.serialize_datetime,
        title="Blockchain - CreativeCoin")


@node.route("/ccn/transactions")
def transactions():
    test = request.args.get("mode", "live")
    txs = sync_txs(test)
    return render_template("blockchain/transactions.html", txs=txs, serialize_dt=utils.serialize_datetime)


@node.route("/ccn/transaction/<txn_id>")
def transaction(txn_id):
    test = request.args.get("mode", "live")
    index = "tx" if test == "live" else "tx_test"

    txn = Transaction.query.filter(Transaction.txn_id == txn_id).first()

    return render_template("blockchain/transaction.html",
        txn=txn,
        truncate=utils.truncate_string,
        serialize_dt=utils.serialize_datetime,
        title="Transaction - CreativeCoin")


@node.route("/ccn/wallet/<address>")
def wallet(address):
    import pyqrcode
    filepath = "creativecoin/static/image/qr/{}".format(secure_filename(address))
    qr = pyqrcode.create(address)
    qr.svg("{}.svg".format(filepath), scale=6)

    test = request.args.get("mode", "live")
    txs = sync_tx_from_wallet(address, test)
    aggs = sync_tx_aggs(address, test)

    return render_template("blockchain/wallet.html", 
        address=address,
        aggs=aggs,
        txs=txs, 
        truncate=utils.truncate_string,
        serialize_dt=utils.serialize_datetime)


@node.route("/create-block")
def create_block():
    test = request.args.get("mode", "live")
    first_block = create_first_block()
    return first_block.self_save(test)


@node.route("/mine", methods=["GET", "POST"])
def mine():
    try:
        app.logger.error("INFO - /mine")
        test = request.args.get("mode", "live")
        tx = Tx(request.get_json())

        node_blocks = sync(test)
        last_block = node_blocks[0]
        new_block = start_mine(last_block, tx)
        tx.block = new_block.hash

        confirmation = 0

        for i in range(5):
            if validate.confirm(new_block, test):
                confirmation += 1

        new_block.confirm = confirmation
        block_created = new_block.self_save(test)
        # tx_created = tx.self_save(test)

        return str(block_created)
    except Exception:
        app.logger.error(traceback.format_exc())
        return "FAILED"


@node.route('/create_tx', methods=["GET", "POST"])
@node.route('/create_tx/<confirm>', methods=["GET", "POST"])
def create_tx(confirm=0):
    """
    ```
    curl -XPOST localhost:5000/create_tx?mode=test -H 'Content-type:application/json' -d '{
        "from_wallet":"ccn-system",
        "to_wallet":"21232f297a57a5a743894a0e4a801fc3",
        "value":150,
        "item_name": "",
        "quantity": 1,
        "txn_type" : "",
        "amount_php": 0,
        "amount_usd": 0,
        "amount_ccn": 0
    }'
    ```
    """
    app.logger.error("INFO - /create_tx")
    test = request.args.get('mode', 'live')

    confirmation = 3
    if confirm > 0:
        for i in range(confirm):
            time.sleep(60)

    new_tx = Tx(request.get_json())

    if validate.valid_tx(new_tx):
        new_tx.confirm = confirmation

    if confirmation == 3:
        node_blocks = sync(test)
        last_block = node_blocks[0]
        data = last_block.data
        data.append(new_tx.hash)
        new_tx.block = last_block.hash
        new_tx.self_save(test)
        last_block.data = data
        last_block.self_save(test)

        return "Transaction created"
    else:
        return "Transaction Failed"



def create_first_block():
    block_data = {}
    block_data['index'] = 0
    block_data['timestamp'] = datetime.datetime.utcnow().strftime(
        "%Y-%m-%dT%H:%M:%SZ")
    block_data['data'] = []
    block_data['prev_hash'] = ''
    block_data['nonce'] = 0
    block = Block(block_data)
    return block


@node.route("/c3RhcnRtaW5pbmc")
def start_mining():
    data = {
        "from_wallet": "21232f297a57a5a743894a0e4a801fc3",
        "to_wallet": "",
        "value": 1.0
    }

    test = request.args.get('mode', 'live')

    if app.config['ENV'] == "production":
        curl_req = "curl -XPOST https://{}/mine -H 'Content-type:application/json' -d '{}'".format(
            app.config["SERVER_NAME"], str(data).replace("'", '"'))
        x = subprocess.Popen(curl_req, shell=True,
                             stdout=subprocess.PIPE).stdout.read()
    else:
        x = requests.post('http://{}/mine?mode={}'.format(app.config['SERVER_NAME'], test),
                          headers={"Content-type": "application/json"},
                          json=data)
        app.logger.error("INFO - {}".format(x.text))

    wallets = queries.get_all_wallets()

    for wallet in queries.get_all_wallets():
        try:
            to = utils.generate_wallet_id(str(wallet.id))
            wallet.mined = wallet.mined+decimal.Decimal(1.0)

            data["to_wallet"] = to
            data["hash"] = utils.generate_txn_id(wallet.id)

            if app.config['ENV'] == "production":

                curl_req = "curl -XPOST https://{}/create_tx -H 'Content-type:application/json' -d '{}'".format(
                    app.config["SERVER_NAME"], str(data).replace("'", '"'))
                x = subprocess.Popen(curl_req, shell=True,
                                     stdout=subprocess.PIPE).stdout.read()

                app.logger.error(x)

            else:
                x = requests.post("http://{}/create_tx?mode={}".format(app.config["SERVER_NAME"], test),
                                  headers={"Content-type": "application/json"},
                                  json=data)

                app.logger.error("INFO - {}".format(x.text))

            grain = utils.get_grain()
            usd = utils.get_usd()

            amount_usd = grain
            amount_php = grain*usd
            transaction = Transaction(
                txn_id=data["hash"],
                item_name="CreativeCoin (Mined)",
                quantity=data["value"],
                is_verified=1,
                is_transferred=1,
                status="ACCEPTED",
                received_confirmations=3,
                txn_from=data["from_wallet"],
                txn_to=utils.generate_wallet_id(wallet.id),
                txn_type="MINE",
                amount_php=amount_php,
                amount_usd=amount_usd,
                amount_ccn=-1
            )

            db.session.add(transaction)
            queries.commit_db()
        except Exception:
            app.logger.error(traceback.format_exc())

    return ""
