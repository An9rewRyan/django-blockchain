from hashlib import sha256
import json
from binascii import unhexlify, hexlify
from typing import List


class Block:

    def __init__(self, previous_hash: str, difficulty: str,
                 version: str, time: str, nonce: int = 1):
        self.headers = {
            'version': version,
            'previous_hash': previous_hash,
            'merkel_root': [],
            'time': time,
            'difficulty': difficulty,
            'nonce': nonce,

        }
        self.transactions = []
        self.transaction_counter = 0
        self.blocksize = 10  # in megabytes

    def set_merkel_root(self) -> str:

        while len(self.headers["merkel_root"]) != 1:
            hashed_trunsactions = []
            for i in range(0, len(self.headers["merkel_root"]) - 1, 2):
                curr_hex = sha256(
                    str(self.headers["merkel_root"][i]).encode()).hexdigest()
                next_hex = sha256(
                    str(self.headers["merkel_root"][i + 1]).encode()).hexdigest()
                hash_pair = sha256((curr_hex + next_hex).encode()).hexdigest()
                hashed_trunsactions.append(hash_pair)
                print(hashed_trunsactions, self.headers["merkel_root"])
            self.headers["merkel_root"] = hashed_trunsactions

        return self.headers["merkel_root"]

    def double_sha256(self, data: str) -> str:
        data_bin = data.encode()
        data_hash = sha256(sha256(data_bin).digest()).digest()
        data_hash_decoded = hexlify(data_hash[::-1]).decode("utf-8")

        return data_hash_decoded

    def hash_headers(self) -> str:

        hashed_header = self.double_sha256(str(self.headers))

        return hashed_header

    def hash_block(self, nonce: int) -> str:
        encoded_block = self.double_sha256(str(self.headers) + str(nonce))
        return encoded_block
