import time
from typing import List, Dict, Optional
from block import Block
from transaction import Transaction, TransactionOutput, TransactionInput
from mempool import Mempool
from crypto_utils import CryptoUtils


class AdvancedBlockchain:
    def __init__(self, difficulty: int = 4, block_reward: float = 50.0):
        self.chain: List[Block] = []
        self.difficulty = difficulty
        self.block_reward = block_reward
        self.mempool = Mempool()
        self.utxo_set: Dict[str, TransactionOutput] = {}
        self.public_keys: Dict[str, str] = {}
        self.target_block_time = 60
        self.difficulty_adjustment_interval = 10

        self.create_genesis_block()

    def create_genesis_block(self):
        genesis_tx = Transaction.create_coinbase_transaction("GENESIS", self.block_reward, 0)
        genesis_block = Block(0, [genesis_tx], "0")
        genesis_block.mine_block(self.difficulty)
        self.chain.append(genesis_block)

        self.utxo_set[f"{genesis_tx.tx_id}:0"] = genesis_tx.outputs[0]

    def get_latest_block(self) -> Block:
        return self.chain[-1]

    def add_transaction(self, transaction: Transaction) -> bool:
        if not transaction.inputs:
            return False

        if not self.mempool.add_transaction(transaction, self.utxo_set, self.public_keys):
            return False

        print(f"Transaction added to mempool: {transaction.tx_id}")
        return True

    def mine_block(self, miner_address: str, force: bool = False) -> Optional[Block]:
        transactions = self.mempool.get_transactions_for_mining(100)

        if not transactions and not force:
            print("No transactions to mine")
            return None

        total_fees = sum(tx.get_fee(self.utxo_set) for tx in transactions) if transactions else 0

        coinbase_tx = Transaction.create_coinbase_transaction(
            miner_address,
            self.block_reward,
            total_fees
        )

        block_transactions = [coinbase_tx] + transactions

        new_block = Block(
            len(self.chain),
            block_transactions,
            self.get_latest_block().hash
        )

        print(f"Mining block {new_block.index} with {len(transactions)} transactions...")
        new_block.mine_block(self.difficulty)

        for tx in transactions:
            for tx_input in tx.inputs:
                utxo_key = f"{tx_input.tx_id}:{tx_input.output_index}"
                if utxo_key in self.utxo_set:
                    del self.utxo_set[utxo_key]

        for tx in block_transactions:
            for i, output in enumerate(tx.outputs):
                utxo_key = f"{tx.tx_id}:{i}"
                self.utxo_set[utxo_key] = output

        self.chain.append(new_block)

        tx_ids = [tx.tx_id for tx in transactions]
        self.mempool.clear_transactions(tx_ids)

        if len(self.chain) % self.difficulty_adjustment_interval == 0:
            self.adjust_difficulty()

        return new_block

    def adjust_difficulty(self):
        if len(self.chain) < self.difficulty_adjustment_interval:
            return

        recent_blocks = self.chain[-self.difficulty_adjustment_interval:]
        time_taken = recent_blocks[-1].timestamp - recent_blocks[0].timestamp
        expected_time = self.target_block_time * self.difficulty_adjustment_interval

        if time_taken < expected_time * 0.5:
            self.difficulty += 1
            print(f"Difficulty increased to {self.difficulty}")
        elif time_taken > expected_time * 2:
            if self.difficulty > 1:
                self.difficulty -= 1
                print(f"Difficulty decreased to {self.difficulty}")

    def get_balance(self, address: str) -> float:
        balance = 0.0
        for utxo_key, utxo in self.utxo_set.items():
            if utxo.address == address:
                balance += utxo.amount
        return balance

    def get_utxos_for_address(self, address: str) -> List[tuple]:
        utxos = []
        for utxo_key, utxo in self.utxo_set.items():
            if utxo.address == address:
                tx_id, output_index = utxo_key.split(':')
                utxos.append((tx_id, int(output_index), utxo.amount))
        return utxos

    def is_chain_valid(self) -> bool:
        for i in range(1, len(self.chain)):
            current_block = self.chain[i]
            previous_block = self.chain[i - 1]

            if current_block.hash != current_block.calculate_hash():
                return False

            if current_block.previous_hash != previous_block.hash:
                return False

            if current_block.merkle_root != current_block.calculate_merkle_root():
                return False

        return True

    def get_transaction_by_id(self, tx_id: str) -> Optional[Transaction]:
        for block in self.chain:
            for tx in block.transactions:
                if tx.tx_id == tx_id:
                    return tx

        return self.mempool.get_transaction(tx_id)

    def get_block_by_hash(self, block_hash: str) -> Optional[Block]:
        for block in self.chain:
            if block.hash == block_hash:
                return block
        return None

    def get_block_by_index(self, index: int) -> Optional[Block]:
        if 0 <= index < len(self.chain):
            return self.chain[index]
        return None

    def get_chain_info(self) -> Dict:
        return {
            'length': len(self.chain),
            'difficulty': self.difficulty,
            'block_reward': self.block_reward,
            'mempool_size': self.mempool.size(),
            'utxo_count': len(self.utxo_set),
            'latest_block_hash': self.get_latest_block().hash,
            'is_valid': self.is_chain_valid()
        }

    def get_mining_stats(self) -> Dict:
        if len(self.chain) < 2:
            return {
                'average_block_time': 0,
                'hash_rate': 0,
                'total_blocks': len(self.chain),
                'difficulty': self.difficulty
            }

        recent_blocks = self.chain[-10:] if len(self.chain) >= 10 else self.chain[1:]
        total_time = recent_blocks[-1].timestamp - recent_blocks[0].timestamp
        avg_block_time = total_time / len(recent_blocks) if recent_blocks else 0

        return {
            'average_block_time': avg_block_time,
            'total_blocks': len(self.chain),
            'difficulty': self.difficulty
        }
