# Module 1 - Create Cryptocurrency

import datetime  # 블록이 생성되고 채굴된 정확한 날짜의 timestamp 생성
import hashlib  # 블럭 해쉬시 사용
import json  # 블럭 인코딩을 위해 이 라이브러리에서 dumps 함수 사용
from flask import Flask, jsonify, request  # 블록체인 실제 상태 요청시 사용
import requests # 블록체인 내의 모든 노드가 실제로 동일한 체인을 가지고 있는지 확인
from uuid import uuid4
from urllib.parse import urlparse


# Part 1 - Building a Blockchain
# 클래스로 설계하자

class Blockchain:

    def __init__(self):  # self는 self 앞에 오는 변수가 객체의 변수를 적용하도록 지정하는데 사용됨
        # chain 초기화
        self.chain = []
        self.transactions = []  # create_block에서 이 변수를 사용하기 때문에 먼저 선언해줘야함
        # 제네시스 블록 생성
        self.create_block(proof=1, previous_hash='0')  # 인코딩된 문자열만 수용하는 hashlib 라이브러리에서 SHA256함수를 사용하기 때문에 0 사용해야함
        self.nodes = set()  # 순서가 없기 때문에 set자료구조 사용
        # initiallize done
        # 블록채굴 직후에 사용될 것이기 때문에 proof를 취함

    def create_block(self, proof, previous_hash):  # 객체의 변수를 사용하기 때문에 self를 취한다.
        # 채굴된 새 블록 정의 / 딕셔너리
        # 인덱스, 타임스탬프(채굴시간), proof, previous_hash
        block = {'index': len(self.chain) + 1,
                 'timestamp': str(datetime.datetime.now()),
                 'proof': proof,
                 'previous_hash': previous_hash,
                 'transactions': self.transactions}  # 이렇게 모든 transaction을 취함
        self.chain.append(block)
        return block

    def get_previous_block(self):
        return self.chain[-1]

    # 작업증명 = 첫번째 채굴자인지 증명
    # 문제 정의 뿐 아니라 해결
    def proof_of_work(self, previous_proof):
        new_proof = 1
        check_proof = False
        while check_proof is False:
            # SHA256 + hexdigest 함수를 결합하여 64자리 해시 생성
            # four leading 0s 로 시작해야함
            # 연산은 비대칭이어야함
            hash_operation = hashlib.sha256(str(new_proof ** 2 - previous_proof ** 2).encode()).hexdigest()
            if hash_operation[:4] == '0000':
                check_proof = True
            else:
                new_proof += 1

        return new_proof

    def hash(self, block):
        # 블록체인에 블록을 해싱하는 역할
        # 추후 블록 딕셔너리를 json 형식으로 저장 예정
        # 블록 딕셔너리를 키별로 정렬할 수 있도록
        encoded_block = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(encoded_block).hexdigest()

    # 블록체인 유효성 검사
    # 각 블록의 이전 해시가 이전 블록의 해시와 동일한지 여부
    # 작업 증명 함수로 정의한 작업증명 문제에 따라 각 블록의 증명이 유효한지 확인

    def is_chain_valid(self, chain):
        previous_block = chain[0]
        block_index = 1

        while block_index < len(chain):
            block = chain[block_index]
            if block['previous_hash'] != self.hash(previous_block):
                return False

            previous_proof = previous_block['proof']
            proof = block['proof']
            # 선행 0로 시작하는지 확인
            hash_operation = hashlib.sha256(str(proof ** 2 - previous_proof ** 2).encode()).hexdigest()
            if hash_operation[:4] != '0000':
                return False

            previous_block = block
            block_index += 1

        return True

    def add_transaction(self, sender, receiver, amount):  # self는 파이썬에서 클래스의 메소드가 자신이 속한 객체에 접근할 수 있도록 해주는 매개변수
        self.transactions.append({'sender' : sender,
                                  'receiver' : receiver,
                                  'amount' : amount})

        previous_block = self.get_previous_block()

        return previous_block['index'] + 1

    def add_node(self, address):
        parsed_url = urlparse(address)
        self.nodes.add(parsed_url.netloc)

    def replace_chain(self):  # 특정 노드에서 이 함수를 호출
        network = self.nodes
        longest_chain = None
        # 가장 긴 체인을 찾기 위해서 네트워크상의 모든 노드의 체인 길이를 비교
        max_length = len(self.chain)
        for node in network :
            response = requests.get(f'http://{node}/get_chain')  # get_chain 요청의 응답을 얻음
            if response.status_code == 200:
                length = response.json()['length']
                chain = response.json()['chain']
                if length > max_length and self.is_chain_valid(chain):
                    max_length = length
                    longest_chain = chain

        if longest_chain:
            self.chain = longest_chain
            return True

        return False



