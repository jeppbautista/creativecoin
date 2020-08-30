import json
import os

from creativecoin.blockchain.block import Block

def confirm(block, test):
    chaindata_dir = 'creativecoin/blockchain/chaindata' if test=='live' else 'creativecoin/blockchain/chaindata-test'
    chaindata_dir = os.path.join(os.getcwd(), chaindata_dir)
    
    prev_file_id = str(block.index-1).zfill(9)
    prev_file = "{}/{}.json".format(chaindata_dir, prev_file_id)
    
    if os.path.exists(prev_file):
        with open(prev_file) as prev_block_file:
            prev_block = Block(json.load(prev_block_file))

    if block.prev_hash == prev_block.hash:
        return True
    return False

def valid_tx(tx):
    if tx.hash is None:
        return False
    return True