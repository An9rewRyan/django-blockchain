import sys
sys.path.append('./classes')
import json
from uuid import uuid4
from django.http import JsonResponse, HttpResponse
import ast
from .classes.Blockchain import Blockchain
from django.views.decorators.csrf import csrf_exempt
from threading import Thread

blockchain = Blockchain()
node_address = str(uuid4()).replace('-', '') 
root_node = 'e36f0158f0aed45b3bc755dc52ed4560d'

daemon = Thread(target = blockchain.spawn_block, args=(), daemon=True, name='Background block spawner') #daemon for spawning blocks on background
daemon.start()

def mine_block(request):
    if request.method == 'GET':
        last_block = blockchain.get_last_block()
        nonce = 1
        coinbase = 0
        print(int(last_block.hash_block(nonce), 16))
        while int(last_block.hash_block(nonce), 16) >= blockchain.difficulty:   
            print(int(last_block.hash_block(nonce), 16), blockchain.difficulty, int(last_block.hash_block(nonce), 16)- blockchain.difficulty, nonce, coinbase )      
            nonce +=1
            if nonce == 2**32:
                nonce = 1
                coinbase +=1
                last_block.headers["merkel_root"]+=str(coinbase)

        last_block.headers["nonce"] = nonce

        blockchain.set_block_nonce(last_block)

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


    
    
    
    
    
    
    
