# -*- coding:utf-8 -*-
from cmd import Cmd


def xtermCMD(ip1, port1, ip2, port2):
    name = "Host_%d: "
    file = "setupNode.py"
    args = "%s %d %s %d" % (ip1, port1, ip2, port2)

    name = "%s %s %d" % (name, ip1, port1)

    cmd = 'xterm -hold -geometry 130x40+0+900 -title "%s" -e python3 -u "%s" %s &'
    return cmd % (name, file, args)


class myCammand(Cmd):
    # def __init__(self):
    #     super().__init__(self);

    def do_EOF(self, line):
        self.do_stop_network(None)
