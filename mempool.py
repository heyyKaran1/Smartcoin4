from typing import List, Dict
from transaction import Transaction, TransactionOutput


class Mempool:
    def __init__(self):
        self.pending_transactions: Dict[str, Transaction] = {}

    def add_transaction(self, transaction: Transaction, utxo_set: Dict[str, TransactionOutput], public_keys: Dict[str, str] = None) -> bool:
        if transaction.tx_id in self.pending_transactions:
            return False

        if not transaction.verify_transaction(utxo_set, public_keys):
            return False

        for tx_input in transaction.inputs:
            utxo_key = f"{tx_input.tx_id}:{tx_input.output_index}"
            for existing_tx in self.pending_transactions.values():
                for existing_input in existing_tx.inputs:
                    existing_utxo_key = f"{existing_input.tx_id}:{existing_input.output_index}"
                    if utxo_key == existing_utxo_key:
                        return False

        self.pending_transactions[transaction.tx_id] = transaction
        return True

    def remove_transaction(self, tx_id: str):
        if tx_id in self.pending_transactions:
            del self.pending_transactions[tx_id]

    def get_transactions_for_mining(self, max_transactions: int = 100) -> List[Transaction]:
        sorted_txs = sorted(
            self.pending_transactions.values(),
            key=lambda tx: self.calculate_priority(tx),
            reverse=True
        )
        return sorted_txs[:max_transactions]

    def calculate_priority(self, transaction: Transaction) -> float:
        return len(transaction.inputs) + len(transaction.outputs)

    def clear_transactions(self, transaction_ids: List[str]):
        for tx_id in transaction_ids:
            self.remove_transaction(tx_id)

    def get_transaction(self, tx_id: str) -> Transaction:
        return self.pending_transactions.get(tx_id)

    def get_all_transactions(self) -> List[Transaction]:
        return list(self.pending_transactions.values())

    def size(self) -> int:
        return len(self.pending_transactions)
