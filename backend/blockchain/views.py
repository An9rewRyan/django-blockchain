import sys
sys.path.append('./classes')
import json
from uuid import uuid4
from django.http import JsonResponse, HttpResponse
import ast
from .classes.Blockchain import Blockchain
from django.views.decorators.csrf import csrf_exempt



blockchain = Blockchain()
node_address = str(uuid4()).replace('-', '') 
root_node = 'e36f0158f0aed45b3bc755dc52ed4560d'


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
        received_json = json.loads(request.body.decode())
        print(received_json)
        transaction_keys = ['sender', 'reciever', 'amount']
        if not all(key in received_json for key in transaction_keys):
            print('Some elements of the transaction are missing')
            return 
        index = blockchain.add_transaction(received_json['sender'], received_json['reciever'], received_json['amount'])
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
    return JsonResponse(response)


    
    
    
    
    
    
    
