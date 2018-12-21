
import asyncio
import sys
import signal

from myAttackNode import AttackNode
from myNode import Node

def setupNode(local_addr, peer_addr, mode):

    loop = asyncio.get_event_loop()

    loop.add_signal_handler(signal.SIGINT, loop.stop)

    #将节点node与IP,port 绑定在一起
    f = loop.create_datagram_endpoint(Node, local_addr=local_addr)
    _, node = loop.run_until_complete(f)


    node.setLocalAddr(local_addr)

    # print("MyId: ", node.ID)

    if mode == "double":
        loop.run_until_complete(node.join(peer_addr,getMoney=False))
        loop.create_task(node.startPOW())
    else:
        loop.run_until_complete(node.join(peer_addr, getMoney=True))

    if mode == "pow":
        loop.create_task(node.startPOW())
    elif mode == "pos":
        loop.create_task(node.startPOS())

    loop.create_task(node.nodeCommand())

    loop.create_task(node.fileCommand())

    loop.run_forever()


def setupBGPNode(local_addr, peer_addr, mode):

    loop = asyncio.get_event_loop()

    loop.add_signal_handler(signal.SIGINT, loop.stop)

    #将节点node与IP,port 绑定在一起
    f = loop.create_datagram_endpoint(Node, local_addr=local_addr)
    _, node = loop.run_until_complete(f)


    node.setLocalAddr(local_addr)


    loop.run_until_complete(node.BGPjoin())

    #
    # if mode == "pow":
    #     loop.create_task(node.startPOW())
    # elif mode == "pos":
    #     loop.create_task(node.startPOS())

    loop.create_task(node.nodeCommand())

    loop.create_task(node.fileCommand())

    loop.run_forever()


def setupDoubleAttackNode(local_addr, peer_addr, attack_num):

    loop = asyncio.get_event_loop()

    loop.add_signal_handler(signal.SIGINT, loop.stop)

    #将节点node与IP,port 绑定在一起
    f = loop.create_datagram_endpoint(AttackNode, local_addr=local_addr)
    _, node = loop.run_until_complete(f)


    node.setLocalAddr(local_addr)
    node.sethackers(attack_num)


    loop.run_until_complete(node.join(peer_addr))


    loop.create_task(node.startPOW())


    loop.create_task(node.nodeCommand())

    loop.create_task(node.fileCommand())

    loop.run_forever()



if __name__ == '__main__':
    if sys.argv[6] == "BGP" :
        setupBGPNode(
            local_addr=(sys.argv[1], int(sys.argv[2])),
            peer_addr=(sys.argv[3], int(sys.argv[4])),
            mode=(sys.argv[5])
        )
    elif sys.argv[6] == "double" :
        setupDoubleAttackNode(
            local_addr=(sys.argv[1], int(sys.argv[2])),
            peer_addr=(sys.argv[3], int(sys.argv[4])),
            attack_num=int(sys.argv[5])
        )
    else:
        setupNode(
            local_addr=(sys.argv[1], int(sys.argv[2])),
            peer_addr=(sys.argv[3], int(sys.argv[4])),
            mode  = (sys.argv[5])
        )