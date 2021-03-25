import hashlib
import datetime

from creativecoin import app, es


class Block(object):
    def __init__(self, kwargs):
        self.index = None
        self.timestamp = None
        self.prev_hash = None
        self.hash = None
        self.nonce = None
        self.confirm = None

        BLOCK_VAR_CONVERSIONS = {
            'index': int, 
            'nonce': int, 
            'hash': str, 
            'prev_hash': str,
            'data': list
        }
        
        for k,v in kwargs.items():
            setattr(self, k, BLOCK_VAR_CONVERSIONS.get(k, str)(v))

        if not hasattr(self, 'hash'):
            self.hash = self.create_self_hash()
        if not hasattr(self, 'nonce'):
            self.nonce = ''
        if not hasattr(self, 'confirm'):
            self.confirm = 0

    def __dict__(self):
        info = {}
        info['index'] = str(self.index)
        info['timestamp'] = self.timestamp
        info['prev_hash'] = str(self.prev_hash)
        info['hash'] = str(self.hash)
        info['data'] = list(self.data)
        info['nonce'] = str(self.nonce)
        info['confirm'] = str(self.confirm)
        return info

    def __eq__(self, other):
        return (self.index == other.index and
                self.timestamp == other.timestamp and
                self.prev_hash == other.prev_hash and
                self.hash == other.hash and
                self.data == other.data and 
                self.nonce == other.nonce)

    def __ne__(self, other):
        return not self.__eq__(other)
    
    def __repr__(self):
        return "Block<index: {} , hash: {}>".format(self.index, self.hash)

    def is_valid(self):
        self.update_self_hash()
        try:
            num_zero = app.config['NUM_ZEROS']
        except:
            num_zero = 3

        if(str(self.hash[0:num_zero])) == '0'*num_zero:
            return True
        else:
            return False

    def header_string(self):
        return str(self.index) + str(self.prev_hash) + str(self.data) + str(self.timestamp) + str(self.nonce)

    def compute_height(self):
        return (datetime.datetime.now() - datetime.datetime.strptime(self.timestamp, "%Y-%m-%dT%H:%M:%SZ")).days * 48

    def create_self_hash(self):
        sha = hashlib.sha256()
        sha.update(self.header_string().encode('utf-8'))
        return sha.hexdigest()

    def update_self_hash(self):
        sha = hashlib.sha256()
        sha.update(self.header_string().encode('utf-8'))
        new_hash = sha.hexdigest()
        self.hash = new_hash
        return new_hash

    def self_save(self, test='live'):
        # chaindata_dir = 'creativecoin/blockchain/chaindata' if test=='live' else 'creativecoin/blockchain/chaindata-test'
        # print("Self save: " + chaindata_dir)

        # chaindata_dir = os.path.join(os.getcwd(), chaindata_dir)

        index = "block" if test == "live" else "block_test"

        try:
            index_string = str(self.index).zfill(9) #front of zeros so they stay in numerical order
            # filename = '{}/{}.json'.format(chaindata_dir,   index_string)

            # with open(filename, 'w+') as block_file:
            #     json.dump(self.__dict__(), block_file)
            es.index(index=index, id=self.hash, body=self.__dict__())
            
        except Exception as ex:
            raise Exception(ex)
        
        return "Success"

