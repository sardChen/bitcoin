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
        self.stop = False;
        # self.logger = None

    def set_node_id(self, node_id):
        self.node_id = node_id

    # def set_logger(self, logger):
    #     self.logger = logger

    def create_genesis_block(self):
        # Create the genesis block
        self.new_block(previous_hash=1, proof=100)


    def new_block(self, proof, previous_hash=None):
        """
        生成新块
        :param proof: <int> The proof given by the Proof of Work algorithm
        :param previous_hash: (Optional) <str> Hash of previous Block
        :return: <dict> New Block
        """

        if len(self.chain) == 0:
            id = random_id()

            self.current_transactions.append({
                'id': id,
                'sender': 0,
                'recipient': self.node_id,
                'amount': 999,
            })

        valid_transactions, invalid_transactions = self.check_transactions()

        # self.logger.info('valid_transactions')
        # self.logger.info(valid_transactions)
        # self.logger.info('invalid_transactions')
        # self.logger.info(invalid_transactions)

        block = {
            'index': len(self.chain) + 1,
            'timestamp': time(),
            'transactions': valid_transactions,
            'proof': proof,
            'previous_hash': previous_hash or self.hash(self.chain[-1]),
            'minerID': self.node_id,
            'minerAmount': self.current_transactions[-1]['amount'],
        }

        # Reset the current list of transactions

        self.current_transactions = [tx for tx in invalid_transactions]

        self.chain.append(block)
        return block

    def new_transaction(self, sender, recipient, amount):
        """
        生成新交易信息，信息将加入到下一个待挖的区块中
        :param sender: ID of the Sender
        :param recipient: ID of the Recipient
        :param amount: <int> Amount
        :return: <int> The index of the Block that will hold this transaction
        """

        id = random_id()

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
        # self.logger.info('in check_chain')

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


    def get_all_tx(self):
        txs=[]
        for block in self.chain:
            for tx in block['transactions']:
                txs.append(tx)

        return txs

    def check_transactions(self):
        # self.logger.info('in check_transactions')
        valid_transactions = []
        invalid_transactions = []

        current_index = 0
        UTXO = defaultdict(int)

        while current_index < len(self.chain):
            block = self.chain[current_index]

            for tx in block['transactions']:
                UTXO[tx['sender']] -= int(tx['amount'])
                UTXO[tx['recipient']] += int(tx['amount'])

            current_index += 1

        for id in UTXO:
            print(id,UTXO[id])

        for tx in self.current_transactions:
            print('sender = ',tx['sender'])
            print('amount = ',tx['amount'])
            if UTXO[tx['sender']] - int(tx['amount']) < 0 and tx['sender'] != 0:
                invalid_transactions.append(tx)
            else:
                UTXO[tx['sender']] -= int(tx['amount'])
                UTXO[tx['recipient']] += int(tx['amount'])
                valid_transactions.append(tx)

        print('valid transactions = ')
        print(valid_transactions)
        print('invalid transactions = ')
        print(invalid_transactions)

        return valid_transactions, invalid_transactions

