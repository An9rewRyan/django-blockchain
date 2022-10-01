from threading import Thread
from django.views.decorators.csrf import csrf_exempt
from .classes.Blockchain import Blockchain
from .classes.Block import Block
import ast
from django.http import JsonResponse, HttpResponse
from uuid import uuid4
import json
import sys
sys.path.append('./classes')

blockchain = Blockchain()
blockchain.nodes = ("127.0.0.1:8001",
                    "127.0.0.1:8002",
                    "127.0.0.1:8003")
node_address = str(uuid4()).replace('-', '')
root_node = 'e36f0158f0aed45b3bc755dc52ed4560d'
# £adasda==asdasdadsadsaasdasd
daemon = Thread(
    target=blockchain.spawn_block,
    args=(),
    daemon=True,
    name='Background block spawner')  # daemon for spawning blocks on background
daemon.start()


def mine_block(request):
    if request.method == 'GET':
        last_block = blockchain.get_last_block()
        nonce = 1
        coinbase = 0
        print(int(last_block.hash_block(nonce), 16))
        while int(last_block.hash_block(nonce), 16) >= blockchain.difficulty:
            print(int(last_block.hash_block(nonce), 16), blockchain.difficulty, int(
                last_block.hash_block(nonce), 16) - blockchain.difficulty, nonce, coinbase)
            nonce += 1
            if nonce == 2**32:
                nonce = 1
                coinbase += 1
                last_block.headers["merkel_root"] += str(coinbase)

        last_block.headers["nonce"] = nonce

        chain = blockchain.set_block_nonce(last_block)
        blockchain.chain = chain
        print("\n\n\n\n", blockchain.chain)
        blockchain.send_chain_to_nodes()

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
                "length": len(blockchain.chain),
                "nodes": blockchain.nodes}

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
def add_transaction(request):  # New
    if request.method == 'POST':
        received_json = json.loads(request.body.decode())
        print(received_json)
        transaction_keys = ['sender', 'reciever', 'amount']
        if not all(key in received_json for key in transaction_keys):
            print('Some elements of the transaction are missing')
            return
        index = blockchain.add_transaction(
            received_json['sender'],
            received_json['reciever'],
            received_json['amount'])
        response = {
            'message': f'This transaction will be added to Block {index}'}
    return JsonResponse(response)

# Connecting new nodes


@csrf_exempt
def connect_node(request):  # New
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

# Replacing the chain by the longest chain if needed asdasd s s

@csrf_exempt
def replace_chain(request):
    if request.method == "POST":
        received_json = json.loads(request.body)
        new_dict_chain = received_json.get('chain')
        response = {'message': 'Blabalbla'}

        new_chain = blockchain.dict_chain_to_block_chain(new_dict_chain)

        if not(blockchain.is_chain_valid(blockchain.chain)) and len(new_chain) >= len(blockchain.chain):
            is_valid = blockchain.is_chain_valid(new_chain)
            if is_valid:
                blockchain.chain = []
                for block in new_dict_chain:
                    new_block = Block(
                        previous_hash=block["headers"]["previous_hash"],
                        difficulty=blockchain.difficulty,
                        version=blockchain.version,
                        nonce=block["headers"]["nonce"],
                        time=block["headers"]["time"]
                    )
                    blockchain.chain.append(new_block)
                response = {'message': 'Blockchain is valid. Current chain updated'}
            else:
                response = {'message': 'Blockchain is not valid. Current chain stay the same'}

        return JsonResponse(response)
