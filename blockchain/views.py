from audioop import maxpp
from datetime import datetime
from hashlib import sha256
import json
from typing import List
from uuid import uuid4
from urllib.parse import urlparse
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt 
from requests import get
import ast

class Transaction:

    def __init___(self, sender: str, reciever: str, amount: int, time: str):
        self.sender = sender 
        self.reciever = reciever
        self.amount = amount
        self.time = time

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
        
class Blockchain:

    def __init__(self):
        self.nodes = set()
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
            if block.headers["previous_hash"] == updated_block.headers["previous_hash"]:
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
            hash_operation = curr_block.hash_block(curr_block.headers["nonce"])
            if curr_block.headers['previous_hash'] != previous_block.hash_headers():
                
                return False
            
            if hash_operation[:self.difficulty] != '0'*self.difficulty:
                return False
            previous_block = curr_block
            block_index += 1
        return True

    def add_transaction(self, sender, receiver, amount, time): #New
        transaction = Transaction(sender, receiver, amount, datetime.now().strftime("%Y-%m-%d %H:%M:%S:%f"))
        max_space = 0
        max_space_block = self.chain[0] #filling the first for test purposes
        for block in self.chain:
            if block.blocksize > max_space:
                max_space = self.chain[0].blocksize
                max_space_block = block
        
        self.chain.remove(max_space_block)

        max_space_block.transaction_counter+=1
        max_space_block.transactions.append(transaction.__dict__)

        self.chain.append(max_space_block)

        return

    def add_node(self, address): #New
        parsed_url = urlparse(address)
        self.nodes.add(parsed_url.netloc)

    def replace_chain(self): #New
        network = self.nodes
        longest_chain = None
        max_length = len(self.chain)
        for node in network:
            response = get(f'http://{node}/get_chain')
            if response.status_code == 200:
                length = response.json()["length"]
                chain = response.json()["chain"]

                new_chain = []

                for block in chain:
                    new_chain.append(Block(
                        previous_hash=block["headers"]["previous_hash"],
                        difficulty=self.difficulty,
                        version=self.version,
                        nonce=block["headers"]["nonce"],
                        time = block["headers"]["time"]
                    ))
                print(length, new_chain, self.is_chain_valid(new_chain))
                if length > max_length and self.is_chain_valid(new_chain):
                    max_length = length
                    longest_chain = new_chain
        if longest_chain:
            self.chain = longest_chain
            return True
        return False

blockchain = Blockchain()
node_address = str(uuid4()).replace('-', '') #New
root_node = 'e36f0158f0aed45b3bc755dc52ed4560d' #New


def create_empty_block(request):
    block = blockchain.create_block(blockchain.get_last_block_hash())
    return JsonResponse(block.__dict__)

def mine_block(request):
    if request.method == 'GET':
        last_block = blockchain.get_last_block()
        nonce = 1
        while last_block.hash_block(nonce)[:blockchain.difficulty] != "0"*blockchain.difficulty:         
            nonce +=1
            last_block.headers["nonce"] = nonce
            print(last_block.hash_block(nonce), nonce)


        blockchain.give_block_nonce(last_block)

        response = {'message': 'Congratulations, you just mined a block!',
                    'timestamp': last_block.headers['time'],
                    'nonce': nonce,
                    'previous_hash': last_block.headers['previous_hash']}

    return JsonResponse(response)

def get_chain(request):
    chain = []
    for block in blockchain.chain:
        chain.append(block.__dict__)

    response = {"chain": chain,
                "length": len(blockchain.chain)}
    print(ast.literal_eval(json.dumps(response)))

    return JsonResponse(ast.literal_eval(json.dumps(response)))

def is_valid(request):
    if request.method == 'GET':
        is_valid = blockchain.is_chain_valid(blockchain.chain)
        if is_valid:
            response = {'message': 'Blockchain is valid.'}
        else:
            response = {'message': 'Blockchain is not valid.'}
    return JsonResponse(response)


@csrf_exempt
def add_transaction(request): #New
    if request.method == 'POST':
        received_json = json.loads(request.body)
        transaction_keys = ['sender', 'receiver', 'amount','time']
        if not all(key in received_json for key in transaction_keys):
            return 'Some elements of the transaction are missing', HttpResponse(status=400)
        index = blockchain.add_transaction(received_json['sender'], received_json['receiver'], received_json['amount'],received_json['time'])
        response = {'message': f'This transaction will be added to Block {index}'}
    return JsonResponse(response)

# Connecting new nodes
@csrf_exempt
def connect_node(request): #New
    if request.method == 'POST':
        received_json = json.loads(request.body)
        nodes = received_json.get('nodes')
        if nodes is None:
            return "No node", HttpResponse(status=400)
        for node in nodes:
            blockchain.add_node(node)
        response = {'message': 'All the nodes are now connected. The Opezdeilcoin Blockchain now contains the following nodes:',
                    'total_nodes': list(blockchain.nodes)}
    return JsonResponse(response)

# Replacing the chain by the longest chain if needed
def replace_chain(request): #New
    chain = []
    for block in blockchain.chain:
        chain.append(block.__dict__)
    if request.method == 'GET':
        is_chain_replaced = blockchain.replace_chain()
        if is_chain_replaced:
            response = {'message': 'The nodes had different chains so the chain was replaced by the longest one.',
                        'new_chain': chain}
        else:
            response = {'message': 'All good. The chain is the largest one.',
                        'actual_chain': chain}
    print("\n\n\n\n\n\n\n")
    return JsonResponse(response)


    
    
    
    
    
    
    
