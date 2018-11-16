# -*- coding:utf-8 -*-
from myRPC import *
from myRoutingTable import KadTable

from myleger import Leger


class Node(myRPCProtocol):
    def __init__(self, ID=None):

        super(Node, self).__init__()

        if ID is None:
            ID = random_id()

        self.ID = ID
        self.routingTable = KadTable(self.ID)
        self.recallFunctions = self.recordFunctions()

        self.BroadCasts = []
        self.leger = Leger(self.ID)

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
