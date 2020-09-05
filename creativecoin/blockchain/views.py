import requests
import hashlib
from flask import Blueprint, redirect, render_template, request, url_for
from flask_login import login_required, current_user

from creativecoin.blockchain.block import Block
from creativecoin.blockchain.mine import start_mine
from creativecoin.blockchain import queries
from creativecoin.blockchain.sync import sync, sync_block
from creativecoin.blockchain.tx import Tx
from creativecoin.blockchain import validate
from creativecoin.helper import utils

from creativecoin import app

import datetime
import decimal
import traceback
import subprocess

node = Blueprint("node", __name__)


@node.route("/ccn/block/<block_id>")
def block(block_id):
    test = request.args.get("mode", "live")
    node_block = sync_block(block_id, test)
    transaction = eval(node_block.data)[1:]
    return render_template("blockchain/block.html", block=node_block, tx=transaction,
            title="Blockchain - CreativeCoin")


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
        tx = request.get_json()

        node_blocks = sync(test)
        last_block = node_blocks[-1]
        new_block = start_mine(last_block, tx)

        confirmation = 0

        for i in range(5):
            if validate.confirm(new_block, test):
                confirmation += 1

        new_block.confirm = confirmation
        return str(new_block.self_save(test))
    except Exception:
        app.logger.error(traceback.format_exc())

    return "ERROR"


@node.route('/create_tx', methods=["GET", "POST"])
def create_tx():
    """
    ```
    curl -XPOST localhost:5000/create_tx?mode=test -H 'Content-type:application/json' -d '{
        "from_wallet":"ccn-system",
        "to_wallet":"8BC96FAB127BE5FE51A6E7E8F2F1EA41",
        "value":150
    }'
    ```
    """
    app.logger.error("INFO - /create_tx")
    test = request.args.get('mode', 'live')

    confirmation = 5
    new_tx = Tx(request.get_json())
    new_tx.hash = utils.generate_txn_id(new_tx.to_wallet)

    if validate.valid_tx(new_tx):
        new_tx.confirm = confirmation

    if confirmation == 5:
        node_blocks = sync(test)
        last_block = node_blocks[-1]
        data = eval(last_block.data)
        data.append(new_tx.__dict__)
        last_block.data = str(data)
        last_block.self_save(test)

    return "Transaction created"


def create_first_block():
    block_data = {}
    block_data['index'] = 0
    block_data['timestamp'] = datetime.datetime.now()
    block_data['data'] = []
    block_data['prev_hash'] = ''
    block_data['nonce'] = 0
    block = Block(block_data)
    return block


@node.route("/c3RhcnRtaW5pbmc")
def start_mining():
    # TODO transactions
    data = {
        "from_wallet": "8BC96FAB127BE5FE51A6E7E8F2F1EA41",
        "to_wallet": "",
        "value": 12.0
    }

    test = request.args.get('mode', 'live')

    if app.config['ENV'] == "production":
        curl_req = "curl -XPOST https://{}/mine -H 'Content-type:application/json' -d '{}'".format(
        app.config["SERVER_NAME"], str(data).replace("'", '"'))
        x = subprocess.Popen(curl_req, shell=True, stdout=subprocess.PIPE).stdout.read()
    else:
        x = requests.post('http://{}/mine?mode={}'.format(app.config['SERVER_NAME'], test),
                    headers={"Content-type": "application/json"},
                    json=data)
        app.logger.error("INFO - {}".format(x.text))

    
    for wallet in queries.get_all_wallets():
        try:
            to = utils.generate_wallet_id(str(wallet.id))
            wallet.mined = wallet.mined+decimal.Decimal(12.0)

            data["to_wallet"] = to

            if app.config['ENV'] == "production":

                curl_req = "curl -XPOST https://{}/create_tx -H 'Content-type:application/json' -d '{}'".format(
                    app.config["SERVER_NAME"], str(data).replace("'", '"'))
                x = subprocess.Popen(curl_req, shell=True, stdout=subprocess.PIPE).stdout.read()
                
                app.logger.error(x)

            else:
                x = requests.post("http://{}/create_tx?mode={}".format(app.config["SERVER_NAME"], test), 
                    headers={"Content-type":"application/json"}, 
                    json=data)

                app.logger.error("INFO - {}".format(x.text))
                
            queries.commit_db()
        except Exception:
            app.logger.error(traceback.format_exc())
        
    return ""
