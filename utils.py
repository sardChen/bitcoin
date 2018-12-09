import binascii
import hashlib
import pickle
import random

import ecdsa

# This elliptic curve is used by bitcoin too
CURVE = ecdsa.SECP256k1

HashLen = 160;

cur_path = '/home/findns/Projects/Python/bitcoin'


def sha1_int(key):
    if hasattr(key, 'encode'):
        key = key.encode()

    digest = hashlib.sha1(key).digest()

    return int.from_bytes(digest, byteorder='big', signed=False)


def random_id():
    ID = random.getrandbits(HashLen)

    return sha1_int(ID.to_bytes(20, byteorder='big', signed=False))


def gen_pub_pvt():
    """
    Generate key-pair.
    """

    sk = ecdsa.SigningKey.generate(curve=CURVE)
    vk = sk.get_verifying_key()

    pvt_key = binascii.hexlify(sk.to_string()).decode()
    pub_key = binascii.hexlify(vk.to_string()).decode()

    return pub_key, pvt_key


def sign_msg(pvt_key, msg):
    pvt_key = binascii.unhexlify(pvt_key.encode())
    sk = ecdsa.SigningKey.from_string(pvt_key, curve=CURVE)

    sign = sk.sign(msg.encode())
    sign = binascii.hexlify(sign).decode()

    return sign


def verify_msg(pub_key, msg, sign):
    pub_key = binascii.unhexlify(pub_key.encode())
    vk = ecdsa.VerifyingKey.from_string(pub_key, curve=CURVE)

    sign = binascii.unhexlify(sign.encode())

    return vk.verify(sign, msg.encode())


def save_data(data, file_path):
    file = open(file_path, 'wb')
    pickle.dump(data, file)
    file.close()

def get_data(file_path):
    file = open(file_path, 'rb')
    data = pickle.load(file)
    file.close()
    return data
