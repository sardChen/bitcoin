# -*- coding: utf-8 -*-

import hashlib
import json
from time import time
from utils import *


class BlockChain(object):
    def __init__(self,ID):
        self.chain = []
        self.current_transactions = []
        self.nodes = set()
        self.set_node_id(ID)

        # Create the genesis block
        self.new_block(previous_hash=1, proof=100)

    def set_node_id(self, node_id):
        self.node_id = node_id

    def register_node(self, address):
        """
        Add a new node to the list of nodes
        :param address: <str> Address of node. Eg. 'http://192.168.0.5:5000'
        :return: None
        """

        # parsed_url = urlparse(address)
        self.nodes.add(address)

    def new_block(self, proof, previous_hash=None):
        """
        生成新块
        :param proof: <int> The proof given by the Proof of Work algorithm
        :param previous_hash: (Optional) <str> Hash of previous Block
        :return: <dict> New Block
        """

        if len(self.chain) == 0:
            id = str(random_id())

            self.current_transactions.append({
                'id': id,
                'sender': "0",
                'recipient': self.node_id,
                'amount': 999,
            })

        block = {
            'index': len(self.chain) + 1,
            'timestamp': time(),
            'transactions': self.current_transactions,
            'proof': proof,
            'previous_hash': previous_hash or self.hash(self.chain[-1]),
            'minerID': self.node_id,
            'minerAmount': self.current_transactions[-1]['amount'],
        }

        # Reset the current list of transactions

        self.current_transactions = []

        self.chain.append(block)
        return block

    def new_transaction(self, sender, recipient, amount):
        """
        生成新交易信息，信息将加入到下一个待挖的区块中
        :param sender: <str> Address of the Sender
        :param recipient: <str> Address of the Recipient
        :param amount: <int> Amount
        :return: <int> The index of the Block that will hold this transaction
        """

        id = str(random_id())

        self.current_transactions.append({
            'id' : id,
            'sender': sender,
            'recipient': recipient,
            'amount': amount,
        })

        return self.last_block['index'] + 1

    @staticmethod
    def hash(block):
        # Hashes a Block
        """
        生成块的 SHA-256 hash值
        :param block: <dict> Block
        :return: <str>
        """

        # We must make sure that the Dictionary is Ordered, or we'll have inconsistent hashes
        block_string = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()

    @property
    def last_block(self):
        # Returns the last Block in the chain
        return self.chain[-1]

    def proof_of_work(self, last_proof):
        """
        简单的工作量证明:
         - 查找一个 p' 使得 hash(pp') 以4个0开头
         - p 是上一个块的证明,  p' 是当前的证明
        :param last_proof: <int>
        :return: <int>
        """

        proof = 0
        while self.valid_proof(last_proof, proof) is False:
            proof += 1

        return proof

    @staticmethod
    def valid_proof(last_proof, proof):
        """
        验证证明: 是否hash(last_proof, proof)以4个0开头?
        :param last_proof: <int> Previous Proof
        :param proof: <int> Current Proof
        :return: <bool> True if correct, False if not.
        """

        guess_str = '%s%s' % (last_proof, proof)
        guess = guess_str.encode()

        # guess = f'{last_proof}{proof}'.encode()

        guess_hash = hashlib.sha256(guess).hexdigest()
        return guess_hash[:2] == "00"

    def valid_chain(self, chain):
        """
        Determine if a given blockchain is valid
        :param chain: <list> A blockchain
        :return: <bool> True if valid, False if not
        """

        last_block = chain[0]
        current_index = 1

        while current_index < len(chain):
            block = chain[current_index]
            print(last_block)
            print(block)
            print("\n-----------\n")
            # Check that the hash of the block is correct
            if block['previous_hash'] != self.hash(last_block):
                return False

            # Check that the Proof of Work is correct
            if not self.valid_proof(last_block['proof'], block['proof']):
                return False

            last_block = block
            current_index += 1

        return True

    def get_chain_from_neighbours(self):
        # TODO get chain from others
        pass


    def resolve_conflicts(self):
        """
        共识算法解决冲突
        使用网络中最长的链.
        :return: <bool> True 如果链被取代, 否则为False
        """

        neighbours = self.nodes
        new_chain = None

        # We're only looking for chains longer than ours
        max_length = len(self.chain)

        # Grab and verify the chains from all the nodes in our network
        for node in neighbours:
            # response = requests.get(f'http://{node}/chain')
            response = self.get_chain_from_neighbours()

            if response.status_code == 200:
                length = response.json()['length']
                chain = response.json()['chain']

                # Check if the length is longer and the chain is valid
                if length > max_length and self.valid_chain(chain):
                    max_length = length
                    new_chain = chain

        # Replace our chain if we discovered a new, valid chain longer than ours
        if new_chain:
            self.chain = new_chain
            return True

        return False


    def removeSomeTX(self,IDlist):
        print("before remove: ",len(self.current_transactions))
        tmp_TXs = []
        for tx in self.current_transactions:
            if tx['id'] not in IDlist:
                tmp_TXs.append(tx)
        self.current_transactions = tmp_TXs
        print("after remove: ", len(self.current_transactions))



