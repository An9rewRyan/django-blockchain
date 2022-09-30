from hashlib import sha256
import json

class Block:

    def __init__(self, previous_hash: str, difficulty: int, version: int, time: str, nonce: int=0):
        self.headers = {
            'time': time,
            'nonce' : nonce,
            'previous_hash' : previous_hash,
            'merkel_root' : [],
            'difficulty': difficulty,
            'version': version,
        }
        self.transactions = []
        self.transaction_counter = 0
        self.blocksize = 10 #in megabytes
    
    def set_merkel_root(self) -> str:

        while len(self.headers["merkel_root"]) != 1:
            hashed_trunsactions = []
            for i in range(0, len(self.headers["merkel_root"])-1, 2):
                curr_hex = sha256(str(self.headers["merkel_root"][i]).encode()).hexdigest()
                next_hex = sha256(str(self.headers["merkel_root"][i+1]).encode()).hexdigest()
                hash_pair = sha256((curr_hex+next_hex).encode()).hexdigest()
                hashed_trunsactions.append(hash_pair)
                print(hashed_trunsactions,self.headers["merkel_root"])
            self.headers["merkel_root"] = hashed_trunsactions
        
        return self.headers["merkel_root"]

    def hash_headers(self) -> str:
        return sha256(str(self.headers).encode()).hexdigest()

    def hash_block(self, nonce):
        encoded_block = (json.dumps(self.__dict__)+str(nonce)).encode()
        return sha256(encoded_block).hexdigest()