import logging
import os.path
#默认日志目录
from utils import cur_path

LOGDIR = "logs"
#默认日志等级
LOGLEVEL = logging.INFO

#=================================#

import os
import sys

#sys.path.append('/home/findns/Projects/mininet')

import traceback
from cmd import Cmd
from command import xtermCMD
import time

from mininet.net import Mininet
from mininet.link import Link
from mininet.cli import CLI
from mininet.node import ( UserSwitch, OVSSwitch, OVSBridge,
                           IVSSwitch,OVSKernelSwitch )
from mininet.topo import ( SingleSwitchTopo, LinearTopo,
                           SingleSwitchReversedTopo, MinimalTopo )
from mininet.topolib import TreeTopo, TorusTopo
from myTopo import *
from mininet.nodelib import LinuxBridge
from mininet.util import *
import shutil

from mininet.link import TCLink

IP = "10.0.0.0/8"
PORT = 9000

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


P2PNet=None
MODE = "pow"

def setMode(mode):
    global MODE;
    MODE = mode;

def setupP2PNet(arg1=1, arg2=3, netType="net"):

    global P2PNet;

    if netType == "circle":
        print("circle");
        topo = circleTopo(arg1,arg2)
        # topo = buildTopo(TOPOS, "torus,3,3")
        switch = customClass(SWITCHES,"ovsbr,stp=1")
        P2PNet = Mininet(topo=topo,switch=switch, ipBase=IP,waitConnected=True);
    elif netType == "net":
        print("net");
        topo = netTopo(arg1)
        switch = customClass(SWITCHES, "ovsbr,stp=1")
        P2PNet = Mininet(topo=topo, switch=switch, ipBase=IP, waitConnected=True);
    else:
        if netType == "star":
            print("star");
            topo = starTopo(arg1)
        elif netType == "tree":
            print("tree");
            topo = treeTopo(arg1,arg2)
        elif netType == "netsimple":
            print("netSimple");
            topo = netsimpleTopo(arg1)
        else:
            print("netType error!");
            sys.exit(0);

        P2PNet = Mininet(topo=topo,link=TCLink,ipBase=IP);

    P2PNet.start();
    #限制带宽
    P2PNet.iperf()

    for i, s in enumerate(P2PNet.switches):
        print(i,s.IP)

    for i, host in enumerate(P2PNet.hosts):
        print(i,host.IP)
        if(i>=0):
            print( host.cmd("ping -c1 10.0.0.1"))
        cmd= xtermCMD(host.IP(), PORT, P2PNet.hosts[0].IP(), PORT, MODE)
        print(cmd)
        host.cmd(cmd % (i))
        time.sleep(1)

    path = os.path.join(cur_path, 'CMD')
    with open(os.path.join(path,"main"), 'w') as f:
        f.close()

def recordNodesInfo():
    path = os.path.join(cur_path, 'Logs')
    with open(os.path.join(path, "main"), 'w') as f:
        for _, host in enumerate(P2PNet.hosts):
            f.write(str(host.IP()) +" "+ host.name+"\n")

def readCommnadFromFile():
    path = os.path.join(cur_path, 'CMD')
    with open(os.path.join(path, "main"), 'r') as f:
        lines = f.readlines();
        if len(lines) > 0:
            return lines[0].strip();
        else:
            return None;

def clearFileCMD():
    path = os.path.join(cur_path,'CMD')
    with open(os.path.join(path, "main"), 'w') as f:
        f.close()

