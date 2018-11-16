# -*- coding:utf-8 -*-
import asyncio
import pickle
import socket

from functools import wraps
from utils import *


# 基于异步IO asyncio 封装的一层简易协议,支持:
# 1.发送消息,分为两类: 1.1 发送请求 1.2 发送回复 1.3发送广播,具体实现在子类
# 2处理消息,分为四类: 2.1 处理广播消息 2.2 处理普通请求 2.3 处理回复消息 2.4 处理超时消息
class myRPCProtocol(asyncio.DatagramProtocol):

    def __init__(self, timeout=10):
        self.timeout = timeout
        self.requests = {}

        super(myRPCProtocol, self).__init__()

    # 实现父类方法-建立连接后回调
    def connection_made(self, transport):
        print("connetcion setup:", transport)

        self.transport = transport
        self.socket_addr = self.transport.get_extra_info('sockname')

    # 实现父类方法-断开连接后回调
    def connection_lost(self, exc):
        print("connnetction lost!")

    # 发送广播
    def postBoardcast(self, funcName, *args, **kwargs):
        """
        print("boardcast none!")
        """

    # 发送请求
    def postRequest(self, peer, funcName, *args, **kwargs):
        messageID = random_id()
        #        print(format("sending request to %r: %r(*%r, **%r) as message %r",
        #                    peer, funcName, args, kwargs, messageID))

        reply = asyncio.Future()
        self.requests[messageID] = reply

        loop = asyncio.get_event_loop()
        loop.call_later(self.timeout, self.handletimeout, messageID, args, kwargs)

        obj = ('request', messageID, funcName, args, kwargs)
        message = pickle.dumps(obj, protocol=0)
        self.transport.sendto(message, peer)

        return reply

    # 发送回复
    def postReply(self, peer, messageID, response):
        #        print(format("sending reply to %r: (%r, %r)", peer, messageID, response))

        obj = ('reply', messageID, self.ID, response)
        message = pickle.dumps(obj, protocol=0)

        self.transport.sendto(message, peer)

    # 实现父类方法-收到数据后调用
    def datagram_received(self, data, peer):
        print("recevive message from ", peer, ":", data)
        msgType, messageID, *details = pickle.loads(data)

        if msgType == 'broadcast':
            funcName, args, kwargs = details
            self.handleBroadcast(peer, messageID, funcName, args, kwargs)
        elif msgType == 'request':
            funcName, args, kwargs = details
            self.handleRequest(peer, messageID, funcName, args, kwargs)
        elif msgType == 'reply':
            response = details
            self.handleReply(peer, messageID, response)

    # 处理请求
    def handleRequest(self, peer, messageID, funcName, args, kwargs):
        #        print(format('handled request from %r: %r(*%r, **%r) as message %r',
        #                    peer, funcName, args, kwargs, messageID))

        recall = self.recallFunctions[funcName]
        response = recall(self, peer, *args, **kwargs)
        self.postReply(peer, messageID, response)

    # 处理回复
    def handleReply(self, peer, messageID, response):
        #        print(format('received reply to message %r, response %r', messageID, response))

        if messageID in self.requests:
            reply = self.requests.pop(messageID)
            reply.set_result(response)

    # 处理广播
    def handleBroadcast(self, peer, messageID, funcName, args, kwargs):
        print("handled broadcast from", peer, funcName, args, " as message ", messageID)
        recall = self.recallFunctions[funcName]
        recall(self, peer, *args, **kwargs)

    # 处理超时
    def handletimeout(self, messageID, args, kwargs):
        # print("timeout :", messageID)
        if messageID in self.requests:
            reply = self.requests.pop(messageID)
            reply.set_exception(socket.timeout)

    # 实现父类方法-发现错误后调用
    def error_received(self, exc):
        print("error received: ", exc)


# 将所有的函数调用变成RPC调用
def convert2RPC(func):
    @asyncio.coroutine
    @wraps(func)
    def convert(*args, **kwargs):
        instance, peer, *args = args
        response = yield from instance.postRequest(peer, convert.funcName, *args, **kwargs)
        return response

    convert.funcName = func.__name__
    convert.recall_function = func

    return convert
