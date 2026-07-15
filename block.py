import time
from typing import List, Dict, Any
from transaction import Transaction
from crypto_utils import CryptoUtils


class Block:
    def __init__(self, index: int, transactions: List[Transaction], previous_hash: str, timestamp: float = None, nonce: int = 0):
        self.index = index
        self.transactions = transactions
        self.previous_hash = previous_hash
        self.timestamp = timestamp or time.time()
        self.nonce = nonce
        self.merkle_root = self.calculate_merkle_root()
        self.hash = self.calculate_hash()

    def calculate_merkle_root(self) -> str:
        tx_dicts = [tx.to_dict() for tx in self.transactions]
        return CryptoUtils.calculate_merkle_root(tx_dicts)

    def calculate_hash(self) -> str:
        block_data = {
            'index': self.index,
            'merkle_root': self.merkle_root,
            'previous_hash': self.previous_hash,
            'timestamp': self.timestamp,
            'nonce': self.nonce
        }
        return CryptoUtils.hash_data(block_data)

    def mine_block(self, difficulty: int):
        target = "0" * difficulty
        while self.hash[:difficulty] != target:
            self.nonce += 1
            self.hash = self.calculate_hash()
        print(f"Block mined: {self.hash} (nonce: {self.nonce})")

    def to_dict(self) -> Dict[str, Any]:
        return {
            'index': self.index,
            'hash': self.hash,
            'previous_hash': self.previous_hash,
            'timestamp': self.timestamp,
            'nonce': self.nonce,
            'merkle_root': self.merkle_root,
            'transactions': [tx.to_dict() for tx in self.transactions]
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'Block':
        transactions = [Transaction.from_dict(tx) for tx in data['transactions']]
        block = Block(
            data['index'],
            transactions,
            data['previous_hash'],
            data['timestamp'],
            data['nonce']
        )
        block.hash = data['hash']
        block.merkle_root = data['merkle_root']
        return block
