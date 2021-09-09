from creativecoin.blockchain.block import Block
import hashlib

class Chain(object):
    def __init__(self, blocks):
        self.blocks = blocks
        self.current_transactions = []

    def __eq__(self, other):
        if len(self)!=len(other):
            return False
        for self_block, other_block in zip(self.blocks, other.blocks):
            if self_block != other_block:
                return False
        return True


    def __gt__(self, other):
        return len(self.blocks) > len(other.blocks)


    def __ge__(self, other):
        return self.__eq__(other) or self.__gt__(other)


    def __len__(self):
        return len(self.blocks)


    def get_by_index(self, index):
        if len(self)<=index:
            return self.blocks[index]
        else:
            return False


    def get_by_hash(self, hash):
        for b in self.blocks:
            if b.hash == hash:
                return b
        return False


    def is_valid(self):
        '''
            Is a valid blockchain if
            1) Each block is indexed one after the other
            2) Each block's prev hash is the hash of the prev block
            3) The block's hash is valid for the number of zeros
        '''      
        for index, cur_block in enumerate(self.blocks[1:]):
            prev_block = self.blocks[index]
            if prev_block.index +1 != cur_block.index:
                return False
            
            if not cur_block.is_valid():
                return False

            if prev_block.hash != cur_block.prev_hash:
                return False
        return True


    def add_block(self, new_block):
        #TODO handle this
        self.blocks.append(new_block)
        return True


    # def add_transaction(self, sender, recipient, amount):
        # sha = hashlib.sha256()
        # details = str(sender) + str(recipient) + str(amount)
        # sha.update(details.encode('utf-8'))
    #     self.current_transactions.append({
    #         'txid': sha.hexdigest(),
    #         'sender': sender,
    #         'recipient': recipient,
    #         'amount': amount
    #     })
    def last_block(self):
        return self.blocks[-1]

    
    def self_save(self):
        for b in self.blocks:
            b.self_save()
        return True

    
    def to_list(self):
        return [b.__dict__() for b in self.blocks]

    
