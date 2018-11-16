# -*- coding:utf-8 -*-

import hashlib
import datetime


# https://blog.csdn.net/simple_the_best/article/details/75448617
# https://learnblockchain.cn/2017/10/27/build_blockchain_by_python/
class myBlock():

    def __init__(self, index=0, timestamp=datetime.datetime.now(), data='', previous_hash='0'):
        self.index = index
        self.timestamp = timestamp
        self.data = data
        self.previous_hash = previous_hash
        self.hash = self.hash_block()

    def hash_block(self):
        sha = hashlib.sha256()
        sha.update(
            bytes(
                str(self.index) + str(self.timestamp) + str(self.data) + str(
                    self.previous_hash), 'utf-8'))
        return sha.hexdigest()

    def create_genesis_block(self):
        #  Manually construct a block with index 0 and arbitrary previous hash
        return myBlock(0, datetime.datetime.now(), "Genesis Block", "0")

    def next_block(self, last_block):
        this_index = last_block.index + 1
        this_timestamp = datetime.datetime.now()
        this_data = "Hey! I'm block " + str(this_index)
        this_hash = last_block.hash
        return myBlock(this_index, this_timestamp, this_data, this_hash)
