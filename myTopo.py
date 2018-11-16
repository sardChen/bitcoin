# -*- coding:utf-8 -*-

from mininet.topo import Topo
from mininet.util import irange


class starTopo(Topo):
    # 1个switch上连接n个hosts
    def build(self, n=2, **_opts):
        self.n = n

        genHostName = lambda i, j: 'h%ss%d' % (j, i)

        switch = self.addSwitch('s%s' % 1)
        for j in irange(1, n):
            host = self.addHost(genHostName(1, j))
            self.addLink(host, switch)


class circleTopo(Topo):
    def build(self, x, y, n=1):
        """x: dimension of torus in x-direction
           y: dimension of torus in y-direction
           n: number of hosts per switch"""
        if x < 3 or y < 3:
            raise Exception('Please use 3x3 or greater for compatibility '
                            'with 2.1')
        if n == 1:
            genHostName = lambda loc, k: 'h%s' % (loc)
        else:
            genHostName = lambda loc, k: 'h%sx%d' % (loc, k)

        hosts, switches, dpid = {}, {}, 0
        # Create and wire interior
        for i in range(0, x):
            for j in range(0, y):
                loc = '%dx%d' % (i + 1, j + 1)
                # dpid cannot be zero for OVS
                dpid = (i + 1) * 256 + (j + 1)
                switch = switches[i, j] = self.addSwitch(
                    's' + loc, dpid='%x' % dpid)
                for k in range(0, n):
                    host = hosts[i, j, k] = self.addHost(
                        genHostName(loc, k + 1))
                    self.addLink(host, switch)
        # Connect switches
        for i in range(0, x):
            for j in range(0, y):
                sw1 = switches[i, j]
                sw2 = switches[i, (j + 1) % y]
                sw3 = switches[(i + 1) % x, j]
                self.addLink(sw1, sw2)
                self.addLink(sw1, sw3)

    # class circleTopo(Topo):
    #     #简化环形结构(本质为任意host只与前后两个host相连接)
    #     def build( self, n ):
    #         self.n = n
    #
    #         genHostName = lambda i, j: 'h%ss%d' % (j, i)
    #
    #         nodes = []
    #         for i in irange( 1, n ):
    #             node = self.addNewNode('s%s' % i, genHostName( i, i ) )
    #             nodes.append(node)
    #
    #         num = n+1
    #         print(type(nodes))
    #         nlen = len(nodes)
    #         for i in irange(0,nlen-1):
    #             switch = self.addSwitch('s%s' % num)
    #             num+=1
    #             self.addLink(switch,nodes[i])
    #             self.addLink(switch,nodes[i-1])

    def addNewNode(self, str1, str2):
        node = self.addSwitch(str1)
        host = self.addHost(str2)
        self.addLink(node, host)
        return node


class treeTopo(Topo):
    # 一个节点连fanout个子节点,树的深度为depth
    def build(self, depth=1, fanout=2):
        self.hostNum = 1
        self.switchNum = 1
        self.addTree(depth, fanout)

    def addTree(self, depth, fanout):
        isSwitch = depth > 0
        if isSwitch:
            node = self.addSwitch('s%s' % self.switchNum)
            self.switchNum += 1
            for _ in range(fanout):
                child = self.addTree(depth - 1, fanout)
                self.addLink(node, child)
        else:
            node = self.addHost('h%s' % self.hostNum)
            self.hostNum += 1
        return node


class netTopo(Topo):
    # 任意两个host之间连接
    def build(self, n=2, **_opts):
        self.n = n
        genHostName = lambda i, j: 'h%ss%d' % (j, i)

        nodes = []
        num = 0

        for i in irange(1, n):
            node = self.addNewNode('s%s' % i, genHostName(i, i))
            for n in nodes:
                self.addLink(n, node)
            nodes.append(node)

    def addNewNode(self, str1, str2):
        node = self.addSwitch(str1)
        host = self.addHost(str2)
        self.addLink(node, host)
        return node


class netsimpleTopo(Topo):
    # 简化全连接(本质任意两个host之间连接)
    def build(self, n=2, **_opts):
        self.n = n
        genHostName = lambda i, j: 'h%ss%d' % (j, i)

        switch0 = self.addSwitch('s0')
        hosts = []
        for i in irange(1, n):
            host = self.addHost(genHostName(i, i))
            hosts.append(host)

        for i in irange(1, n):
            switch = self.addSwitch('s%s' % i)
            self.addLink(switch, hosts[i - 1])
            self.addLink(switch, hosts[i - 2])
            self.addLink(switch, switch0)
