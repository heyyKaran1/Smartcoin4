from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from advanced_blockchain import AdvancedBlockchain
from advanced_wallet import AdvancedWallet
from database import Database
from erc20_token import TokenManager
from smart_contract import ContractManager
from staking import StakingPool
import threading
import os

app = Flask(__name__, static_folder='frontend')
CORS(app)

blockchain = AdvancedBlockchain(difficulty=2, block_reward=50.0)
database = Database("blockchain.db")
token_manager = TokenManager()
contract_manager = ContractManager()
staking_pool = StakingPool(apy=10.0)  # 10% APY
wallets = {}

# Initialize SmartCoin Token
CCI_TOKEN = None
CCI_PRICE_INR = 10  # 1 CCI = ₹10
CCI_PRICE_USD = 0.12  # 1 CCI = $0.12
CCI_CONTRACT_ADDRESS = "0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb"
NETWORK = "Ethereum Mainnet"

def initialize_cci():
    global CCI_TOKEN
    if not CCI_TOKEN:
        CCI_TOKEN = token_manager.create_token(
            name="CCI Coin",
            symbol="CCI",
            total_supply=1000000000,  # 1 billion
            creator_address="GENESIS"
        )
    return CCI_TOKEN

initialize_cci()

# Tokenomics Distribution
TOKENOMICS = {
    "Public Sale": 30,
    "Ecosystem Development": 20,
    "Team & Advisors": 15,
    "Marketing & Partnerships": 10,
    "Staking Rewards": 15,
    "Reserve Fund": 10
}


@app.route('/')
def index():
    return send_from_directory('frontend', 'index.html')


@app.route('/<path:path>')
def serve_static(path):
    return send_from_directory('frontend', path)


@app.route('/api/blockchain/info', methods=['GET'])
def get_blockchain_info():
    info = blockchain.get_chain_info()
    mining_stats = blockchain.get_mining_stats()
    return jsonify({
        **info,
        **mining_stats
    })


@app.route('/api/blocks', methods=['GET'])
def get_blocks():
    limit = request.args.get('limit', default=10, type=int)
    blocks = blockchain.chain[-limit:]
    return jsonify([block.to_dict() for block in blocks])


@app.route('/api/block/<int:index>', methods=['GET'])
def get_block_by_index(index):
    block = blockchain.get_block_by_index(index)
    if block:
        return jsonify(block.to_dict())
    return jsonify({'error': 'Block not found'}), 404


@app.route('/api/block/hash/<block_hash>', methods=['GET'])
def get_block_by_hash(block_hash):
    block = blockchain.get_block_by_hash(block_hash)
    if block:
        return jsonify(block.to_dict())
    return jsonify({'error': 'Block not found'}), 404


@app.route('/api/transaction/<tx_id>', methods=['GET'])
def get_transaction(tx_id):
    transaction = blockchain.get_transaction_by_id(tx_id)
    if transaction:
        return jsonify(transaction.to_dict())
    return jsonify({'error': 'Transaction not found'}), 404


@app.route('/api/wallet/create', methods=['POST'])
def create_wallet():
    wallet = AdvancedWallet()
    wallet_id = len(wallets)
    wallets[wallet_id] = wallet
    return jsonify({
        'wallet_id': wallet_id,
        'address': wallet.get_address(),
        'balance': blockchain.get_balance(wallet.get_address())
    })


@app.route('/api/wallet/<int:wallet_id>', methods=['GET'])
def get_wallet(wallet_id):
    if wallet_id not in wallets:
        return jsonify({'error': 'Wallet not found'}), 404

    wallet = wallets[wallet_id]
    return jsonify({
        'wallet_id': wallet_id,
        'address': wallet.get_address(),
        'balance': blockchain.get_balance(wallet.get_address())
    })


@app.route('/api/balance/<address>', methods=['GET'])
def get_balance(address):
    balance = blockchain.get_balance(address)
    utxos = blockchain.get_utxos_for_address(address)
    return jsonify({
        'address': address,
        'balance': balance,
        'utxo_count': len(utxos)
    })


