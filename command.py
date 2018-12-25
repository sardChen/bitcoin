import os

from utils import cur_path


def xtermCMD(ip1, port1, ip2, port2, mode, nodeType="normal"):
    name="Host_%d: "

    file = "setupNode.py"
    file = os.path.join(cur_path, file)

    args = "%s %d %s %d %s %s" % (ip1,port1,ip2,port2,mode,nodeType)

    name = "%s %s %d" % (name, ip1, port1)

    cmd = 'xterm -hold -geometry 130x40+0+900 -title "%s" -e python3 -u "%s" %s &'
    return cmd % (name, file, args)



