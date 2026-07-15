import hashlib
import json
from ecdsa import SigningKey, VerifyingKey, SECP256k1, BadSignatureError
from typing import Dict, Any


class CryptoUtils:
    @staticmethod
    def generate_keypair():
        private_key = SigningKey.generate(curve=SECP256k1)
        public_key = private_key.get_verifying_key()
        return private_key, public_key

    @staticmethod
    def private_key_to_string(private_key: SigningKey) -> str:
        return private_key.to_string().hex()

    @staticmethod
    def public_key_to_string(public_key: VerifyingKey) -> str:
        return public_key.to_string().hex()

    @staticmethod
    def string_to_private_key(key_string: str) -> SigningKey:
        return SigningKey.from_string(bytes.fromhex(key_string), curve=SECP256k1)

    @staticmethod
    def string_to_public_key(key_string: str) -> VerifyingKey:
        return VerifyingKey.from_string(bytes.fromhex(key_string), curve=SECP256k1)

    @staticmethod
    def public_key_to_address(public_key: VerifyingKey) -> str:
        public_key_bytes = public_key.to_string()
        sha256_hash = hashlib.sha256(public_key_bytes).digest()
        ripemd160 = hashlib.new('ripemd160')
        ripemd160.update(sha256_hash)
        return ripemd160.hexdigest()

    @staticmethod
    def sign_data(private_key: SigningKey, data: Dict[str, Any]) -> str:
        data_string = json.dumps(data, sort_keys=True)
        signature = private_key.sign(data_string.encode())
        return signature.hex()

    @staticmethod
    def verify_signature(public_key: VerifyingKey, data: Dict[str, Any], signature: str) -> bool:
        try:
            data_string = json.dumps(data, sort_keys=True)
            public_key.verify(bytes.fromhex(signature), data_string.encode())
            return True
        except BadSignatureError:
            return False

    @staticmethod
    def hash_data(data: Any) -> str:
        if isinstance(data, dict) or isinstance(data, list):
            data_string = json.dumps(data, sort_keys=True)
        else:
            data_string = str(data)
        return hashlib.sha256(data_string.encode()).hexdigest()

    @staticmethod
    def calculate_merkle_root(transactions: list) -> str:
        if not transactions:
            return hashlib.sha256(b'').hexdigest()

        transaction_hashes = [CryptoUtils.hash_data(tx) for tx in transactions]

        while len(transaction_hashes) > 1:
            if len(transaction_hashes) % 2 != 0:
                transaction_hashes.append(transaction_hashes[-1])

            new_hashes = []
            for i in range(0, len(transaction_hashes), 2):
                combined = transaction_hashes[i] + transaction_hashes[i + 1]
                new_hash = hashlib.sha256(combined.encode()).hexdigest()
                new_hashes.append(new_hash)

            transaction_hashes = new_hashes

        return transaction_hashes[0]