@app.route('/api/transaction/create', methods=['POST'])
def create_transaction():
    data = request.json
    wallet_id = data.get('wallet_id')
    to_address = data.get('to_address')
    amount = data.get('amount')
    fee = data.get('fee', 0.1)

    merchant_name = data.get('merchant_name', '')
    merchant_id = data.get('merchant_id', '')
    purpose = data.get('purpose', '')
    reference_id = data.get('reference_id', '')

    if wallet_id not in wallets:
        return jsonify({'error': 'Wallet not found'}), 404

    wallet = wallets[wallet_id]
    transaction = wallet.create_transaction(to_address, amount, fee, blockchain)

    if not transaction:
        return jsonify({'error': 'Failed to create transaction'}), 400

    transaction.merchant_details = {
        'merchant_name': merchant_name,
        'merchant_id': merchant_id,
        'purpose': purpose,
        'reference_id': reference_id
    }

    if blockchain.add_transaction(transaction):
        return jsonify({
            'success': True,
            'tx_id': transaction.tx_id,
            'merchant_name': merchant_name,
            'merchant_id': merchant_id,
            'purpose': purpose,
            'reference_id': reference_id,
            'amount': amount,
            'message': 'Transaction added to mempool'
        })

    return jsonify({'error': 'Failed to add transaction to mempool'}), 400


@app.route('/api/mine', methods=['POST'])
def mine_block():
    data = request.json
    miner_address = data.get('miner_address')

    if not miner_address:
        return jsonify({'error': 'Miner address required'}), 400

    block = blockchain.mine_block(miner_address, force=True)

    if block:
        database.save_block(block)

        for tx in block.transactions:
            for i, output in enumerate(tx.outputs):
                utxo_key = f"{tx.tx_id}:{i}"
                database.save_utxo(utxo_key, output.address, output.amount, tx.tx_id, i)

        for tx in block.transactions:
            for tx_input in tx.inputs:
                utxo_key = f"{tx_input.tx_id}:{tx_input.output_index}"
                database.delete_utxo(utxo_key)

        return jsonify({
            'success': True,
            'block': block.to_dict(),
            'message': f'Block {block.index} mined successfully'
        })

    return jsonify({'error': 'No transactions to mine'}), 400


@app.route('/api/mempool', methods=['GET'])
def get_mempool():
    transactions = blockchain.mempool.get_all_transactions()
    return jsonify({
        'size': len(transactions),
        'transactions': [tx.to_dict() for tx in transactions]
    })


@app.route('/api/utxos/<address>', methods=['GET'])
def get_utxos(address):
    utxos = blockchain.get_utxos_for_address(address)
    return jsonify({
        'address': address,
        'utxos': [{'tx_id': tx_id, 'output_index': idx, 'amount': amount}
                  for tx_id, idx, amount in utxos]
    })


@app.route('/api/validate', methods=['GET'])
def validate_chain():
    is_valid = blockchain.is_chain_valid()
    return jsonify({
        'valid': is_valid,
        'message': 'Blockchain is valid' if is_valid else 'Blockchain is invalid'
    })


@app.route('/api/stats', methods=['GET'])
def get_stats():
    total_supply = sum(utxo.amount for utxo in blockchain.utxo_set.values())
    unique_addresses = len(set(utxo.address for utxo in blockchain.utxo_set.values()))

    return jsonify({
        'total_supply': total_supply,
        'unique_addresses': unique_addresses,
        'total_transactions': sum(len(block.transactions) for block in blockchain.chain),
        'blocks_mined': len(blockchain.chain),
        'difficulty': blockchain.difficulty,
        'block_reward': blockchain.block_reward
    })


@app.route('/api/blockchain/history', methods=['GET'])
def get_blockchain_history():
    blocks = blockchain.chain[-20:] if len(blockchain.chain) > 20 else blockchain.chain
    history = []
    for block in blocks:
        history.append({
            'index': block.index,
            'transaction_count': len(block.transactions),
            'timestamp': block.timestamp,
            'difficulty': blockchain.difficulty
        })
    return jsonify({'history': history})


