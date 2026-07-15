from advanced_blockchain import AdvancedBlockchain
from advanced_wallet import AdvancedWallet
from database import Database
import sys

def view_blockchain_status():
    print("\n" + "="*70)
    print("🪙  YOUR CRYPTOCURRENCY - LIVE STATUS")
    print("="*70)

    blockchain = AdvancedBlockchain(difficulty=2, block_reward=50.0)

    info = blockchain.get_chain_info()

    print(f"\n📊 BLOCKCHAIN INFO:")
    print(f"   Total Blocks: {info['length']}")
    print(f"   Mining Difficulty: {info['difficulty']}")
    print(f"   Block Reward: {info['block_reward']} coins")
    print(f"   Pending Transactions: {info['mempool_size']}")
    print(f"   Total UTXOs: {info['utxo_count']}")
    print(f"   Chain Valid: {'✅ YES' if info['is_valid'] else '❌ NO'}")

    total_supply = sum(utxo.amount for utxo in blockchain.utxo_set.values())
    print(f"\n💰 TOTAL COIN SUPPLY: {total_supply} coins")

    addresses = {}
    for utxo_key, utxo in blockchain.utxo_set.items():
        addresses[utxo.address] = addresses.get(utxo.address, 0) + utxo.amount

    print(f"\n👛 WALLETS WITH COINS: {len(addresses)}")
    for i, (addr, balance) in enumerate(sorted(addresses.items(), key=lambda x: x[1], reverse=True), 1):
        utxo_count = sum(1 for k, v in blockchain.utxo_set.items() if v.address == addr)
        print(f"   {i}. {addr[:40]}... = {balance} coins ({utxo_count} UTXOs)")

    print(f"\n⛓️  RECENT BLOCKS:")
    for block in blockchain.chain[-5:]:
        print(f"   Block #{block.index:3d} | Hash: {block.hash[:40]}...")
        print(f"            | Txs: {len(block.transactions)} | Nonce: {block.nonce}")

    print(f"\n📈 RECENT TRANSACTIONS:")
    tx_count = 0
    for block in reversed(blockchain.chain[-3:]):
        for tx in block.transactions:
            tx_count += 1
            if tx.inputs:
                print(f"   TX: {tx.tx_id[:32]}...")
                print(f"       Inputs: {len(tx.inputs)} | Outputs: {len(tx.outputs)}")
            else:
                print(f"   COINBASE: {tx.tx_id[:32]}... (Mining Reward)")
            if tx_count >= 5:
                break
        if tx_count >= 5:
            break

    print("\n" + "="*70)
    print("✨ Your cryptocurrency is running successfully!")
    print("="*70 + "\n")

def create_new_wallet():
    print("\n🔑 Creating New Wallet...")
    wallet = AdvancedWallet()

    print(f"\n✅ Wallet Created!")
    print(f"   Address: {wallet.get_address()}")
    print(f"   (Keep this private key safe!)")

    wallet.export_to_file(f"wallet_{wallet.get_address()[:8]}.json")
    print(f"\n💾 Wallet saved to: wallet_{wallet.get_address()[:8]}.json")

    return wallet

def check_balance(address):
    blockchain = AdvancedBlockchain(difficulty=2, block_reward=50.0)
    balance = blockchain.get_balance(address)
    utxos = blockchain.get_utxos_for_address(address)

    print(f"\n💰 Balance for {address[:40]}...")
    print(f"   Total: {balance} coins")
    print(f"   UTXOs: {len(utxos)}")

    if utxos:
        print(f"\n   UTXO Details:")
        for tx_id, idx, amount in utxos:
            print(f"      • {tx_id[:32]}...:{idx} = {amount} coins")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        if sys.argv[1] == "balance" and len(sys.argv) > 2:
            check_balance(sys.argv[2])
        elif sys.argv[1] == "newwallet":
            create_new_wallet()
        else:
            print("Usage: python3 view_coin.py [balance <address> | newwallet]")
    else:
        view_blockchain_status()
