import datetime
import time
import json
import hashlib

from creativecoin.blockchain.sync import sync
from creativecoin.blockchain.block import Block


def generate_header(kwargs):
    return str(kwargs['index']) +  kwargs['prev_hash']  +  str(kwargs['data'])  +  str(kwargs['timestamp']) + str(kwargs['nonce'])


def calculate_hash(**kwargs):
    header_string = generate_header(kwargs)
    sha = hashlib.sha256()
    sha.update(header_string.encode('utf-8'))
    return sha.hexdigest()


def start_mine(last_block, tx):
    index = int(last_block.index) + 1
    timestamp = datetime.datetime.now()
    # tx['block'] = index
    data = []
    prev_hash = last_block.hash
    nonce = 0
    
    try:
        num_zero = app.config['NUM_ZEROS']
    except:
        num_zero = 3
    
    block_hash = calculate_hash(index=index, 
                                prev_hash=prev_hash,
                                data=data,
                                timestamp=timestamp,
                                nonce=nonce )

    while(block_hash[0:num_zero]) != '0'*num_zero:
        nonce += 1
        block_hash = calculate_hash(index=index, 
                                prev_hash=prev_hash,
                                data=data,
                                timestamp=timestamp,
                                nonce=nonce )

    block_data = {}
    block_data['index'] = int(last_block.index) + 1
    block_data['timestamp'] = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    block_data['data'] = data
    block_data['prev_hash'] = last_block.hash
    block_data['hash'] = block_hash
    block_data['nonce'] = nonce
    return Block(block_data)

