# -*- coding: utf-8 -*-
import asyncio
import hashlib
import json
from time import time
from utils import *
from collections import defaultdict


class BlockChain(object):
    def __init__(self,ID):
        self.chain = []
        self.current_transactions = []
        self.nodes = set()
        self.set_node_id(ID)

        # Create the genesis block
        self.new_block(previous_hash=1, proof=100)
        self.stop = False;

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

    @asyncio.coroutine
    def proof_of_work(self, last_proof):
        """
        简单的工作量证明:
         - 查找一个 p' 使得 hash(pp') 以6个0开头
         - p 是上一个块的证明,  p' 是当前的证明
        :param last_proof: <int>
        :return: <int>
        """

        proof = 0
        count=0
        while self.valid_proof(last_proof, proof) is False:
            tmp = random.randint(1,3)
            # print(proof)
            proof += tmp
            count+=1
            if count==5:
                yield from asyncio.sleep(1)
                count=0
            if self.stop == True:
                break;

        return proof

    @staticmethod
    def valid_proof(last_proof, proof):
        """
        验证证明: 是否hash(last_proof, proof)以6个0开头?
        :param last_proof: <int> Previous Proof
        :param proof: <int> Current Proof
        :return: <bool> True if correct, False if not.
        """

        guess_str = '%s%s' % (last_proof, proof)
        guess = guess_str.encode()

        # guess = f'{last_proof}{proof}'.encode()

        guess_hash = hashlib.sha256(guess).hexdigest()
        return guess_hash[:2] == "00"

    # check if chain has fork
    def check_chain(self, chain):
        """
                    Determine if a given blockchain is valid
                    :param chain: <list> A blockchain
                    :return: <bool> True if valid, False if not
                    """

        last_block = chain[0]
        current_index = 1
        UTXO = defaultdict(int)
        tx_id_set = set()

        for tx in last_block['transactions']:
            UTXO[tx['sender']] -= int(tx['amount'])
            UTXO[tx['recipient']] += int(tx['amount'])

            if tx['id'] not in tx_id_set:
                tx_id_set.add(tx['id'])
            else:
                return False

        while current_index < len(chain):
            block = chain[current_index]
            # print(last_block)
            # print(block)
            # print("\n-----------\n")
            # Check that the hash of the block is correct
            # check fork
            if block['previous_hash'] != self.hash(last_block):
                return False

            # Check that the Proof of Work is correct
            if not self.valid_proof(last_block['proof'], block['proof']):
                return False

            for tx in block['transactions']:
                UTXO[tx['sender']] -= int(tx['amount'])
                UTXO[tx['recipient']] += int(tx['amount'])

                if tx['id'] not in tx_id_set:
                    tx_id_set.add(tx['id'])
                else:
                    return False

            last_block = block
            current_index += 1

        for id in UTXO:
            if id == '0':
                continue
            elif UTXO[id] < 0:
                return False

        return True



    def removeSomeTX(self,IDlist):
        print("before remove: ",len(self.current_transactions))
        tmp_TXs = []
        for tx in self.current_transactions:
            if tx['id'] not in IDlist:
                tmp_TXs.append(tx)
        self.current_transactions = tmp_TXs
        print("after remove: ", len(self.current_transactions))


    def getAllTX(self):
        txIds=[]
        for block in self.chain:
            for tx in block['transactions']:
                txIds.append(tx['id'])
        return txIds


