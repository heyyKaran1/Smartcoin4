import time
from typing import List, Dict, Any, Optional
from crypto_utils import CryptoUtils
from ecdsa import SigningKey


class TransactionInput:
    def __init__(self, tx_id: str, output_index: int, signature: str = ""):
        self.tx_id = tx_id
        self.output_index = output_index
        self.signature = signature

    def to_dict(self) -> Dict[str, Any]:
        return {
            'tx_id': self.tx_id,
            'output_index': self.output_index,
            'signature': self.signature
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'TransactionInput':
        return TransactionInput(
            data['tx_id'],
            data['output_index'],
            data.get('signature', '')
        )


class TransactionOutput:
    def __init__(self, address: str, amount: float):
        self.address = address
        self.amount = amount

    def to_dict(self) -> Dict[str, Any]:
        return {
            'address': self.address,
            'amount': self.amount
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'TransactionOutput':
        return TransactionOutput(data['address'], data['amount'])


class Transaction:
    def __init__(self, inputs: List[TransactionInput], outputs: List[TransactionOutput], timestamp: float = None):
        self.inputs = inputs
        self.outputs = outputs
        self.timestamp = timestamp or time.time()
        self.tx_id = self.calculate_hash()
        self.merchant_details = None

    def calculate_hash(self) -> str:
        tx_data = {
            'inputs': [inp.to_dict() for inp in self.inputs],
            'outputs': [out.to_dict() for out in self.outputs],
            'timestamp': self.timestamp
        }
        return CryptoUtils.hash_data(tx_data)

    def sign_transaction(self, private_key: SigningKey, utxo_set: Dict[str, TransactionOutput]):
        for tx_input in self.inputs:
            utxo_key = f"{tx_input.tx_id}:{tx_input.output_index}"
            if utxo_key not in utxo_set:
                raise ValueError(f"UTXO not found: {utxo_key}")

            utxo = utxo_set[utxo_key]
            public_key = private_key.get_verifying_key()
            address = CryptoUtils.public_key_to_address(public_key)

            if utxo.address != address:
                raise ValueError(f"Cannot sign input: address mismatch")

            sign_data = {
                'tx_id': tx_input.tx_id,
                'output_index': tx_input.output_index,
                'outputs': [out.to_dict() for out in self.outputs],
                'timestamp': self.timestamp
            }
            tx_input.signature = CryptoUtils.sign_data(private_key, sign_data)

        self.tx_id = self.calculate_hash()

    def verify_transaction(self, utxo_set: Dict[str, TransactionOutput], public_keys: Dict[str, str] = None) -> bool:
        if not self.inputs:
            return True

        total_input = 0
        total_output = sum(out.amount for out in self.outputs)

        for tx_input in self.inputs:
            utxo_key = f"{tx_input.tx_id}:{tx_input.output_index}"
            if utxo_key not in utxo_set:
                return False

            utxo = utxo_set[utxo_key]
            total_input += utxo.amount

            if public_keys and utxo.address in public_keys:
                public_key_string = public_keys[utxo.address]
            else:
                if not tx_input.signature:
                    return False
                continue

            try:
                public_key = CryptoUtils.string_to_public_key(public_key_string)
            except:
                return False

            sign_data = {
                'tx_id': tx_input.tx_id,
                'output_index': tx_input.output_index,
                'outputs': [out.to_dict() for out in self.outputs],
                'timestamp': self.timestamp
            }

            if not CryptoUtils.verify_signature(public_key, sign_data, tx_input.signature):
                return False

        if total_input < total_output:
            return False

        return True

    def get_public_key_from_utxo(self, utxo: TransactionOutput, utxo_set: Dict[str, TransactionOutput]) -> Optional[str]:
        return None

    def get_fee(self, utxo_set: Dict[str, TransactionOutput]) -> float:
        total_input = sum(utxo_set[f"{inp.tx_id}:{inp.output_index}"].amount
                         for inp in self.inputs
                         if f"{inp.tx_id}:{inp.output_index}" in utxo_set)
        total_output = sum(out.amount for out in self.outputs)
        return total_input - total_output

    def to_dict(self) -> Dict[str, Any]:
        result = {
            'tx_id': self.tx_id,
            'inputs': [inp.to_dict() for inp in self.inputs],
            'outputs': [out.to_dict() for out in self.outputs],
            'timestamp': self.timestamp
        }
        if self.merchant_details:
            result['merchant_details'] = self.merchant_details
        return result

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'Transaction':
        inputs = [TransactionInput.from_dict(inp) for inp in data['inputs']]
        outputs = [TransactionOutput.from_dict(out) for out in data['outputs']]
        tx = Transaction(inputs, outputs, data['timestamp'])
        tx.tx_id = data['tx_id']
        if 'merchant_details' in data:
            tx.merchant_details = data['merchant_details']
        return tx

    @staticmethod
    def create_coinbase_transaction(miner_address: str, block_reward: float, fees: float) -> 'Transaction':
        outputs = [TransactionOutput(miner_address, block_reward + fees)]
        return Transaction([], outputs)
