from hashlib import sha256
import json

class Block:

    def __init__(self, previous_hash: str, difficulty: int, version: int, time: str, nonce: int=0):
        self.headers = {
            'time': time,
            'nonce' : nonce,
            'previous_hash' : previous_hash,
            'merkel_root' : '',
            'difficulty': difficulty,
            'version': version,
        }
        self.transactions = []
        self.transaction_counter = 0
        self.blocksize = 10 #in megabytes
    
    def get_merkel_root(self, transactions) -> str:
        if transactions != 1:
            hashed_trunsactions = []
            for i in range(0, len(transactions)-1, 2):
                curr_hex = sha256(transactions[i].encode()).hexdigest()
                next_hex = sha256(transactions[i+1].encode()).hexdigest()
                hash_pair = sha256((curr_hex+next_hex).encode()).hexdigest()
                hashed_trunsactions.append(hash_pair)
            return self.get_merkel_root(self, hashed_trunsactions)
        else:
            return transactions

    def hash_headers(self) -> str:
        return sha256(str(self.headers).encode()).hexdigest()

    def hash_block(self, nonce):
        encoded_block = (json.dumps(self.__dict__)+str(nonce)).encode()
        return sha256(encoded_block).hexdigest()