# ===== SmartCoin Token Endpoints =====

@app.route('/api/cci/info', methods=['GET'])
def get_cci_info():
    token = initialize_cci()
    circulating_supply = sum(token.balances.values()) - token.balance_of("GENESIS")
    market_cap_inr = circulating_supply * CCI_PRICE_INR
    market_cap_usd = circulating_supply * CCI_PRICE_USD

    return jsonify({
        'name': token.name,
        'symbol': token.symbol,
        'total_supply': token.total_supply,
        'circulating_supply': circulating_supply,
        'decimals': token.decimals,
        'price_inr': CCI_PRICE_INR,
        'price_usd': CCI_PRICE_USD,
        'market_cap_inr': market_cap_inr,
        'market_cap_usd': market_cap_usd,
        'contract_address': CCI_CONTRACT_ADDRESS,
        'network': NETWORK,
        'holders': len(token.balances),
        'tokenomics': TOKENOMICS,
        'blockchain_height': len(blockchain.chain),
        'transaction_count': token.transaction_count,
        'paused': token.paused
    })


@app.route('/api/cci/balance/<address>', methods=['GET'])
def get_cci_balance(address):
    token = initialize_cci()
    balance = token.balance_of(address)
    value_inr = balance * CCI_PRICE_INR
    value_usd = balance * CCI_PRICE_USD

    return jsonify({
        'address': address,
        'balance': balance,
        'symbol': 'CCI',
        'value_inr': value_inr,
        'value_usd': value_usd
    })


@app.route('/api/cci/transfer', methods=['POST'])
def transfer_cci():
    data = request.json
    from_address = data.get('from_address')
    to_address = data.get('to_address')
    amount = data.get('amount')

    token = initialize_cci()
    success = token.transfer(from_address, to_address, amount)

    if success:
        return jsonify({
            'success': True,
            'message': f'Transferred {amount} CCI',
            'from': from_address,
            'to': to_address,
            'amount': amount
        })

    return jsonify({'success': False, 'error': 'Transfer failed'}), 400


@app.route('/api/cci/mint', methods=['POST'])
def mint_cci():
    data = request.json
    to_address = data.get('to_address')
    amount = data.get('amount')

    token = initialize_cci()
    success = token.mint(to_address, amount)

    if success:
        return jsonify({
            'success': True,
            'message': f'Minted {amount} CCI to {to_address}',
            'amount': amount
        })

    return jsonify({'success': False, 'error': 'Minting failed'}), 400


@app.route('/api/cci/burn', methods=['POST'])
def burn_cci():
    data = request.json
    from_address = data.get('from_address')
    amount = data.get('amount')

    token = initialize_cci()
    success = token.burn(from_address, amount)

    if success:
        return jsonify({
            'success': True,
            'message': f'Burned {amount} CCI from {from_address}',
            'amount': amount
        })

    return jsonify({'success': False, 'error': 'Burn failed'}), 400


@app.route('/api/cci/history', methods=['GET'])
def get_transaction_history():
    token = initialize_cci()
    limit = request.args.get('limit', default=50, type=int)
    address = request.args.get('address')

    history = token.transaction_history[-limit:]

    if address:
        history = [tx for tx in history if tx['from'] == address or tx['to'] == address]

    return jsonify({
        'count': len(history),
        'transactions': list(reversed(history))
    })


@app.route('/api/cci/activity', methods=['GET'])
def get_live_activity():
    token = initialize_cci()
    limit = request.args.get('limit', default=10, type=int)

    recent = token.transaction_history[-limit:]

    return jsonify({
        'activity': list(reversed(recent))
    })


# ===== Smart Contract Endpoints =====

@app.route('/api/contract/deploy', methods=['POST'])
def deploy_contract():
    data = request.json
    creator = data.get('creator')
    code = data.get('code', 'CCI Coin Contract')
    initial_state = data.get('initial_state', {})

    contract_id = contract_manager.deploy_contract(creator, code, initial_state)

    return jsonify({
        'success': True,
        'contract_id': contract_id,
        'contract_address': CCI_CONTRACT_ADDRESS,
        'network': NETWORK,
        'message': 'Smart contract deployed successfully'
    })


