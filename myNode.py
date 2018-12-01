# -*- coding:utf-8 -*-
from myRPC import *
from myRoutingTable import KadTable

from myleger import Leger
from myBlockChain import *


class Node(myRPCProtocol):
    def __init__(self, ID=None):

        super(Node, self).__init__()

        if ID is None:
            ID = random_id()

        self.ID = ID
        self.routingTable = KadTable(self.ID)
        self.recallFunctions = self.recordFunctions()

        self.BroadCasts = []
        # self.leger = Leger(self.ID)
        self.blockchain = None

    def recordFunctions(self):
        funcs = []
        funcs.extend(myRPCProtocol.__dict__.values())
        funcs.extend(Node.__dict__.values())

        return {
            func.funcName: func.recall_function
            for func in funcs if hasattr(func, 'funcName')
        }

    @convert2RPC
    def ping(self, peer, peerID):
        print(self.ID, "handling ping", peer, peerID)
        return (self.ID, peerID)

    @convert2RPC
    def download_peer_blockchain(self, peer, peerID):
        print(self.ID, "downloading blockchain from", peer, peerID)
        return self.blockchain

    @convert2RPC
    def findNodes(self, peer, peerID):
        self.routingTable.add(peerID, peer)
        return self.routingTable.getKpeers(peerID)

    @asyncio.coroutine
    def updateRoutingTable(self, peer):
        # self.routingTable.add(self.ID,self)
        peers = yield from self.findNodes(peer, self.ID)
        for peerID in peers.keys():
            self.routingTable.add(peerID, peers[peerID])

        self.routingTable.printTable()

    @asyncio.coroutine
    def join(self, peer):

        print(self.ID, "Pinging ", peer)

        try:
            yield from self.ping(peer, self.ID)
        except socket.timeout:
            print("Could not ping %r", peer)
            return

        yield from self.updateRoutingTable(peer)
        yield from self.download_blockchain_all()

        # test create transaction and mine
        peers = self.routingTable.getNeighborhoods()
        print('peers', peers)
        if len(peers) > 0 and len(self.blockchain.chain) == 1:
            for peerID, peer in peers.items():
                tx_id = self.create_transaction(self.blockchain, self.ID, peerID, len(self.blockchain.chain))
            print('current transactin = ', self.blockchain.current_transactions)
            response = self.mine(self.blockchain, self.ID)
            print('after mining, blockchain = ', self.blockchain.chain)

    @asyncio.coroutine
    def download_blockchain_all(self):
        peers = self.routingTable.getNeighborhoods()

        if len(peers) == 0:
            # genesis block
            self.blockchain = BlockChain()
        else:
            for peerID, peer in peers.items():
                reveive_blockchain = yield from self.download_peer_blockchain(peers[peerID], self.ID)

                if self.blockchain == None:
                    self.blockchain = reveive_blockchain
                elif len(reveive_blockchain.chain) > len(self.blockchain.chain):
                    self.blockchain = reveive_blockchain

                # print('blockchain received from', peerID, peer, len(reveive_blockchain.chain))
            print('current blockchain len = ', len(self.blockchain.chain))

    def mine(self, blockchain, node_identifier):
        # We run the proof of work algorithm to get the next proof...
        last_block = blockchain.last_block
        last_proof = last_block['proof']
        # use proof of work
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

    def create_transaction(self, blockchain, sender, recipient, amount):
        # Create a new Transaction
        tx_index = blockchain.new_transaction(sender, recipient, amount)
        return tx_index

    def pingAll(self, peer, peerID):
        peers = self.routingTable.getNeighborhoods()
        for peerID, peer in peers.keys():
            yield from self.ping(peers[peerID], self.ID)

    def postBoardcast(self, messageID, funcName, *args, **kwargs):
        if messageID not in self.BroadCasts:
            self.BroadCasts.append(messageID)

            obj = ('broadcast', messageID, funcName, *args)
            message = pickle.dumps(obj, protocol=0)

            peers = self.routingTable.getNeighborhoods()

            for peer in peers.items():
                self.transport.sendto(message, peer)

    # 收到的所有请求,更新路由表
    # 处理请求
    def handleRequest(self, peer, messageID, funcName, args, kwargs):
        peerID = args[0]
        self.routingTable.add(peerID, peer)
        super(Node, self).handleRequest(peer, messageID, funcName, args, kwargs)

        print("===================")
        self.routingTable.printTable()

    # 处理回复
    def handleReply(self, peer, messageID, response):
        peerID, response = response
        self.routingTable.add(peerID, peer)
        super(Node, self).handleReply(peer, messageID, response)

    # 处理广播
    def handleBroadcast(self, peer, messageID, funcName, args, kwargs):
        peerID = args[0]
        self.routingTable.add(peerID, peer)

        if messageID not in self.BroadCasts:
            self.BroadCasts.append(messageID)
            self.postBoardcast(messageID, funcName, args, kwargs)
            super(Node, self).handleBroadcast(peer, messageID, funcName, args, kwargs)

    # 处理超时
    def handletimeout(self, messageID, args, kwargs):
        peerID = args[0]
        self.routingTable.remove(peerID)
        super(Node, self).handletimeout(messageID, args, kwargs)
