import requests
import hashlib
from flask import Blueprint, redirect, render_template, request, url_for
from flask_login import login_required, current_user

from creativecoin.blockchain.block import Block
from creativecoin.blockchain.mine import start_mine
from creativecoin.blockchain.sync import sync, sync_block
from creativecoin.blockchain.tx import Tx
from creativecoin.blockchain import validate

from creativecoin import app

import datetime

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
    test = request.args.get("mode", "live")
    tx = request.get_json()

    sha = hashlib.sha256()

    try:
        user = str(current_user.email).encode('utf-8')
    except AttributeError as identifier:
        user = "jeppbautista@gmail.com".encode('utf-8')

    sha.update(user)
    wallet_address = sha.hexdigest()

    node_blocks = sync(test)
    last_block = node_blocks[-1]
    new_block = start_mine(last_block, tx)

    confirmation = 0

    for i in range(5):
        if validate.confirm(new_block, test):
            confirmation += 1

    new_block.confirm = confirmation
    return str(new_block.self_save(test))


@node.route('/create_tx', methods=["GET", "POST"])
def create_tx():
    """
    ```
    curl -XPOST localhost:5000/create_tx?mode=test -H 'Content-type:application/json' -d '{
        "from":"ccn-admin",
        "to":"030113470ac5b92c80f93e244786d134a894fb1b08d79b3b7cf77be7b620c0a3",
        "value":150
    }'
    ```
    """
    test = request.args.get('mode', 'live')

    confirmation = 5
    new_tx = Tx(request.get_json())

    if validate.valid_tx(new_tx):
        new_tx.confirm = confirmation

    if confirmation==5:
        x = requests.post('https://{}/mine?mode={}'.format(app.config['SERVER_NAME'],test), 
            headers={"Content-type":"application/json"}, 
            json=new_tx.__dict__)

        if x.status_code != 200:
            app.logger.error("mine API failed")
            app.logger.error(x.text)

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