@app.route('/api/contract/<contract_id>/execute', methods=['POST'])
def execute_contract(contract_id):
    data = request.json
    function_name = data.get('function')
    params = data.get('params', {})
    caller = data.get('caller')

    result = contract_manager.execute_contract(contract_id, function_name, params, caller)

    return jsonify(result)


@app.route('/api/contract/<contract_id>', methods=['GET'])
def get_contract(contract_id):
    contract = contract_manager.get_contract(contract_id)

    if contract:
        return jsonify(contract.to_dict())

    return jsonify({'error': 'Contract not found'}), 404


@app.route('/api/contracts', methods=['GET'])
def get_all_contracts():
    contracts = contract_manager.get_all_contracts()
    return jsonify({
        'count': len(contracts),
        'contracts': contracts
    })


# ===== Staking Endpoints =====

@app.route('/api/staking/stake', methods=['POST'])
def stake_tokens():
    data = request.json
    address = data.get('address')
    amount = data.get('amount')

    token = initialize_cci()
    balance = token.balance_of(address)

    if balance < amount:
        return jsonify({'success': False, 'error': 'Insufficient balance'}), 400

    # Transfer from user to staking pool
    success = token.transfer(address, 'STAKING_POOL', amount)
    if success:
        staking_pool.stake(address, amount)
        return jsonify({
            'success': True,
            'message': f'Staked {amount} CCI',
            'staked_amount': amount
        })

    return jsonify({'success': False, 'error': 'Staking failed'}), 400


@app.route('/api/staking/unstake', methods=['POST'])
def unstake_tokens():
    data = request.json
    address = data.get('address')
    amount = data.get('amount')

    success = staking_pool.unstake(address, amount)
    if success:
        token = initialize_cci()
        token.transfer('STAKING_POOL', address, amount)
        return jsonify({
            'success': True,
            'message': f'Unstaked {amount} CCI',
            'unstaked_amount': amount
        })

    return jsonify({'success': False, 'error': 'Unstaking failed'}), 400


@app.route('/api/staking/claim', methods=['POST'])
def claim_rewards():
    data = request.json
    address = data.get('address')

    rewards = staking_pool.claim_rewards(address)
    if rewards > 0:
        token = initialize_cci()
        token.mint(address, rewards)
        return jsonify({
            'success': True,
            'message': f'Claimed {rewards:.2f} CCI rewards',
            'rewards': rewards
        })

    return jsonify({'success': False, 'error': 'No rewards to claim'}), 400


@app.route('/api/staking/info/<address>', methods=['GET'])
def get_staking_info(address):
    info = staking_pool.get_stake_info(address)
    return jsonify(info)


@app.route('/api/staking/pool', methods=['GET'])
def get_pool_stats():
    stats = staking_pool.get_pool_stats()
    return jsonify(stats)


def run_api(host='0.0.0.0', port=5000, debug=False):
    app.run(host=host, port=port, debug=debug, threaded=True)


if __name__ == '__main__':
    print("Starting CCI Coin Enterprise Platform API Server...")
    print("API running at http://localhost:5000")
    print("\n🪙  CCI Coin Token Initialized")
    print(f"   Contract: {CCI_CONTRACT_ADDRESS}")
    print(f"   Network: {NETWORK}")
    print(f"   Price: ₹{CCI_PRICE_INR} | ${CCI_PRICE_USD}")
    print(f"   Total Supply: 1,000,000,000 CCI")
    print("\nAvailable endpoints:")
    print("  GET  /api/blockchain/info")
    print("  GET  /api/cci/info")
    print("  GET  /api/cci/balance/<address>")
    print("  POST /api/cci/transfer")
    print("  POST /api/cci/mint")
    print("  POST /api/contract/deploy")
    print("  GET  /api/contracts")
    run_api(debug=True)
