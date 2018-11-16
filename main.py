# -*- coding:utf-8 -*-
import logging

#默认日志目录
LOGDIR = "logs"
#默认日志等级
LOGLEVEL = logging.INFO

#=================================#

import os
import sys
import traceback
from command import *
import time

from mininet.net import Mininet
from mininet.node import ( UserSwitch, OVSSwitch, OVSBridge,
                           IVSSwitch,OVSKernelSwitch )
from mininet.topo import ( SingleSwitchTopo, LinearTopo,
                           SingleSwitchReversedTopo, MinimalTopo )
from mininet.topolib import TreeTopo, TorusTopo
from myTopo import *
from mininet.nodelib import LinuxBridge
from mininet.util import *

IP = "10.0.0.0/8"
PORT = 9000

P2PNet = None

SWITCHES = { 'user': UserSwitch,
             'ovs': OVSSwitch,
             'ovsbr' : OVSBridge,
             'ovsk': OVSSwitch,
             'ivs': IVSSwitch,
             'lxbr': LinuxBridge,
             'default': OVSKernelSwitch }
TOPOS = { 'minimal': MinimalTopo,
          'linear': LinearTopo,
          'reversed': SingleSwitchReversedTopo,
          'single': SingleSwitchTopo,
          'tree': TreeTopo,
          'torus': TorusTopo }


def setupP2PNet(arg1=1, arg2=3, netType="net"):

    if netType == "circle":
        print("circle")
        topo = circleTopo(arg1,arg2)
        # topo = buildTopo(TOPOS, "torus,3,3")
        switch = customClass(SWITCHES,"ovsbr,stp=1")
        P2PNet = Mininet(topo=topo,switch=switch, ipBase=IP,waitConnected=True)
    elif netType == "net":
        print("net")
        topo = netTopo(arg1)
        switch = customClass(SWITCHES, "ovsbr,stp=1")
        P2PNet = Mininet(topo=topo, switch=switch, ipBase=IP, waitConnected=True)
    else:
        if netType == "star":
            print("star")
            topo = starTopo(arg1)
        elif netType == "tree":
            print("tree")
            topo = treeTopo(arg1,arg2)
        elif netType == "netsimple":
            print("netSimple")
            topo = netsimpleTopo(arg1)
        else:
            print("netType error!")
            sys.exit(0)

        P2PNet = Mininet(topo=topo,ipBase=IP)

    P2PNet.start()

    for i, s in enumerate(P2PNet.switches):
        print(i,s.IP)

    for i, host in enumerate(P2PNet.hosts):
        print(i,host.IP)
        if(i>=0):
            print( host.cmd("ping -c1 10.0.0.1"))
        cmd= xtermCMD(host.IP(), PORT, P2PNet.hosts[0].IP(), PORT)
        print(cmd)
        host.cmd(cmd % (i))
        time.sleep(1)



if __name__ == '__main__':

    try:
        setupP2PNet(4,3,netType='star')
        myCammand().cmdloop()
    except SystemExit:
        pass
    except:
        traceback.print_exc()
        traceback.print_stack()

        os.system("killall -SIGKILL xterm")
        os.system("mn --clean > /dev/null 2>&1")

