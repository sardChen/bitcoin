from aioconsole import ainput

from myBlockChain import BlockChain
from myRPC import *;
from myRoutingTable import KadTable;

import logging  # 引入logging模块
import os.path
#from watchdog.events import *
import time

from myleger import Leger;

class Node(myRPCProtocol):

    def __init__(self, ID=None):

        super(Node, self).__init__()

        if ID is None:
            ID = random_id();

        self.ID = ID;
        self.routingTable = KadTable(self.ID);
        self.recallFunctions = self.recordFunctions();

        self.BroadCasts = [];
        # self.leger = Leger(self.ID);

        self.blockchain = None
        self.local_addr = None





    def setLocalAddr(self,local_addr):
        self.local_addr = local_addr;
        self.initFileCMD()
        self.logger = self.init_logger()
        self.recordbaseInfo()


    def recordFunctions(self):
        funcs = []
        funcs.extend(myRPCProtocol.__dict__.values())
        funcs.extend(Node.__dict__.values())


        return {
            func.funcName: func.recall_function
            for func in funcs if hasattr(func, 'funcName')
        }


    @convert2RPC
    def ping(self,peer,peerID):
        print(self.ID, "handling ping", peer, peerID)
        return (self.ID, peerID)


    @convert2RPC
    def findNodes(self, peer, peerID):
        self.routingTable.add(peerID,peer);
        return self.routingTable.getKpeers(peerID);

    @convert2RPC
    def testBoradCast(self, peer, peerId, args):
        print("Recived boardCast message!!!!", peer, peerId, args)

    @convert2RPC
    def recordTX(self, peer, peerId, transaction):
        print("Recived new transaction!!!!", peer, peerId, transaction)
        if transaction['id'] not in [x['id'] for x in self.blockchain.current_transactions]:
            logging.info("Recived new transaction")
            self.blockchain.current_transactions.append(transaction);
            logging.info(self.blockchain.current_transactions)
            self.recordTXInfo()


    @convert2RPC
    def recordNewBlock(self, peer, peerId, newBlock):
        print("Recived new Block!!!!", peer, peerId, newBlock)
        #TODO record new block right now!!
        logging.info("Recived new Block")
        self.blockchain.chain.append(newBlock);
        IDlist = [x['id'] for x in self.blockchain.chain[-1]['transactions']]
        self.blockchain.removeSomeTX(IDlist)
        logging.info(self.blockchain.chain)
        self.recordBlockInfo()
        self.recordTXInfo()




    @convert2RPC
    def download_peer_blockchain(self, peer, peerID):
        # print(self.ID, "downloading blockchain from", peer, peerID)
        return self.blockchain



    @asyncio.coroutine
    def updateRoutingTable(self, peer):
        # self.routingTable.add(self.ID,self)
        peers = yield from self.findNodes(peer, self.ID)
        for peerID in peers.keys():
            self.routingTable.add(peerID, peers[peerID])

        # self.routingTable.printTable();


    @asyncio.coroutine
    def join(self, peer):

        # print(self.ID, "Pinging ", peer)
        print("myIP: ",self.local_addr," myID: ",self.ID)

        try:
            yield from self.ping(peer, self.ID)
        except socket.timeout:
            print("Could not ping %r", peer)
            return

        try:
            yield from self.updateRoutingTable(peer);
            print("======================print my routing table============================")
            self.routingTable.printTable();
        except socket.timeout:
            print("Could not updateRoutingTable", peer)
            return


        try:
            yield from self.download_blockchain_all();
        except socket.timeout:
            print("Could not download blockchain", peer)
            return

        try:
            tx_id = self.create_transaction(self.blockchain, self.routingTable.getPeerIDByIP(peer[0]), self.ID, random.randint(1,10))
            self.logger.info('init get transactinon from miner = ')
            self.logger.info(self.blockchain.current_transactions)
            self.recordTXInfo()
            yield from self.postBoardcast(random_id(), 'recordTX', self.ID, self.blockchain.current_transactions[-1]);
        except socket.timeout:
            print("Could not get money from node0", peer)
            return


        # test boardcast!
        # if(len(self.routingTable.getNeighborhoods())==3):
        #     yield from self.postBoardcast(random_id(), 'testBoradCast',self.ID,"Testargs");

        # test create transaction and mine
        # peers = self.routingTable.getNeighborhoods()
        # print('peers', peers)
        # if len(peers) > 0 and len(self.blockchain.chain) == 1:
        #     for peerID, peer in peers.items():
        #         tx_id = self.create_transaction(self.blockchain, self.ID, peerID, len(self.blockchain.chain))
        #         print('current transactin = ', self.blockchain.current_transactions)
        #         response = self.mine(self.blockchain, self.ID)
        #         print('after mining, blockchain = ', self.blockchain.chain)
        #         self.logger.info('after mining, blockchain = ')
        #         self.logger.info(self.blockchain.chain)





    @asyncio.coroutine
    def download_blockchain_all(self):
        peers = self.routingTable.getNeighborhoods()

        if len(peers) == 0:
            # genesis block
            self.blockchain = BlockChain(self.ID)
        else:
            for peerID, peer in peers.items():
                receive_blockchain = yield from self.download_peer_blockchain(peers[peerID], self.ID)

                if self.blockchain == None:
                    self.blockchain = receive_blockchain
                    self.blockchain.set_node_id(self.ID)
                elif len(receive_blockchain.chain) > len(self.blockchain.chain):
                    self.blockchain = receive_blockchain
                    self.blockchain.set_node_id(self.ID)

                    # print('blockchain received from', peerID, peer, len(reveive_blockchain.chain))

        print('current blockchain = ', self.blockchain.chain)
        self.logger.info('blockchain.node_id = ' + str(self.blockchain.node_id))
        self.logger.info(self.blockchain.chain)
        self.recordBlockInfo()


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
            amount=random.randint(1,10),
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

    def init_logger(self):
        # 第一步，创建一个logger
        logger = logging.getLogger()
        logger.setLevel(logging.INFO)  # Log等级总开关
        # 第二步，创建一个handler，用于写入日志文件
        rq = time.strftime('%Y%m%d%H%M', time.localtime(time.time()))
        log_path = os.path.join(cur_path,'Logs',str(self.local_addr[0]))

        if not os.path.exists(log_path):
            os.mkdir(log_path)

        log_name = os.path.join(log_path, str(self.ID) + ".log")

        logfile = log_name
        fh = logging.FileHandler(logfile, mode='w')
        fh.setLevel(logging.DEBUG)  # 输出到file的log等级的开关
        # 第三步，定义handler的输出格式
        formatter = logging.Formatter("%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s")
        fh.setFormatter(formatter)
        # 第四步，将logger添加到handler里面
        logger.addHandler(fh)
        return logger

    def recordbaseInfo(self):
        log_path = os.path.join(cur_path, 'Logs', str(self.local_addr[0]))

        if not os.path.exists(log_path):
            os.mkdir(log_path)

        baseInfo = os.path.join(log_path, "baseInfo")
        with open(baseInfo,'w') as f:
            f.write(str(self.ID)+"\n")
            f.write(str(self.local_addr)+"\n")

    def recordTXInfo(self):
        log_path = os.path.join(cur_path, 'Logs', str(self.local_addr[0]))

        if not os.path.exists(log_path):
            os.mkdir(log_path)

        TXInfo = os.path.join(log_path, "TXInfo")
        save_data(self.blockchain.current_transactions,TXInfo)

    def recordBlockInfo(self):
        log_path = os.path.join(cur_path, 'Logs', str(self.local_addr[0]))

        if not os.path.exists(log_path):
            os.mkdir(log_path)

        BlockInfo = os.path.join(log_path, "BlockInfo")
        save_data(self.blockchain.chain,BlockInfo)


    def initFileCMD(self):
        path = os.path.join(cur_path,'CMD')

        with open(os.path.join(path,str(self.local_addr[0])), 'w') as f:
            f.close();


    def create_transaction(self, blockchain, sender, recipient, amount):
        # Create a new Transaction
        tx_index = blockchain.new_transaction(sender, recipient, amount)
        return tx_index


    @asyncio.coroutine
    def pingAll(self, peer, peerID):
        peers = self.routingTable.getNeighborhoods();
        for peerID, peer in peers.keys():
            yield from self.ping(peers[peerID], self.ID);


    @asyncio.coroutine
    def postBoardcast(self, messageID, funcName, *args):
        if messageID not in self.BroadCasts:
            self.BroadCasts.append(messageID);

            obj = ('broadcast', messageID, funcName, *args)
            message = pickle.dumps(obj, protocol=0)

            peers = self.routingTable.getNeighborhoods();

            for peer in peers.values():
                self.transport.sendto(message, peer)




