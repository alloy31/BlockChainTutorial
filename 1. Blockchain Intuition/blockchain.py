# Module 1 - Create Blockchain

import datetime  # 블록이 생성되고 채굴된 정확한 날짜의 timestamp 생성
import hashlib  # 블럭 해쉬시 사용
import json  # 블럭 인코딩을 위해 이 라이브러리에서 dumps 함수 사용
from flask import Flask, jsonify  # 블록체인 실제 상태 요청시 사용


# Part 1 - Building a Blockchain
# 클래스로 설계하자

class Blockchain:

    def __init__(self):  # self는 self 앞에 오는 변수가 객체의 변수를 적용하도록 지정하는데 사용됨
        # chain 초기화
        self.chain = []

        # 제네시스 블록 생성
        self.create_block(proof=1, previous_hash='0')  # 인코딩된 문자열만 수용하는 hashlib 라이브러리에서 SHA256함수를 사용하기 때문에 0 사용해야함

        # initiallize done
        # 블록채굴 직후에 사용될 것이기 때문에 proof를 취함

    def create_block(self, proof, previous_hash):  # 객체의 변수를 사용하기 때문에 self를 취한다.
        # 채굴된 새 블록 정의 / 딕셔너리
        # 인덱스, 타임스탬프(채굴시간), proof, previous_hash
        block = {'index': len(self.chain) + 1,
                 'timestamp': str(datetime.datetime.now()),
                 'proof': proof,
                 'previous_hash': previous_hash}
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

# Part 2 = Mining our Blockhain


# Creating a Web App
app = Flask(__name__)

# Creating a Blockchain
blockchain = Blockchain()


# Mining a new Block
@app.route('/mine_block', methods=['GET', 'POST'])
def mine_block():
    previous_block = blockchain.get_previous_block()
    previous_proof = previous_block['proof']
    proof = blockchain.proof_of_work(previous_proof)
    previous_hash = blockchain.hash(previous_block)
    block = blockchain.create_block(proof, previous_hash)

    response = {'message': 'Conratulations, you just mine a block!!',
                'index': block['index'],
                'timestamp': block['timestamp'],
                'proof': block['proof'],
                'previous_hash': block['previous_hash']}

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


# Running the app
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)