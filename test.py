import collections

from myBlock import myBlock


def test_dict():
    dict = {}
    for i in range(161):
        dict[i] = {}

    tmp = dict[1]
    tmp[2] = 3
    tmp[1] = 2
    print(dict)


def test_blockchain():
    block = myBlock()
    #  Create the blockchain and add the genesis block
    blockchain = [block.create_genesis_block()]
    previous_block = blockchain[0]

    #  How many blocks should we add to the chain after the genesis block
    num_of_blocks_to_add = 20

    for i in range(0, num_of_blocks_to_add):
        block_to_add = block.next_block(previous_block)
        blockchain.append(block_to_add)
        previous_block = block_to_add
        #  Tell everyone about it!
        print("Block #{} has been added to the blockchain!".format(block_to_add.index))
        print("Hash: {}\n".format(block_to_add.hash))


if __name__ == '__main__':
    test_blockchain()
