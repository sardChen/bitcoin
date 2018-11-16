# -*- coding:utf-8 -*-
import asyncio
import sys
import signal

from myNode import Node

def setupNode(local_addr, peer_addr):

    loop = asyncio.get_event_loop()

    loop.add_signal_handler(signal.SIGINT, loop.stop)

    #将节点node与IP,port 绑定在一起
    f = loop.create_datagram_endpoint(Node, local_addr=local_addr)
    _, node = loop.run_until_complete(f)

    print("MyId: ", node.ID)

    loop.run_until_complete(node.join(peer_addr))

    loop.run_forever()



if __name__ == '__main__':
    setupNode(
        local_addr=(sys.argv[1], int(sys.argv[2])),
        peer_addr=(sys.argv[3], int(sys.argv[4]))
    )