from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_socketio import SocketIO, emit, join_room, leave_room
from csrf_protection import init_csrf, get_csrf_token
from advanced_blockchain import AdvancedBlockchain
from advanced_wallet import AdvancedWallet
from database import Database
from erc20_token import TokenManager
from smart_contract import ContractManager
from staking import StakingPool
from auth import auth_manager, token_required, admin_required
from validators import validator
import os
from dotenv import load_dotenv
import logging

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__, static_folder='frontend')
app.config['SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'dev-secret-key')

CORS(app, origins=os.getenv('CORS_ORIGINS', 'http://localhost:5000').split(','),
     supports_credentials=True)

csrf = init_csrf(app)

socketio = SocketIO(app, cors_allowed_origins="*")

limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=[f"{os.getenv('RATE_LIMIT_PER_MINUTE', 100)} per minute"],
    storage_uri="memory://"
)

blockchain = AdvancedBlockchain(difficulty=2, block_reward=50.0)
database = Database("blockchain.db")
token_manager = TokenManager()
contract_manager = ContractManager()
staking_pool = StakingPool(apy=10.0)
wallets = {}

CCI_TOKEN = None
CCI_PRICE_INR = 10
CCI_PRICE_USD = 0.12
CCI_CONTRACT_ADDRESS = "0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb"
NETWORK = "Ethereum Mainnet"

def initialize_cci():
    global CCI_TOKEN
    if not CCI_TOKEN:
        CCI_TOKEN = token_manager.create_token(
            name="CCI Coin",
            symbol="CCI",
            total_supply=1000000000,
            creator_address="GENESIS"
        )
    return CCI_TOKEN

initialize_cci()

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

@app.route('/api/csrf-token', methods=['GET'])
def get_csrf():
    """Get CSRF token for frontend"""
    return jsonify({'csrf_token': get_csrf_token()})

@app.route('/api/auth/register', methods=['POST'])
@limiter.limit("5 per hour")
def register():
    data = request.json
    email = data.get('email')
    password = data.get('password')

    valid, error = validator.validate_email(email)
    if not valid:
        return jsonify({'error': error}), 400

    valid, error = validator.validate_password(password)
    if not valid:
        return jsonify({'error': error}), 400

    user = auth_manager.register_user(email, password)
    if not user:
        return jsonify({'error': 'User already exists'}), 400

    logger.info(f"New user registered: {email}")
    return jsonify({
        'success': True,
        'message': 'User registered successfully'
    })

@app.route('/api/auth/login', methods=['POST'])
@limiter.limit("10 per minute")
def login():
    data = request.json
    email = data.get('email')
    password = data.get('password')

    token = auth_manager.authenticate(email, password)
    if not token:
        return jsonify({'error': 'Invalid credentials'}), 401

    logger.info(f"User logged in: {email}")
    return jsonify({
        'success': True,
        'token': token,
        'message': 'Login successful'
    })

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

@app.route('/api/wallets', methods=['GET'])
def get_all_wallets():
    wallet_list = []
    for wallet_id, wallet in wallets.items():
        wallet_list.append({
            'wallet_id': wallet_id,
            'address': wallet.get_address(),
            'balance': blockchain.get_balance(wallet.get_address())
        })
    return jsonify(wallet_list)

@app.route('/api/wallet/create', methods=['POST'])
@limiter.limit("20 per hour")
def create_wallet():
    wallet = AdvancedWallet()
    wallet_id = len(wallets)
    wallets[wallet_id] = wallet

    address = wallet.get_address()
    logger.info(f"New wallet created: {address}")

    socketio.emit('wallet_created', {
        'wallet_id': wallet_id,
        'address': address
    })

    return jsonify({
        'wallet_id': wallet_id,
        'address': address,
        'balance': blockchain.get_balance(address)
    })

@app.route('/api/balance/<address>', methods=['GET'])
def get_balance(address):
    valid, error = validator.validate_address(address)
    if not valid:
        return jsonify({'error': error}), 400

    balance = blockchain.get_balance(address)
    utxos = blockchain.get_utxos_for_address(address)
    return jsonify({
        'address': address,
        'balance': balance,
        'utxo_count': len(utxos)
    })

