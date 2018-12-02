
from utils import HashLen;


def distance(peer1ID, peer2ID):
    return HashLen - (peer1ID ^ peer2ID).bit_length;

class KadTable(object):
    def __init__(self, ID, k=8):
        self.ID = ID;
        self.k = k;
        self.buckets = {};
        for i in range(HashLen+1):
            self.buckets[i] = {};
        super(KadTable, self).__init__();


    def add(self, peerID, peer):
        bucket = self.buckets[self.distance(peerID)];
#        if(len(bucket) < self.k):
        if peerID in bucket:
            del bucket[peerID];
        bucket[peerID] = peer;

    def getPeerById(self,peerID):
        bucket = self.buckets[self.distance(peerID)];
        if peerID in bucket:
            return bucket[peerID];
        return None;

    def remove(self, peerID):
        bucket = self.buckets[self.distance(peerID)];
        if peerID in bucket:
            del bucket[peerID];

    #TODO
    def getKpeers(self, peerID):
        peers = {};
        for i in self.buckets.keys():
            for ID in self.buckets[i].keys():
                if(ID != peerID):
                    peers[ID] = self.buckets[i][ID];
        return peers;

    # TODO
    def getNeighborhoods(self):
        peers = {};
        for i in self.buckets.keys():
            for ID in self.buckets[i].keys():
                if (ID != self.ID):
                    peers[ID] = self.buckets[i][ID];
        return peers;


    def distance(self,peerID):
        # print(self.ID,"   ",peerID)
        return HashLen - (self.ID ^ peerID).bit_length();

    def printTable(self):
        for i in self.buckets.keys():
            for ID in self.buckets[i].keys():
                print(ID, " : ", self.buckets[i][ID]);
