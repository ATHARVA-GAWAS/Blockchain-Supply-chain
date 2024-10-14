# supply_chain/blockchain.py

import hashlib
import json
from time import time
from urllib.parse import urlparse

class Blockchain:
    def __init__(self):
        self.chain = []
        self.current_transactions = []
        self.validators = set()  # Set of authorized validators
        self.new_block(previous_hash='1', proof=100)  # Create the genesis block

    def new_block(self, proof, previous_hash=None):
        block = {
            'index': len(self.chain) + 1,
            'timestamp': time(),
            'transactions': self.current_transactions,
            'proof': proof,
            'previous_hash': previous_hash or self.hash(self.chain[-1]),
        }
        self.current_transactions = []  # Reset the current list of transactions
        self.chain.append(block)
        return block

    def new_transaction(self, seller, buyer, product_id, quantity, price):
        self.current_transactions.append({
            'seller': seller,
            'buyer': buyer,
            'product_id': product_id,
            'quantity': quantity,
            'price': price,
        })
        return self.last_block['index'] + 1

    @staticmethod
    def hash(block):
        block_string = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()

    @property
    def last_block(self):
        return self.chain[-1]

    def add_validator(self, validator):
        self.validators.add(validator)

    def validate_transaction(self, transaction):
        seller = transaction['seller']
        # Only authorized sellers can create transactions
        if seller in self.validators:
            return True
        return False

    def consensus(self):
        # A simple consensus method where we assume transactions are confirmed
        # if they come from an authorized validator.
        for transaction in self.current_transactions:
            if not self.validate_transaction(transaction):
                raise Exception("Unauthorized transaction attempt detected.")
        proof = 1  # You can implement additional logic here for proof generation
        return proof

    def mine_block(self):
        # This function would be called to mine a block based on the current transactions.
        proof = self.consensus()  # Get consensus proof
        previous_hash = self.hash(self.last_block)
        return self.new_block(proof, previous_hash)

# Example usage
blockchain = Blockchain()

# Adding validators (this should be done in your user management logic)
blockchain.add_validator('farmer_1')
blockchain.add_validator('distributor_1')

# New transaction
blockchain.new_transaction(seller='farmer_1', buyer='distributor_1', product_id='crop_001', quantity=10, price=100)

# Mine the block after consensus is achieved
blockchain.mine_block()
