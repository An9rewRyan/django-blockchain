from typing import List
from .Block import Block
from .Transaction import Transaction
from datetime import datetime
from requests import get
from urllib.parse import urlparse
from threading import Thread
from time import sleep

class Blockchain:

    def __init__(self):
        self.nodes = set()
        self.chain: List[Block] = []
        self.version = 1
        self.difficulty = 2**234
        self.spawn_period = 120 #in seconds
        self.nodes = set() 
    
    def spawn_block(self) -> None:
        print("Here!")
        while True:
            block = Block(
                previous_hash = self.get_last_block_hash(), 
                difficulty = self.difficulty,
                version = self.version,
                time = datetime.now().strftime("%Y-%m-%d %H:%M:%S:%f")
            )
            self.chain.append(block)
            print("New block spawned!")
            sleep(self.spawn_period)

    def get_last_block(self) -> Block:
        return self.chain[-1]

    def get_last_block_hash(self) -> str:
        if len(self.chain) > 1:
            last_block = self.get_last_block()
            last_block_hash = last_block.hash_headers()
            return last_block_hash
        else:
            return " "

    def set_block_nonce(self, updated_block: Block) -> None:
        for block in self.chain:
            if block.headers["previous_hash"] == updated_block.headers["previous_hash"]:
                self.chain.remove(block)
                self.chain.append(updated_block)
        return

    def is_chain_valid(self, chain: List[Block]) -> bool:
        previous_block = chain[0]
        block_index = 1
        while block_index < len(chain):
            curr_block = chain[block_index]
            hash_operation = curr_block.hash_block(curr_block.headers["nonce"])
            if curr_block.headers['previous_hash'] != previous_block.hash_headers():
                print("Hash headers wrong")
                return False
            
            if hash_operation[:self.difficulty] != '0'*self.difficulty:
                print(hash_operation, " not walid proof of work")
                return False
            previous_block = curr_block
            block_index += 1
        return True

    def add_transaction(self, sender, receiver, amount): #New
        transaction = Transaction(sender, receiver, amount, datetime.now().strftime("%Y-%m-%d %H:%M:%S:%f"))

        max_space_block = self.chain[0] #filling the first for test purposes

        max_space_block.transaction_counter+=1
        max_space_block.transactions.append(transaction.__dict__)
         #this is necessary for recourrsive set_merkel_root func to work

        if max_space_block.transaction_counter % 4 == 0:
            max_space_block.headers["merkel_root"] = max_space_block.transactions
            max_space_block.set_merkel_root()

        self.chain.append(max_space_block)

        return

    def add_node(self, address): #New
        parsed_url = urlparse(address)
        self.nodes.add(parsed_url.netloc)

    def dict_chain_to_block_chain(self, chain: List[dict]) -> List[Block]:
        block_chain = []
        for block in chain:
            block_chain.append(Block(
                previous_hash=block["headers"]["previous_hash"],
                difficulty=self.difficulty,
                version=self.version,
                nonce=block["headers"]["nonce"],
                time = block["headers"]["time"]
        ))
        return block_chain

    def replace_chain(self): #New
        network = self.nodes
        longest_chain = None
        max_length = len(self.chain)
        for node in network:
            response = get(f'http://{node}/get_chain')
            if response.status_code == 200:
                length = response.json()["length"]
                dict_chain = response.json()["chain"]

                new_chain = self.dict_chain_to_block_chain(dict_chain)

                print(length, new_chain, self.is_chain_valid(new_chain))
                if length > max_length and self.is_chain_valid(new_chain):
                    max_length = length
                    longest_chain = new_chain
        if longest_chain:
            self.chain = longest_chain
            return True
        return False