def new_transaction(blockchain, sender, recipient, amount):
    # Create a new Transaction
    index = blockchain.new_transaction(sender, recipient, amount)

    return index


def mine(blockchain, node_identifier):
    # We run the proof of work algorithm to get the next proof...
    last_block = blockchain.last_block
    last_proof = last_block['proof']
    proof = blockchain.proof_of_work(last_proof)

    # 给工作量证明的节点提供奖励.
    # 发送者为 "0" 表明是新挖出的币
    blockchain.new_transaction(
        sender="0",
        recipient=node_identifier,
        amount=1,
    )

    # Forge the new Block by adding it to the chain
    block = blockchain.new_block(proof)

    response = {
        'message': "New Block Forged",
        'index': block['index'],
        'transactions': block['transactions'],
        'proof': block['proof'],
        'previous_hash': block['previous_hash'],
    }
    return response


def full_chain(blockchain):
    response = {
        'chain': blockchain.chain,
        'length': len(blockchain.chain),
    }
    return response


if __name__ == '__main__':
    # Instantiate the Blockchain
    blockchain = BlockChain()

    mine_msg = mine(blockchain, '192.168.0.1')
    print('mine_msg', mine_msg)

    tx_msg = new_transaction(blockchain, '192.168.0.1', '192.168.0.121', 5)
    print('tx_msg', tx_msg)

    mine_msg = mine(blockchain, '192.168.0.2')
    print('mine_msg', mine_msg)

    full_msg = full_chain(blockchain)
    print('full_msg', full_msg)

    '''
    {
  'chain': [
    {
      'index': 1,
      'proof': 100,
      'transactions': [],
      'timestamp': 1543413451.6612592,
      'previous_hash': 1
    },
    {
      'index': 2,
      'proof': 226,
      'transactions': [
        {
          'sender': '0',
          'recipient': '192.168.0.1',
          'amount': 1
        }
      ],
      'timestamp': 1543413451.6612592,
      'previous_hash': '938862bd1bfb9941153d7dd19412281f0ffc1423a1cd382b1078f78fc0491dc7'
    },
    {
      'index': 3,
      'proof': 346,
      'transactions': [
        {
          'sender': '192.168.0.1',
          'recipient': '192.168.0.121',
          'amount': 5
        },
        {
          'sender': '0',
          'recipient': '192.168.0.2',
          'amount': 1
        }
      ],
      'timestamp': 1543413451.662258,
      'previous_hash': 'c3517dcb7efbd6cfabe017980bfc3e4635b5e35301848f20b9bdb5cc932a3169'
    }
  ],
  'length': 3
    }
    '''