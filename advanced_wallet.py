import json
from typing import List, Optional
from ecdsa import SigningKey, VerifyingKey
from crypto_utils import CryptoUtils
from transaction import Transaction, TransactionInput, TransactionOutput


class AdvancedWallet:
    def __init__(self):
        self.private_key, self.public_key = CryptoUtils.generate_keypair()
        self.address = CryptoUtils.public_key_to_address(self.public_key)

    def get_address(self) -> str:
        return self.address

    def get_public_key(self) -> VerifyingKey:
        return self.public_key

    def get_private_key(self) -> SigningKey:
        return self.private_key

    def create_transaction(self, to_address: str, amount: float, fee: float, blockchain) -> Optional[Transaction]:
        balance = blockchain.get_balance(self.address)

        if balance < amount + fee:
            print(f"Insufficient balance. Required: {amount + fee}, Available: {balance}")
            return None

        utxos = blockchain.get_utxos_for_address(self.address)

        selected_utxos = []
        total_input = 0.0

        for tx_id, output_index, utxo_amount in utxos:
            selected_utxos.append((tx_id, output_index, utxo_amount))
            total_input += utxo_amount
            if total_input >= amount + fee:
                break

        if total_input < amount + fee:
            print(f"Could not gather enough UTXOs")
            return None

        inputs = [TransactionInput(tx_id, output_index) for tx_id, output_index, _ in selected_utxos]

        outputs = [TransactionOutput(to_address, amount)]

        change = total_input - amount - fee
        if change > 0.0001:
            outputs.append(TransactionOutput(self.address, change))

        transaction = Transaction(inputs, outputs)

        try:
            transaction.sign_transaction(self.private_key, blockchain.utxo_set)
            blockchain.public_keys[self.address] = CryptoUtils.public_key_to_string(self.public_key)
            print(f"Transaction created: {transaction.tx_id}")
            return transaction
        except Exception as e:
            print(f"Failed to sign transaction: {e}")
            return None

    def export_wallet(self) -> dict:
        return {
            'address': self.address,
            'public_key': CryptoUtils.public_key_to_string(self.public_key),
            'private_key': CryptoUtils.private_key_to_string(self.private_key)
        }

    def export_to_file(self, filename: str):
        wallet_data = self.export_wallet()
        with open(filename, 'w') as f:
            json.dump(wallet_data, f, indent=2)
        print(f"Wallet exported to {filename}")

    @staticmethod
    def import_wallet(wallet_data: dict) -> 'AdvancedWallet':
        wallet = AdvancedWallet.__new__(AdvancedWallet)
        wallet.private_key = CryptoUtils.string_to_private_key(wallet_data['private_key'])
        wallet.public_key = CryptoUtils.string_to_public_key(wallet_data['public_key'])
        wallet.address = wallet_data['address']
        return wallet

    @staticmethod
    def import_from_file(filename: str) -> 'AdvancedWallet':
        with open(filename, 'r') as f:
            wallet_data = json.load(f)
        return AdvancedWallet.import_wallet(wallet_data)

    def sign_message(self, message: str) -> str:
        return CryptoUtils.sign_data(self.private_key, {'message': message})

    def verify_message(self, message: str, signature: str, public_key: VerifyingKey) -> bool:
        return CryptoUtils.verify_signature(public_key, {'message': message}, signature)
