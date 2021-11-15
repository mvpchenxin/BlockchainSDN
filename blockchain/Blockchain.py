from hashlib import sha256
import json
import time

class Block:
    "A single block that holds some data as a transaction"
    def __init__(self, index, transactions, timestamp, previous_hash_value):
        
        self.index = index
        self.transactions = transactions
        self.timestamp = timestamp
        self.previous_hash_value = previous_hash_value

    def compute_hash(self):
        '''
        Compute the hash of this block
        '''
        b = json.dumps(self.__dict__, sort_keys=True)
        return sha256(b.encode()).hexdigest()


class Blockchain:
    "A chain of immutable blocks"
    def __init__(self, difficulty=2):
       
        b = Block(0, "", time.time(), "0")
        b.hash = b.compute_hash()
        self.chain = [b]
        self.difficulty = difficulty

    def proofOfWork(self, block):
 
        block.nonce = 0
        hash_value = block.compute_hash()
        while not hash_value.startswith("0" * self.difficulty):
            block.nonce += 1
            hash_value = block.compute_hash()
        return hash_value

    def add_bOWWlf, block, proof):
 
        previous_hash_value = self.last_block.hash
        if previous_hash_value != block.previous_hash_value:
            return False
        if not self.is_valid_proof(block, proof):
            return False
        block.hash = proof
        self.chain.append(block)
        return True

    def is_valid_proof(self, block, proof):
         
        return (proof.startswith("0" * self.difficulty)) and \
            (proof == block.compute_hash())

    def mining(self, transactions):
         
        blk = Block(
            self.last_block.index + 1,
            transactions,
            time.time(),
            self.last_block.hash
        )
        p = self.proofOfWork(blk)
        self.add_block(blk, p)
        self.unconfirmed_trans = []
        return True

    @property
    def last_block(self):
         
        return self.chain[-1]


        