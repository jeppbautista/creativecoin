from creativecoin.blockchain.block import Block
from creativecoin import app

import os
import json

def sync(test='live'):
    node_blocks = []

    chaindata_dir = 'creativecoin/blockchain/chaindata' if test=='live' else 'creativecoin/blockchain/chaindata-test'
    chaindata_dir=os.path.join(os.getcwd(), chaindata_dir)
    
    if os.path.exists(chaindata_dir):
        for filename in sorted(os.listdir(chaindata_dir)):
            filepath = '{}/{}'.format(chaindata_dir, filename)
            with open (filepath, 'r') as block_file:
                block_info = json.load(block_file)
                block_object = Block(block_info)
                node_blocks.append(block_object)
                
    return node_blocks


def sync_block(block, test='live'):
    chaindata_dir = 'creativecoin/blockchain/chaindata' if test=='live' else 'creativecoin/blockchain/chaindata-test'
    chaindata_dir = os.path.join(os.getcwd(), chaindata_dir)

    file_id = str(block).zfill(9)
    block_file = "{}/{}.json".format(chaindata_dir, file_id)
    app.logger.error(block_file)
    if os.path.exists(block_file):
        with open(block_file) as curr_lock_file:
            curr_block = Block(json.load(curr_lock_file))

    return curr_block