# Part 2 = Mining our Blockhain


# Creating a Web App
app = Flask(__name__)

# Creating an address for the node on Port 5000
node_address = str(uuid4()).replace('-','')


# Creating a Blockchain
blockchain = Blockchain()


# Mining a new Block
@app.route('/mine_block', methods=['GET', 'POST'])
def mine_block():
    previous_block = blockchain.get_previous_block()
    previous_proof = previous_block['proof']
    proof = blockchain.proof_of_work(previous_proof)
    previous_hash = blockchain.hash(previous_block)
    blockchain.add_transaction(sender= node_address, receiver='Kirill', amount=10)
    block = blockchain.create_block(proof, previous_hash)

    response = {'message': 'Conratulations, you just mine a block!!',
                'index': block['index'],
                'timestamp': block['timestamp'],
                'proof': block['proof'],
                'previous_hash': block['previous_hash'],
                'transactions': block['transactions']}

    return jsonify(response), 200


# Getting the full blockchain
@app.route('/get_chain', methods=['GET'])
def get_chain():
    response = {'chain': blockchain.chain,
                'length': len(blockchain.chain)}

    return jsonify(response), 200


@app.route('/is_valid', methods=['GET'])
def is_valid():
    is_valid = blockchain.is_chain_valid(blockchain.chain)
    if is_valid:
        response = {'message': 'All good. The Blockchain is valid!'}
    else:
        response = {'message': 'We have a problem!!'}

    return jsonify(response), 200


# Adding a new transaction to the Blockchain
@app.route('/add_transaction', methods=['POST'])
def add_transaction():
    json = request.get_json()
    transaction_keys = ['sender', 'receiver', 'amount']
    if not all (key in json for key in transaction_keys):
        return 'Some elements of the transaction are missing', 400

    index = blockchain.add_transaction(json['sender'], json['receiver'], json['amount'])
    response = {'message': f'This transaction will be added to Block {index}'}
    return jsonify(response), 201


# Part 3 - Decentrallizing our Blockchain

# Connecting new nodes
@app.route('/connect_node', methods = ['POST'])
def connect_node():
    json = request.get_json(force=True, silent=True, cache=False)
    # 네트워크에 있는 모든 노드와 새로운 노드를 연결
    nodes = json.get('nodes')
    if nodes is None :
        return 'No nodes provided', 400

    for node in nodes:
        blockchain.add_node(node)
    response = {'message': 'All the nodes now connected. The hadcoin Blockchain now contains the following nodes',
                'total_nodes': list(blockchain.nodes)}
    return jsonify(response), 201

# Replacing the chain by the longest chain if needed
@app.route('/replace_chain', methods=['GET'])
def replace_chain():
    is_chain_replaced = blockchain.replace_chain()  # chain을 교체해줌

    if is_chain_replaced:
        response = {'message': 'The node had different chains so the chain was replaced by the longest chain',
                    'new_chain': blockchain.chain}
    else:
        response = {'message': 'All good. The chain is the largest one',
                    'actual_chain': blockchain.chain}

    return jsonify(response), 200


# Running the app
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002)