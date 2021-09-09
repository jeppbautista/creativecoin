from creativecoin.blockchain.block import Block
from creativecoin.blockchain.tx import Tx
from creativecoin.blockchain import queries
from creativecoin import app, es

import os
import json

def sync(test='live'):
    node_blocks = []

    # chaindata_dir = 'creativecoin/blockchain/chaindata' if test=='live' else 'creativecoin/blockchain/chaindata-test'
    # chaindata_dir=os.path.join(os.getcwd(), chaindata_dir)
    
    # if os.path.exists(chaindata_dir):
    #     for filename in sorted(os.listdir(chaindata_dir)):
    #         filepath = '{}/{}'.format(chaindata_dir, filename)
    #         with open (filepath, 'r') as block_file:
    #             block_info = json.load(block_file)
    #             block_object = Block(block_info)
    #             node_blocks.append(block_object)

    index = "block" if test=="live" else "block_test"

    res = es.search(index=index, body=queries.get_all_blocks())["hits"]["hits"]
    for block in res:
        block_object = Block(block["_source"])
        node_blocks.append(block_object)

    return node_blocks


def sync_block(block, test='live'):
    # chaindata_dir = 'creativecoin/blockchain/chaindata' if test=='live' else 'creativecoin/blockchain/chaindata-test'
    # chaindata_dir = os.path.join(os.getcwd(), chaindata_dir)

    # file_id = str(block).zfill(9)
    # block_file = "{}/{}.json".format(chaindata_dir, file_id)
    # app.logger.error(block_file)
    # if os.path.exists(block_file):
    #     with open(block_file) as curr_lock_file:
    #         curr_block = Block(json.load(curr_lock_file))

    index = "block" if test=="live" else "block_test"
    res = es.search(index=index, body=queries.get_block(block))["hits"]["hits"][0]
    curr_block = Block(res["_source"])

    return curr_block


def sync_tx(block, test='live'):
    txs = []
    index = "tx" if test=="live" else "tx_test"

    res = es.search(index=index, body=queries.get_all_tx_from_block(block))["hits"]["hits"]
    for tx in res:
        txs.append(Tx(tx["_source"]))

    return txs


def sync_txs(test='live'):
    txs = []
    index = "tx" if test=="live" else "tx_test"

    res = es.search(index=index, body=queries.get_all_txs())["hits"]["hits"]
    for tx in res:
        txs.append(Tx(tx["_source"]))

    return txs


def sync_tx_from_wallet(wallet, test='live'):
    txs = []
    index = "tx" if test=="live" else "tx_test"

    res = es.search(index=index, body=queries.get_all_tx_from_wallet(wallet))["hits"]["hits"]
    for tx in res:
        txs.append(Tx(tx["_source"]))

    return txs


def sync_tx_aggs(wallet, test='live'):
    txs = []
    index = "tx" if test=="live" else "tx_test"

    total_trans = es.search(index=index, body=queries.get_total_trans_aggs_tx_from_wallet(wallet))["aggregations"]["total_transaction"]["value"]
    total_received = es.search(index=index, body=queries.get_total_rec_aggs_tx_from_wallet(wallet))["aggregations"]["total_received_filter"]["total_received"]["value"]
    total_sent = es.search(index=index, body=queries.get_total_sent_aggs_tx_from_wallet(wallet))["aggregations"]["total_sent_filter"]["total_sent"]["value"]

    return {
        "total_trans": total_trans,
        "total_received": total_received,
        "total_sent": total_sent
    }