#收到的所有请求,更新路由表
    # 处理请求
    def handleRequest(self, peer, messageID, funcName, args, kwargs):
        peerID = args[0];
        self.routingTable.add(peerID,peer);
        super(Node, self).handleRequest(peer, messageID, funcName, args, kwargs);




    # 处理回复
    def handleReply(self, peer, messageID, response):
        peerID, response = response;
        self.routingTable.add(peerID,peer);
        super(Node, self).handleReply(peer, messageID, response);



    # 处理广播
    def handleBroadcast(self, peer, messageID, funcName, *args):
        peerID = args[0];
        self.routingTable.add(peerID, peer);

        if messageID not in self.BroadCasts:
            self.BroadCasts.append(messageID);
            self.postBoardcast(messageID, funcName, args);
            super(Node,self).handleBroadcast(peer, messageID, funcName, *args);

    # 处理超时
    def handletimeout(self, messageID, args, kwargs):
        peerID = args[0];
        self.routingTable.remove(peerID);
        super(Node, self).handletimeout( messageID, args, kwargs);




#=================监听命令行=====================#
    async def nodeCommand(self):

        while True:
            line = await ainput(">>> ")
            line = line.strip()

            if not line:
                continue;


            await self.dealCMD(line)

# =================监听文件命令行=====================#

    async def fileCommand(self):
        while True:
            line = self.readFromFile()
            if line != None:
                line = line.strip()
                if len(line) > 0:
                    await self.dealCMD(line)
                    self.clearFileCMD()

            await asyncio.sleep(2)




    def printHelpList(self):
        print("==========this is a help list!==========")


    def printLog(self):
        path = os.path.join(cur_path,'Logs')
        with open(os.path.join(path, str(self.ID)+".log"), 'r') as f:
            lines = f.readlines()
            for line in lines:
                print(line)


    def clearFileCMD(self):
        path = os.path.join(cur_path,'CMD')
        with open(os.path.join(path, str(self.local_addr[0])), 'w') as f:
            f.close()

    def readFromFile(self):
        path = os.path.join(cur_path,'CMD')
        with open(os.path.join(path,str(self.local_addr[0])),'r') as f:
            lines = f.readlines();
            if len(lines)>0:
                return lines[0].strip();
            else:
                return None;

    async def dealCMD(self,line):
        line = line.split();

        cmd = line[0];
        args = line[1:];

        if cmd in ["?", "help"]:
            self.printHelpList();

        elif cmd in ["id"]:
            print("NodeId : ", self.ID);

        elif cmd in ["ip"]:
            print("<ip,port> ",self.local_addr)

        elif cmd in ["showHashTable"]:
            self.routingTable.printTable();

        elif cmd in ["showlog"]:
            self.printLog();

        elif cmd in ["ping"]:
            IP = args[0];
            peer = self.routingTable.getPeerByIP(IP)
            if peer != None:
                try:
                    await self.ping(peer, self.ID);
                except socket.timeout:
                    print("Could not ping %r", peer)
                    return
            else:
                print("peerIP : ", IP, " not exist!");

        elif cmd in ["testBoardCast"]:
            try:
                await self.postBoardcast(random_id(), 'testBoradCast', self.ID, "Testargs");
            except socket.timeout:
                print(self.ID, ": could not postBoardcast")
                return
        elif cmd in ["mine"]:
            response = self.mine(self.blockchain, self.ID)
            # IDlist = [x.id for x in self.blockchain.chain[-1]['transactions']]
            # self.blockchain.removeSomeTX(IDlist)
            self.logger.info('after mining, blockchain = ')
            self.logger.info(self.blockchain.chain)
            # broadcast new Blcokchain
            self.recordBlockInfo()
            self.recordTXInfo()
            await self.postBoardcast(random_id(), 'recordNewBlock', self.ID, self.blockchain.chain[-1]);


        elif cmd in ["createTx"]:
            IP = args[0];
            amount = int(args[1])
            peerID = self.routingTable.getPeerIDByIP(IP)
            # check for enough money
            tx_id = self.create_transaction(self.blockchain, self.ID, str(peerID), amount)
            self.logger.info('current transactinon = ')
            self.logger.info(self.blockchain.current_transactions)
            self.recordTXInfo()
            await self.postBoardcast(random_id(), 'recordTX', self.ID, self.blockchain.current_transactions[-1]);


