import time
from typing import Dict, Any, List, Optional
from crypto_utils import CryptoUtils


class SmartContract:
    def __init__(self, contract_id: str, creator: str, code: str, state: Dict = None):
        self.contract_id = contract_id
        self.creator = creator
        self.code = code
        self.state = state or {}
        self.created_at = time.time()
        self.transaction_history: List[Dict] = []

    def execute(self, function_name: str, params: Dict, caller: str) -> Dict:
        execution_result = {
            'success': False,
            'result': None,
            'error': None,
            'gas_used': 0
        }

        try:
            if function_name == 'transfer':
                result = self._handle_transfer(params, caller)
                execution_result['success'] = result
                execution_result['result'] = result
                execution_result['gas_used'] = 21000

            elif function_name == 'mint':
                result = self._handle_mint(params, caller)
                execution_result['success'] = result
                execution_result['result'] = result
                execution_result['gas_used'] = 50000

            elif function_name == 'burn':
                result = self._handle_burn(params, caller)
                execution_result['success'] = result
                execution_result['result'] = result
                execution_result['gas_used'] = 30000

            elif function_name == 'set_value':
                key = params.get('key')
                value = params.get('value')
                self.state[key] = value
                execution_result['success'] = True
                execution_result['result'] = f"Set {key} = {value}"
                execution_result['gas_used'] = 20000

            elif function_name == 'get_value':
                key = params.get('key')
                value = self.state.get(key)
                execution_result['success'] = True
                execution_result['result'] = value
                execution_result['gas_used'] = 5000

            else:
                execution_result['error'] = f"Unknown function: {function_name}"

            self.transaction_history.append({
                'function': function_name,
                'params': params,
                'caller': caller,
                'timestamp': time.time(),
                'result': execution_result
            })

        except Exception as e:
            execution_result['error'] = str(e)

        return execution_result

    def _handle_transfer(self, params: Dict, caller: str) -> bool:
        to_address = params.get('to')
        amount = params.get('amount', 0)

        if not to_address or amount <= 0:
            return False

        caller_balance = self.state.get(f'balance_{caller}', 0)
        if caller_balance < amount:
            return False

        self.state[f'balance_{caller}'] = caller_balance - amount
        self.state[f'balance_{to_address}'] = self.state.get(f'balance_{to_address}', 0) + amount
        return True

    def _handle_mint(self, params: Dict, caller: str) -> bool:
        if caller != self.creator:
            return False

        to_address = params.get('to')
        amount = params.get('amount', 0)

        if not to_address or amount <= 0:
            return False

        self.state[f'balance_{to_address}'] = self.state.get(f'balance_{to_address}', 0) + amount
        self.state['total_supply'] = self.state.get('total_supply', 0) + amount
        return True

    def _handle_burn(self, params: Dict, caller: str) -> bool:
        amount = params.get('amount', 0)

        if amount <= 0:
            return False

        caller_balance = self.state.get(f'balance_{caller}', 0)
        if caller_balance < amount:
            return False

        self.state[f'balance_{caller}'] = caller_balance - amount
        self.state['total_supply'] = self.state.get('total_supply', 0) - amount
        return True

    def get_balance(self, address: str) -> float:
        return self.state.get(f'balance_{address}', 0)

    def to_dict(self) -> Dict:
        return {
            'contract_id': self.contract_id,
            'creator': self.creator,
            'code': self.code,
            'state': self.state,
            'created_at': self.created_at,
            'transaction_count': len(self.transaction_history)
        }


class ContractManager:
    def __init__(self):
        self.contracts: Dict[str, SmartContract] = {}

    def deploy_contract(self, creator: str, code: str, initial_state: Dict = None) -> str:
        contract_id = CryptoUtils.hash_data({
            'creator': creator,
            'code': code,
            'timestamp': time.time()
        })

        contract = SmartContract(contract_id, creator, code, initial_state)
        self.contracts[contract_id] = contract
        return contract_id

    def execute_contract(self, contract_id: str, function_name: str, params: Dict, caller: str) -> Dict:
        contract = self.contracts.get(contract_id)
        if not contract:
            return {'success': False, 'error': 'Contract not found'}

        return contract.execute(function_name, params, caller)

    def get_contract(self, contract_id: str) -> Optional[SmartContract]:
        return self.contracts.get(contract_id)

    def get_all_contracts(self) -> List[Dict]:
        return [contract.to_dict() for contract in self.contracts.values()]
