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
    transaction = eval(node_block.data)[0]
    print(transaction)
    return render_template("blockchain/block.html", block=node_block, tx=transaction)


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
        "from":"ccn-system",
        "to":"030113470ac5b92c80f93e244786d134a894fb1b08d79b3b7cf77be7b620c0a3",
        "value":150
    }'
    ```
    """
    app.logger.error("INFO - /create_tx")
    test = request.args.get('mode', 'live')

    confirmation = 5
    new_tx = Tx(request.get_json())
    new_tx.hash = "12345"

    if validate.valid_tx(new_tx):
        new_tx.confirm = confirmation

    if confirmation==5:
        # x = requests.post('http://{}/mine?mode={}'.format(app.config['SERVER_NAME'],test), 
        #     headers={"Content-type":"application/json"}, 
        #     json=new_tx.__dict__)

        curl_req = "curl -XPOST https://{}/mine -H 'Content-type:application/json' -d '{}'".format(
                app.config["SERVER_NAME"], str(new_tx.__dict__).replace("'", '"'))
        x = subprocess.Popen(curl_req, shell=True, stdout=subprocess.PIPE).stdout.read()
        app.logger.error(x)

        # if x.status_code != 200:
        #     app.logger.error("ERROR - mine API failed")
        #     app.logger.error(x.text)

    return str(new_tx.__dict__)


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
    #TODO transactions
    data = {
        "from":"ccn-system",
        "to":"",
        "value":0.5
    }
    for wallet in queries.get_all_wallets():
        try:
            to = utils.generate_wallet_id(str(wallet.id))
            wallet.mined = wallet.mined+decimal.Decimal(0.5)

            data["to"] = to
            # x = requests.post("http://{}/create_tx".format(app.config["SERVER_NAME"]), json=data)
            curl_req = "curl -XPOST https://{}/create_tx -H 'Content-type:application/json' -d '{}'".format(
                app.config["SERVER_NAME"], str(data).replace("'", '"'))
            x = subprocess.Popen(curl_req, shell=True, stdout=subprocess.PIPE).stdout.read()
            app.logger.error(x)
            #     app.logger.error("ERROR - mine API failed")
            #     app.logger.error(x.text)
            #     continue
            queries.commit_db()
        except Exception:
            app.logger.error(traceback.format_exc())
        
    return ""