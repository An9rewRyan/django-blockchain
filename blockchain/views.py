from datetime import datetime
from hashlib import sha256
import json
from typing import List
from uuid import uuid4
from urllib.parse import urlparse
from django.http import JsonResponse, HttpResponse

class Block:

    def __init__(self, previous_hash: str, difficulty: int,
                        version: int, time: str):
        self.headers = {
            'time': time,
            'nonce' : 0,
            'previous_hash' : previous_hash,
            'merkel_root' : '',
            'difficulty': difficulty,
            'version': version,
        }
        self.transactions = []
        self.transaction_counter = 0
        self.blocksize = 10 #in megabytes
    
    def hash_headers(self) -> str:
        return sha256(str(self.headers).encode()).hexdigest()
    
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
    
    def hash_block(self, nonce):
        encoded_block = (json.dumps(self.__dict__)+str(nonce)).encode()
        return sha256(encoded_block).hexdigest()
        
class Blockchain:

    def __init__(self):
        self.chain: List[Block] = []
        self.version = 1
        self.difficulty = 4
        self.nodes = set() 
        self.create_block()
    
    def get_last_block_hash(self) -> str:
        last_block : Block = self.chain[-1]
        last_block_hash = last_block.hash_headers()
        return last_block_hash
    
    def get_last_block(self) -> Block:
        return self.chain[-1]

    def give_block_nonce(self, updated_block:Block) -> None:
        for block in self.chain:
            if block.headers == updated_block.headers:
                self.chain.remove(block)
                self.chain.append(updated_block)
        return

    def create_block(self, previous_hash: str= "" ):
        block = Block(
            previous_hash = previous_hash, 
            difficulty = self.difficulty,
            version = self.version,
            time = datetime.now().strftime("%Y-%m-%d %H:%M:%S:%f")
        )
        self.chain.append(block)
        return block
    
    def is_chain_valid(self, chain: List[Block]):
        previous_block = chain[0]
        block_index = 1
        while block_index < len(chain):
            curr_block = chain[block_index]
            if curr_block.headers['previous_hash'] != previous_block.hash():
                return False
            hash_operation = curr_block.hash_block()
            if hash_operation[:self.difficulty] != '0'*self.difficulty:
                return False
            previous_block = curr_block
            block_index += 1
        return True

class Transaction:

    def __init___(self, sender: str, reciever: str, amount: int, time: str):
        self.sender = sender 
        self.reciever = reciever
        self.amount = amount
        self.time = time

blockchain = Blockchain()

def create_empty_block(request):
    block = blockchain.create_block(blockchain.get_last_block_hash())
    return JsonResponse(block.__dict__)

def mine_block(request):
    if request.method == 'GET':
        last_block = blockchain.get_last_block()
        nonce = 1
        while last_block.hash_block(nonce)[:blockchain.difficulty] != "0"*blockchain.difficulty:
            nonce +=1
            print(last_block.hash_block(nonce))

        last_block.headers["nonce"] = nonce
        blockchain.give_block_nonce(last_block)

        response = {'message': 'Congratulations, you just mined a block!',
                    'timestamp': last_block.headers['time'],
                    'nonce': nonce,
                    'previous_hash': last_block.headers['previous_hash']}

    return JsonResponse(response)

# Getting the full Blockchain
def get_chain(request):
    chain = []
    for block in blockchain.chain:
        chain.append(block.__dict__)

    response = {'chain': chain,
                'length': len(blockchain.chain)}

    return JsonResponse(response)

# Checking if the Blockchain is valid
def is_valid(request):
    if request.method == 'GET':
        is_valid = blockchain.is_chain_valid(blockchain.chain)
        if is_valid:
            response = {'message': 'All good. The Blockchain is valid.'}
        else:
            response = {'message': 'Houston, we have a problem. The Blockchain is not valid.'}
    return JsonResponse(response)

    
    
    
    
    
    
    