def fileCommand():
    while True:
        line = readCommnadFromFile()
        if line != None:
            line = line.strip()
            if len(line) > 0:
                line = line.split();
                cmd = line[0];
                args = line[1:];

                if cmd in ["delNode"]:
                    hostName = args[0].strip()
                    node = None;
                    for host in P2PNet.hosts:
                        if host.name == hostName:
                            node = host;
                            break;
                    P2PNet.delNode(node);
                    recordNodesInfo()

                elif cmd in ["addNode"]:
                    id = len(P2PNet.hosts)

                    newHost = P2PNet.addHost("h%ds%d" % (id, id))

                    switch = P2PNet.switches[0];

                    P2PNet.addLink(switch, newHost);

                    slink = Link(switch, newHost)
                    switch.attach(slink);
                    switch.start(P2PNet.controllers);

                    newHost.configDefault(defaultRoute=newHost.defaultIntf())

                    print(P2PNet.hosts[0].cmd("ping -c1 %s" % newHost.IP()))  # important!!!

                    print(newHost.cmd("ping -c1 10.0.0.1"))

                    cmd = xtermCMD(newHost.IP(), PORT, P2PNet.hosts[0].IP(), PORT, MODE)

                    print(cmd)

                    newHost.cmd(cmd % (id))

                    print("Started new node: %s" % newHost)

                    recordNodesInfo()

                clearFileCMD()

        sleep(2)


class myCommand(Cmd):
    intro = "Control the bitcoin simulation network. Type help or ? to list commands.\n"
    prompt = ">>> "

    def do_EXIT(self):
        os.system("killall -SIGKILL xterm")
        os.system("mn --clean > /dev/null 2>&1")

    def do_ShowNodes(self, line):
        for i, host in enumerate(P2PNet.hosts):
            print(i, host.IP, host.name)

    def do_AddNode(self, line):

        id = len(P2PNet.hosts)

        newHost = P2PNet.addHost("h%ds%d" % (id, id))

        switch = P2PNet.switches[0];

        P2PNet.addLink(switch, newHost);

        slink = Link(switch, newHost)
        switch.attach(slink);
        switch.start(P2PNet.controllers);

        newHost.configDefault(defaultRoute=newHost.defaultIntf())

        print(P2PNet.hosts[0].cmd("ping -c1 %s" % newHost.IP() ))       #important!!!

        print(newHost.cmd("ping -c1 10.0.0.1"))

        cmd = xtermCMD(newHost.IP(),PORT,P2PNet.hosts[0].IP(),PORT, MODE)

        print(cmd)

        newHost.cmd(cmd % (id))

        print("Started new node: %s" % newHost)

    def do_DelNode(self, line):
        args = line.split()
        if (len(args) != 1):
            print("Expected 1 argument, %d given" % len(args))
        else:
            hostName = args[0].strip()
            node = None;
            for host in P2PNet.hosts:
                if host.name == hostName:
                    node = host;
                    break;
            P2PNet.delNode(node);

    def do_Execute(self,line):
        args = line.split()
        if (len(args) <= 1):
            print("Expected two or more argument, %d given" % len(args))
        else:
            hostName = args[0].strip()
            node = None;
            for host in P2PNet.hosts:
                if host.name == hostName:
                    node = host;
                    break;
            if node !=None:
                path = os.path.join(cur_path,'CMD')
                with open(os.path.join(path, str(node.IP())), 'w') as f:
                    f.write(' '.join(args[2:]));
            else:
                print("no such host : ",hostName)

    def do_CLI(self,Line):
        CLI(P2PNet)


def delete_log():
    log_path = os.path.join(cur_path,'Logs')
    shutil.rmtree(log_path)
    if not os.path.exists(log_path):
        os.mkdir(log_path)

def deleteCMD():

    CMDpath = os.path.join(cur_path,'CMD')
    shutil.rmtree(CMDpath)
    if not os.path.exists(CMDpath):
        os.mkdir(CMDpath)


if __name__ == '__main__':

    try:
        delete_log();
        deleteCMD();
        setupP2PNet(4,3,netType='star');
        myCommand().cmdloop();
    except SystemExit:
        pass
    except:
        traceback.print_exc()
        traceback.print_stack()

        os.system("killall -SIGKILL xterm")
        os.system("mn --clean > /dev/null 2>&1")

