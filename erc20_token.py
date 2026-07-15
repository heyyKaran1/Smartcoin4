import time
from typing import Dict, List, Optional
from crypto_utils import CryptoUtils


class Token:
    def __init__(self, name: str, symbol: str, total_supply: float, decimals: int = 18):
        self.name = name
        self.symbol = symbol
        self.total_supply = total_supply
        self.decimals = decimals
        self.balances: Dict[str, float] = {}
        self.allowances: Dict[str, Dict[str, float]] = {}
        self.paused = False
        self.max_wallet = total_supply
        self.max_transaction = total_supply
        self.transaction_count = 0
        self.transaction_history: List[Dict] = []
        self.token_id = CryptoUtils.hash_data({
            'name': name,
            'symbol': symbol,
            'total_supply': total_supply,
            'timestamp': time.time()
        })

    def mint(self, to_address: str, amount: float) -> bool:
        if amount <= 0:
            return False

        self.balances[to_address] = self.balances.get(to_address, 0) + amount
        self.transaction_history.append({
            'type': 'mint',
            'from': 'GENESIS',
            'to': to_address,
            'amount': amount,
            'timestamp': time.time()
        })
        return True

    def burn(self, from_address: str, amount: float) -> bool:
        if amount <= 0:
            return False

        from_balance = self.balances.get(from_address, 0)
        if from_balance < amount:
            return False

        self.balances[from_address] = from_balance - amount
        self.total_supply -= amount
        self.transaction_history.append({
            'type': 'burn',
            'from': from_address,
            'to': 'BURN',
            'amount': amount,
            'timestamp': time.time()
        })
        return True

    def transfer(self, from_address: str, to_address: str, amount: float) -> bool:
        if self.paused or amount <= 0 or amount > self.max_transaction:
            return False

        from_balance = self.balances.get(from_address, 0)
        if from_balance < amount:
            return False

        new_balance = self.balances.get(to_address, 0) + amount
        if new_balance > self.max_wallet:
            return False

        self.balances[from_address] = from_balance - amount
        self.balances[to_address] = new_balance
        self.transaction_count += 1
        self.transaction_history.append({
            'type': 'transfer',
            'from': from_address,
            'to': to_address,
            'amount': amount,
            'timestamp': time.time()
        })
        return True

    def pause(self):
        self.paused = True

    def unpause(self):
        self.paused = False

    def set_max_wallet(self, max_amount: float):
        self.max_wallet = max_amount

    def set_max_transaction(self, max_amount: float):
        self.max_transaction = max_amount

    def approve(self, owner: str, spender: str, amount: float) -> bool:
        if owner not in self.allowances:
            self.allowances[owner] = {}
        self.allowances[owner][spender] = amount
        return True

    def transfer_from(self, spender: str, from_address: str, to_address: str, amount: float) -> bool:
        if from_address not in self.allowances or spender not in self.allowances[from_address]:
            return False

        allowed = self.allowances[from_address][spender]
        if allowed < amount:
            return False

        from_balance = self.balances.get(from_address, 0)
        if from_balance < amount:
            return False

        self.balances[from_address] = from_balance - amount
        self.balances[to_address] = self.balances.get(to_address, 0) + amount
        self.allowances[from_address][spender] = allowed - amount
        return True

    def balance_of(self, address: str) -> float:
        return self.balances.get(address, 0)

    def allowance(self, owner: str, spender: str) -> float:
        if owner not in self.allowances:
            return 0
        return self.allowances[owner].get(spender, 0)

    def to_dict(self) -> Dict:
        return {
            'token_id': self.token_id,
            'name': self.name,
            'symbol': self.symbol,
            'total_supply': self.total_supply,
            'decimals': self.decimals,
            'holders': len(self.balances)
        }


class TokenManager:
    def __init__(self):
        self.tokens: Dict[str, Token] = {}

    def create_token(self, name: str, symbol: str, total_supply: float, creator_address: str) -> Token:
        token = Token(name, symbol, total_supply)
        token.mint(creator_address, total_supply)
        self.tokens[token.token_id] = token
        return token

    def get_token(self, token_id: str) -> Optional[Token]:
        return self.tokens.get(token_id)

    def get_all_tokens(self) -> List[Token]:
        return list(self.tokens.values())

    def get_tokens_by_holder(self, address: str) -> List[Dict]:
        holder_tokens = []
        for token in self.tokens.values():
            balance = token.balance_of(address)
            if balance > 0:
                holder_tokens.append({
                    'token_id': token.token_id,
                    'name': token.name,
                    'symbol': token.symbol,
                    'balance': balance
                })
        return holder_tokens
