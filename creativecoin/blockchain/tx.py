import hashlib
import datetime

from creativecoin import app

class Tx(object):
    def __init__(self, kwargs):
        TX_VAR_CONVERSIONS = {
            'value': float
        }
        for k,v in kwargs.items():
            setattr(self, k, TX_VAR_CONVERSIONS.get(k, str)(v))
        
        try:
            self.timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

            if not hasattr(self, 'hash'):
                self.hash = self.create_self_hash()
            
            if not hasattr(self, 'status'):
                self.status = False

            if not hasattr(self, 'confirm'):
                self.confirm = 0

            self.raw_value = self.value
            # self.blockchain_fee = app.config['BLOCKCHAIN_FEE']*float(self.raw_value)
            self.value = self.raw_value 
            self.size = len(str(self.__dict__))
        except AttributeError as e:
            self.hash = None


    def __repr__(self):
        return "Transaction<hash: {} >".format(self.hash)


    def create_self_hash(self):
        # Generate hash for transactions; formula is:
        #   HASH(from + to + value + timestamp)
    
        sha = hashlib.sha256()
        sha.update((str(self.from_wallet) + str(self.to_wallet) + str(self.value) + self.timestamp).encode('utf-8'))
        new_hash = sha.hexdigest()

        return new_hash