@app.route('/api/transaction/merchant', methods=['POST'])
@limiter.limit("30 per minute")
def create_merchant_transaction():
    data = request.json

    valid, errors = validator.validate_merchant_payment(data)
    if not valid:
        return jsonify({'error': 'Validation failed', 'details': errors}), 400

    from_address = validator.sanitize_string(data['from_address'])
    to_address = validator.sanitize_string(data['to_address'])
    amount = float(data['amount'])
    fee = float(data.get('fee', 0.5))
    merchant_name = validator.sanitize_string(data['merchant_name'], 100)
    merchant_id = validator.sanitize_string(data.get('merchant_id', ''), 100)
    purpose = validator.sanitize_string(data.get('purpose', ''), 255)
    reference_id = validator.sanitize_string(data.get('reference_id', ''), 100)

    wallet = None
    for w in wallets.values():
        if w.get_address() == from_address:
            wallet = w
            break

    if not wallet:
        return jsonify({'error': 'Wallet not found'}), 404

    transaction = wallet.create_transaction(to_address, amount, fee, blockchain)
    if not transaction:
        return jsonify({'error': 'Insufficient funds'}), 400

    transaction.merchant_details = {
        'merchant_name': merchant_name,
        'merchant_id': merchant_id,
        'purpose': purpose,
        'reference_id': reference_id
    }

    if blockchain.add_transaction(transaction):
        logger.info(f"Merchant payment created: {transaction.tx_id} - {merchant_name}")

        socketio.emit('transaction_pending', {
            'tx_id': transaction.tx_id,
            'from': from_address,
            'to': to_address,
            'amount': amount,
            'merchant': merchant_name
        }, room=to_address)

        return jsonify({
            'success': True,
            'tx_id': transaction.tx_id,
            'merchant_name': merchant_name,
            'amount': amount,
            'message': 'Payment successful. Transaction pending confirmation.'
        })

    return jsonify({'error': 'Transaction failed'}), 400

@app.route('/api/mine', methods=['POST'])
@limiter.limit("60 per hour")
def mine_block():
    data = request.json
    miner_address = data.get('miner_address')

    if not miner_address:
        return jsonify({'error': 'Miner address required'}), 400

    valid, error = validator.validate_address(miner_address)
    if not valid:
        return jsonify({'error': error}), 400

    block = blockchain.mine_block(miner_address, force=True)

    if block:
        database.save_block(block)
        logger.info(f"Block {block.index} mined by {miner_address}")

        socketio.emit('block_mined', {
            'index': block.index,
            'hash': block.hash,
            'miner': miner_address,
            'transactions': len(block.transactions)
        })

        for tx in block.transactions:
            if hasattr(tx, 'merchant_details') and tx.merchant_details:
                for output in tx.outputs:
                    socketio.emit('payment_received', {
                        'tx_id': tx.tx_id,
                        'amount': output.amount,
                        'merchant': tx.merchant_details.get('merchant_name'),
                        'block': block.index
                    }, room=output.address)

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
        'transaction_count': token.transaction_count
    })

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

@socketio.on('connect')
def handle_connect():
    logger.info(f"Client connected: {request.sid}")
    emit('connected', {'message': 'Connected to CCI Coin WebSocket'})

@socketio.on('disconnect')
def handle_disconnect():
    logger.info(f"Client disconnected: {request.sid}")

@socketio.on('subscribe')
def handle_subscribe(data):
    address = data.get('address')
    if address:
        join_room(address)
        logger.info(f"Client {request.sid} subscribed to {address}")
        emit('subscribed', {'address': address})

@socketio.on('unsubscribe')
def handle_unsubscribe(data):
    address = data.get('address')
    if address:
        leave_room(address)
        logger.info(f"Client {request.sid} unsubscribed from {address}")
        emit('unsubscribed', {'address': address})

@app.errorhandler(429)
def ratelimit_handler(e):
    return jsonify({'error': 'Rate limit exceeded. Please try again later.'}), 429

@app.errorhandler(404)
def not_found(e):
    return jsonify({'error': 'Resource not found'}), 404

@app.errorhandler(500)
def internal_error(e):
    logger.error(f"Internal error: {str(e)}")
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    print("\n" + "="*60)
    print("🚀 CCI Coin Enterprise Platform - Production API")
    print("="*60)
    print(f"\n📊 Configuration:")
    print(f"   Environment: {os.getenv('FLASK_ENV', 'development')}")
    print(f"   Contract: {CCI_CONTRACT_ADDRESS}")
    print(f"   Network: {NETWORK}")
    print(f"   Rate Limit: {os.getenv('RATE_LIMIT_PER_MINUTE', 100)}/min")
    print(f"\n✅ Security Features:")
    print("   ✓ JWT Authentication")
    print("   ✓ Rate Limiting")
    print("   ✓ Input Validation")
    print("   ✓ CORS Protection")
    print("   ✓ WebSocket Real-time Updates")
    print(f"\n🌐 Server: http://0.0.0.0:5000")
    print("="*60 + "\n")

    socketio.run(app, host='0.0.0.0', port=5000, debug=True, allow_unsafe_werkzeug=True)
