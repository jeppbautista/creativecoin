import hashlib
import datetime

from creativecoin import app, es


class Tx(object):
    def __init__(self, kwargs):
        TX_VAR_CONVERSIONS = {
            'value': float
        }
        for k,v in kwargs.items():
            setattr(self, k, TX_VAR_CONVERSIONS.get(k, str)(v))
        
        try:
            if not hasattr(self, 'timestamp'):
                self.timestamp = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")

            if not hasattr(self, 'hash'):
                self.hash = self.create_self_hash()
            
            if not hasattr(self, 'status'):
                self.status = False

            if not hasattr(self, 'confirm'):
                self.confirm = 0

            self.raw_value = self.value
            self.blockchain_fee = app.config['BLOCKCHAIN_FEE']*float(self.raw_value)
            self.value = self.raw_value 
            self.size = len(str(self.__dict__))
        except AttributeError as e:
            self.hash = None

    def __dict__(self):
        info = {}
        info['from_wallet'] = str(self.from_wallet)
        info['to_wallet'] = str(self.to_wallet)
        info['value'] = self.value
        info['block'] = str(self.block)
        info['timestamp'] = self.timestamp
        info['hash'] = self.hash
        info['status'] = self.status
        info['confirm'] = self.confirm
        info['raw_value'] = self.raw_value
        info['blockchain_fee'] = self.blockchain_fee
        info['size'] = self.size
        return info

    def __repr__(self):
        return "Transaction<hash: {} >".format(self.hash)

    def create_self_hash(self):
        sha = hashlib.sha1()
        sha.update((str(self.from_wallet) + str(self.to_wallet) + str(self.value) + self.timestamp).encode('utf-8'))
        new_hash = sha.hexdigest()

        return new_hash

    def self_save(self, test='live'):
        index = "tx" if test == "live" else "tx_test"

        try:
            es.index(index=index, id=self.hash, body=self.__dict__())
        except Exception as ex:
            app.logger.error("ERROR: {}".format(ex))
            return False

        return True

